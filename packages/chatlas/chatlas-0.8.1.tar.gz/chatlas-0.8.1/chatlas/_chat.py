from __future__ import annotations

import copy
import inspect
import os
import sys
import traceback
import warnings
from pathlib import Path
from threading import Thread
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Generator,
    Generic,
    Iterator,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from ._callbacks import CallbackManager
from ._content import (
    Content,
    ContentJson,
    ContentText,
    ContentToolRequest,
    ContentToolResult,
)
from ._display import (
    EchoDisplayOptions,
    IPyMarkdownDisplay,
    LiveMarkdownDisplay,
    MarkdownDisplay,
    MockMarkdownDisplay,
)
from ._logging import log_tool_error
from ._provider import Provider
from ._tools import Tool, ToolRejectError
from ._turn import Turn, user_turn
from ._typing_extensions import TypedDict
from ._utils import html_escape, wrap_async


class AnyTypeDict(TypedDict, total=False):
    pass


SubmitInputArgsT = TypeVar("SubmitInputArgsT", bound=AnyTypeDict)
"""
A TypedDict representing the arguments that can be passed to the `.chat()`
method of a [](`~chatlas.Chat`) instance.
"""

CompletionT = TypeVar("CompletionT")

EchoOptions = Literal["output", "all", "none", "text"]


class Chat(Generic[SubmitInputArgsT, CompletionT]):
    """
    A chat object that can be used to interact with a language model.

    A `Chat` is an sequence of sequence of user and assistant
    [](`~chatlas.Turn`)s sent to a specific [](`~chatlas.Provider`). A `Chat`
    takes care of managing the state associated with the chat; i.e. it records
    the messages that you send to the server, and the messages that you receive
    back. If you register a tool (i.e. an function that the assistant can call
    on your behalf), it also takes care of the tool loop.

    You should generally not create this object yourself, but instead call
    [](`~chatlas.ChatOpenAI`) or friends instead.
    """

    def __init__(
        self,
        provider: Provider,
        turns: Optional[Sequence[Turn]] = None,
    ):
        """
        Create a new chat object.

        Parameters
        ----------
        provider
            A [](`~chatlas.Provider`) object.
        turns
            A list of [](`~chatlas.Turn`) objects to initialize the chat with.
        """
        self.provider = provider
        self._turns: list[Turn] = list(turns or [])
        self._tools: dict[str, Tool] = {}
        self._on_tool_request_callbacks = CallbackManager()
        self._on_tool_result_callbacks = CallbackManager()
        self._current_display: Optional[MarkdownDisplay] = None
        self._echo_options: EchoDisplayOptions = {
            "rich_markdown": {},
            "rich_console": {},
            "css_styles": {},
        }

    def get_turns(
        self,
        *,
        include_system_prompt: bool = False,
    ) -> list[Turn[CompletionT]]:
        """
        Get all the turns (i.e., message contents) in the chat.

        Parameters
        ----------
        include_system_prompt
            Whether to include the system prompt in the turns.
        """

        if not self._turns:
            return self._turns

        if not include_system_prompt and self._turns[0].role == "system":
            return self._turns[1:]
        return self._turns

    def get_last_turn(
        self,
        *,
        role: Literal["assistant", "user", "system"] = "assistant",
    ) -> Turn[CompletionT] | None:
        """
        Get the last turn in the chat with a specific role.

        Parameters
        ----------
        role
            The role of the turn to return.
        """
        for turn in reversed(self._turns):
            if turn.role == role:
                return turn
        return None

    def set_turns(self, turns: Sequence[Turn]):
        """
        Set the turns of the chat.

        This method is primarily useful for clearing or setting the turns of the
        chat (i.e., limiting the context window).

        Parameters
        ----------
        turns
            The turns to set. Turns with the role "system" are not allowed.
        """
        if any(x.role == "system" for x in turns):
            idx = next(i for i, x in enumerate(turns) if x.role == "system")
            raise ValueError(
                f"Turn {idx} has a role 'system', which is not allowed. "
                "The system prompt must be set separately using the `.system_prompt` property. "
                "Consider removing this turn and setting the `.system_prompt` separately "
                "if you want to change the system prompt."
            )
        self._turns = list(turns)

    @property
    def system_prompt(self) -> str | None:
        """
        A property to get (or set) the system prompt for the chat.

        Returns
        -------
        str | None
            The system prompt (if any).
        """
        if self._turns and self._turns[0].role == "system":
            return self._turns[0].text
        return None

    @system_prompt.setter
    def system_prompt(self, value: str | None):
        if self._turns and self._turns[0].role == "system":
            self._turns.pop(0)
        if value is not None:
            self._turns.insert(0, Turn("system", value))

    @overload
    def tokens(self) -> list[tuple[int, int] | None]: ...

    @overload
    def tokens(
        self,
        values: Literal["cumulative"],
    ) -> list[tuple[int, int] | None]: ...

    @overload
    def tokens(
        self,
        values: Literal["discrete"],
    ) -> list[int]: ...

    def tokens(
        self,
        values: Literal["cumulative", "discrete"] = "discrete",
    ) -> list[int] | list[tuple[int, int] | None]:
        """
        Get the tokens for each turn in the chat.

        Parameters
        ----------
        values
            If "cumulative" (the default), the result can be summed to get the
            chat's overall token usage (helpful for computing overall cost of
            the chat). If "discrete", the result can be summed to get the number of
            tokens the turns will cost to generate the next response (helpful
            for estimating cost of the next response, or for determining if you
            are about to exceed the token limit).

        Returns
        -------
        list[int]
            A list of token counts for each (non-system) turn in the chat. The
            1st turn includes the tokens count for the system prompt (if any).

        Raises
        ------
        ValueError
            If the chat's turns (i.e., `.get_turns()`) are not in an expected
            format. This may happen if the chat history is manually set (i.e.,
            `.set_turns()`). In this case, you can inspect the "raw" token
            values via the `.get_turns()` method (each turn has a `.tokens`
            attribute).
        """

        turns = self.get_turns(include_system_prompt=False)

        if values == "cumulative":
            return [turn.tokens for turn in turns]

        if len(turns) == 0:
            return []

        err_info = (
            "This can happen if the chat history is manually set (i.e., `.set_turns()`). "
            "Consider getting the 'raw' token values via the `.get_turns()` method "
            "(each turn has a `.tokens` attribute)."
        )

        # Sanity checks for the assumptions made to figure out user token counts
        if len(turns) == 1:
            raise ValueError(
                "Expected at least two turns in the chat history. " + err_info
            )

        if len(turns) % 2 != 0:
            raise ValueError(
                "Expected an even number of turns in the chat history. " + err_info
            )

        if turns[0].role != "user":
            raise ValueError(
                "Expected the 1st non-system turn to have role='user'. " + err_info
            )

        if turns[1].role != "assistant":
            raise ValueError(
                "Expected the 2nd turn non-system to have role='assistant'. " + err_info
            )

        if turns[1].tokens is None:
            raise ValueError(
                "Expected the 1st assistant turn to contain token counts. " + err_info
            )

        res: list[int] = [
            # Implied token count for the 1st user input
            turns[1].tokens[0],
            # The token count for the 1st assistant response
            turns[1].tokens[1],
        ]
        for i in range(1, len(turns) - 1, 2):
            ti = turns[i]
            tj = turns[i + 2]
            if ti.role != "assistant" or tj.role != "assistant":
                raise ValueError(
                    "Expected even turns to have role='assistant'." + err_info
                )
            if ti.tokens is None or tj.tokens is None:
                raise ValueError(
                    "Expected role='assistant' turns to contain token counts."
                    + err_info
                )
            res.extend(
                [
                    # Implied token count for the user input
                    tj.tokens[0] - sum(ti.tokens),
                    # The token count for the assistant response
                    tj.tokens[1],
                ]
            )

        return res

    def token_count(
        self,
        *args: Content | str,
        data_model: Optional[type[BaseModel]] = None,
    ) -> int:
        """
        Get an estimated token count for the given input.

        Estimate the token size of input content. This can help determine whether input(s)
        and/or conversation history (i.e., `.get_turns()`) should be reduced in size before
        sending it to the model.

        Parameters
        ----------
        args
            The input to get a token count for.
        data_model
            If the input is meant for data extraction (i.e., `.extract_data()`), then
            this should be the Pydantic model that describes the structure of the data to
            extract.

        Returns
        -------
        int
            The token count for the input.

        Note
        ----
        Remember that the token count is an estimate. Also, models based on
        `ChatOpenAI()` currently does not take tools into account when
        estimating token counts.

        Examples
        --------
        ```python
        from chatlas import ChatAnthropic

        chat = ChatAnthropic()
        # Estimate the token count before sending the input
        print(chat.token_count("What is 2 + 2?"))

        # Once input is sent, you can get the actual input and output
        # token counts from the chat object
        chat.chat("What is 2 + 2?", echo="none")
        print(chat.token_usage())
        ```
        """

        return self.provider.token_count(
            *args,
            tools=self._tools,
            data_model=data_model,
        )

    async def token_count_async(
        self,
        *args: Content | str,
        data_model: Optional[type[BaseModel]] = None,
    ) -> int:
        """
        Get an estimated token count for the given input asynchronously.

        Estimate the token size of input content. This can help determine whether input(s)
        and/or conversation history (i.e., `.get_turns()`) should be reduced in size before
        sending it to the model.

        Parameters
        ----------
        args
            The input to get a token count for.
        data_model
            If this input is meant for data extraction (i.e., `.extract_data_async()`),
            then this should be the Pydantic model that describes the structure of the data
            to extract.

        Returns
        -------
        int
            The token count for the input.
        """

        return await self.provider.token_count_async(
            *args,
            tools=self._tools,
            data_model=data_model,
        )

    def app(
        self,
        *,
        stream: bool = True,
        port: int = 0,
        launch_browser: bool = True,
        bg_thread: Optional[bool] = None,
        echo: Optional[EchoOptions] = None,
        content: Literal["text", "all"] = "all",
        kwargs: Optional[SubmitInputArgsT] = None,
    ):
        """
        Enter a web-based chat app to interact with the LLM.

        Parameters
        ----------
        stream
            Whether to stream the response (i.e., have the response appear in chunks).
        port
            The port to run the app on (the default is 0, which will choose a random port).
        launch_browser
            Whether to launch a browser window.
        bg_thread
            Whether to run the app in a background thread. If `None`, the app will
            run in a background thread if the current environment is a notebook.
        echo
            One of the following (defaults to `"none"` when `stream=True` and `"text"` when
            `stream=False`):
              - `"text"`: Echo just the text content of the response.
              - `"output"`: Echo text and tool call content.
              - `"all"`: Echo both the assistant and user turn.
              - `"none"`: Do not echo any content.
        content
            Whether to display text content or all content (i.e., tool calls).
        kwargs
            Additional keyword arguments to pass to the method used for requesting
            the response.
        """

        try:
            from shiny import App, run_app, ui
        except ImportError:
            raise ImportError(
                "The `shiny` package is required for the `browser` method. "
                "Install it with `pip install shiny`."
            )

        app_ui = ui.page_fillable(
            ui.chat_ui("chat"),
            fillable_mobile=True,
        )

        def server(input):  # noqa: A002
            chat = ui.Chat(
                "chat",
                messages=[
                    {"role": turn.role, "content": turn.text}
                    for turn in self.get_turns()
                ],
            )

            @chat.on_user_submit
            async def _(user_input: str):
                if stream:
                    await chat.append_message_stream(
                        await self.stream_async(
                            user_input,
                            kwargs=kwargs,
                            echo=echo or "none",
                            content=content,
                        )
                    )
                else:
                    await chat.append_message(
                        str(
                            self.chat(
                                user_input,
                                kwargs=kwargs,
                                stream=False,
                                echo=echo or "text",
                            )
                        )
                    )

        app = App(app_ui, server)

        def _run_app():
            run_app(app, launch_browser=launch_browser, port=port)

        # Use bg_thread by default in Jupyter and Positron
        if bg_thread is None:
            from rich.console import Console

            console = Console()
            bg_thread = console.is_jupyter or (os.getenv("POSITRON") == "1")

        if bg_thread:
            thread = Thread(target=_run_app, daemon=True)
            thread.start()
        else:
            _run_app()

        return None

    def console(
        self,
        *,
        echo: EchoOptions = "output",
        stream: bool = True,
        kwargs: Optional[SubmitInputArgsT] = None,
    ):
        """
        Enter a chat console to interact with the LLM.

        To quit, input 'exit' or press Ctrl+C.

        Parameters
        ----------
        echo
            One of the following (default is "output"):
              - `"text"`: Echo just the text content of the response.
              - `"output"`: Echo text and tool call content.
              - `"all"`: Echo both the assistant and user turn.
              - `"none"`: Do not echo any content.
        stream
            Whether to stream the response (i.e., have the response appear in chunks).
        kwargs
            Additional keyword arguments to pass to the method used for requesting
            the response

        Returns
        -------
        None
        """

        print("\nEntering chat console. To quit, input 'exit' or press Ctrl+C.\n")

        while True:
            user_input = input("?> ")
            if user_input.strip().lower() in ("exit", "exit()"):
                break
            print("")
            self.chat(user_input, echo=echo, stream=stream, kwargs=kwargs)
            print("")

    def chat(
        self,
        *args: Content | str,
        echo: EchoOptions = "output",
        stream: bool = True,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> ChatResponse:
        """
        Generate a response from the chat.

        Parameters
        ----------
        args
            The user input(s) to generate a response from.
        echo
            One of the following (default is "output"):
              - `"text"`: Echo just the text content of the response.
              - `"output"`: Echo text and tool call content.
              - `"all"`: Echo both the assistant and user turn.
              - `"none"`: Do not echo any content.
        stream
            Whether to stream the response (i.e., have the response appear in
            chunks).
        kwargs
            Additional keyword arguments to pass to the method used for
            requesting the response.

        Returns
        -------
        ChatResponse
            A (consumed) response from the chat. Apply `str()` to this object to
            get the text content of the response.
        """
        turn = user_turn(*args)

        display = self._markdown_display(echo=echo)

        response = ChatResponse(
            self._chat_impl(
                turn,
                echo=echo,
                content="text",
                stream=stream,
                kwargs=kwargs,
            )
        )

        with display:
            for _ in response:
                pass

        return response

    async def chat_async(
        self,
        *args: Content | str,
        echo: EchoOptions = "output",
        stream: bool = True,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> ChatResponseAsync:
        """
        Generate a response from the chat asynchronously.

        Parameters
        ----------
        args
            The user input(s) to generate a response from.
        echo
            One of the following (default is "output"):
              - `"text"`: Echo just the text content of the response.
              - `"output"`: Echo text and tool call content.
              - `"all"`: Echo both the assistant and user turn.
              - `"none"`: Do not echo any content.
        stream
            Whether to stream the response (i.e., have the response appear in
            chunks).
        kwargs
            Additional keyword arguments to pass to the method used for
            requesting the response.

        Returns
        -------
        ChatResponseAsync
            A (consumed) response from the chat. Apply `str()` to this object to
            get the text content of the response.
        """
        turn = user_turn(*args)

        display = self._markdown_display(echo=echo)

        response = ChatResponseAsync(
            self._chat_impl_async(
                turn,
                echo=echo,
                content="text",
                stream=stream,
                kwargs=kwargs,
            ),
        )

        with display:
            async for _ in response:
                pass

        return response

    @overload
    def stream(
        self,
        *args: Content | str,
        content: Literal["text"] = "text",
        echo: EchoOptions = "none",
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> Generator[str, None, None]: ...

    @overload
    def stream(
        self,
        *args: Content | str,
        content: Literal["all"],
        echo: EchoOptions = "none",
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> Generator[str | ContentToolRequest | ContentToolResult, None, None]: ...

    def stream(
        self,
        *args: Content | str,
        content: Literal["text", "all"] = "text",
        echo: EchoOptions = "none",
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> Generator[str | ContentToolRequest | ContentToolResult, None, None]:
        """
        Generate a response from the chat in a streaming fashion.

        Parameters
        ----------
        args
            The user input(s) to generate a response from.
        content
            Whether to yield just text content or include rich content objects
            (e.g., tool calls) when relevant.
        echo
            One of the following (default is "none"):
              - `"text"`: Echo just the text content of the response.
              - `"output"`: Echo text and tool call content.
              - `"all"`: Echo both the assistant and user turn.
              - `"none"`: Do not echo any content.
        kwargs
            Additional keyword arguments to pass to the method used for requesting
            the response.

        Returns
        -------
        ChatResponse
            An (unconsumed) response from the chat. Iterate over this object to
            consume the response.
        """
        turn = user_turn(*args)

        display = self._markdown_display(echo=echo)

        generator = self._chat_impl(
            turn,
            stream=True,
            echo=echo,
            content=content,
            kwargs=kwargs,
        )

        def wrapper() -> Generator[
            str | ContentToolRequest | ContentToolResult, None, None
        ]:
            with display:
                for chunk in generator:
                    yield chunk

        return wrapper()

    @overload
    async def stream_async(
        self,
        *args: Content | str,
        content: Literal["text"] = "text",
        echo: EchoOptions = "none",
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> AsyncGenerator[str, None]: ...

    @overload
    async def stream_async(
        self,
        *args: Content | str,
        content: Literal["all"],
        echo: EchoOptions = "none",
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> AsyncGenerator[str | ContentToolRequest | ContentToolResult, None]: ...

    async def stream_async(
        self,
        *args: Content | str,
        content: Literal["text", "all"] = "text",
        echo: EchoOptions = "none",
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> AsyncGenerator[str | ContentToolRequest | ContentToolResult, None]:
        """
        Generate a response from the chat in a streaming fashion asynchronously.

        Parameters
        ----------
        args
            The user input(s) to generate a response from.
        content
            Whether to yield just text content or include rich content objects
            (e.g., tool calls) when relevant.
        echo
            One of the following (default is "none"):
              - `"text"`: Echo just the text content of the response.
              - `"output"`: Echo text and tool call content.
              - `"all"`: Echo both the assistant and user turn.
              - `"none"`: Do not echo any content.
        kwargs
            Additional keyword arguments to pass to the method used for requesting
            the response.

        Returns
        -------
        ChatResponseAsync
            An (unconsumed) response from the chat. Iterate over this object to
            consume the response.
        """
        turn = user_turn(*args)

        display = self._markdown_display(echo=echo)

        async def wrapper() -> AsyncGenerator[
            str | ContentToolRequest | ContentToolResult, None
        ]:
            with display:
                async for chunk in self._chat_impl_async(
                    turn,
                    stream=True,
                    echo=echo,
                    content=content,
                    kwargs=kwargs,
                ):
                    yield chunk

        return wrapper()

    def extract_data(
        self,
        *args: Content | str,
        data_model: type[BaseModel],
        echo: EchoOptions = "none",
        stream: bool = False,
    ) -> dict[str, Any]:
        """
        Extract structured data from the given input.

        Parameters
        ----------
        args
            The input to extract data from.
        data_model
            A Pydantic model describing the structure of the data to extract.
        echo
            One of the following (default is "none"):
              - `"text"`: Echo just the text content of the response.
              - `"output"`: Echo text and tool call content.
              - `"all"`: Echo both the assistant and user turn.
              - `"none"`: Do not echo any content.
        stream
            Whether to stream the response (i.e., have the response appear in chunks).

        Returns
        -------
        dict[str, Any]
            The extracted data.
        """

        display = self._markdown_display(echo=echo)

        response = ChatResponse(
            self._submit_turns(
                user_turn(*args),
                data_model=data_model,
                echo=echo,
                stream=stream,
            )
        )

        with display:
            for _ in response:
                pass

        turn = self.get_last_turn()
        assert turn is not None

        res: list[ContentJson] = []
        for x in turn.contents:
            if isinstance(x, ContentJson):
                res.append(x)

        if len(res) != 1:
            raise ValueError(
                f"Data extraction failed: {len(res)} data results received."
            )

        json = res[0]
        return json.value

    async def extract_data_async(
        self,
        *args: Content | str,
        data_model: type[BaseModel],
        echo: EchoOptions = "none",
        stream: bool = False,
    ) -> dict[str, Any]:
        """
        Extract structured data from the given input asynchronously.

        Parameters
        ----------
        args
            The input to extract data from.
        data_model
            A Pydantic model describing the structure of the data to extract.
        echo
            One of the following (default is "none"):
              - `"text"`: Echo just the text content of the response.
              - `"output"`: Echo text and tool call content.
              - `"all"`: Echo both the assistant and user turn.
              - `"none"`: Do not echo any content.
        stream
            Whether to stream the response (i.e., have the response appear in chunks).
            Defaults to `True` if `echo` is not "none".

        Returns
        -------
        dict[str, Any]
            The extracted data.
        """

        display = self._markdown_display(echo=echo)

        response = ChatResponseAsync(
            self._submit_turns_async(
                user_turn(*args),
                data_model=data_model,
                echo=echo,
                stream=stream,
            )
        )

        with display:
            async for _ in response:
                pass

        turn = self.get_last_turn()
        assert turn is not None

        res: list[ContentJson] = []
        for x in turn.contents:
            if isinstance(x, ContentJson):
                res.append(x)

        if len(res) != 1:
            raise ValueError(
                f"Data extraction failed: {len(res)} data results received."
            )

        json = res[0]
        return json.value

    def register_tool(
        self,
        func: Callable[..., Any] | Callable[..., Awaitable[Any]],
        *,
        model: Optional[type[BaseModel]] = None,
    ):
        """
        Register a tool (function) with the chat.

        The function will always be invoked in the current Python process.

        Examples
        --------

        If your tool has straightforward input parameters, you can just
        register the function directly (type hints and a docstring explaning
        both what the function does and what the parameters are for is strongly
        recommended):

        ```python
        from chatlas import ChatOpenAI, Tool


        def add(a: int, b: int) -> int:
            '''
            Add two numbers together.

            Parameters
            ----------
            a : int
                The first number to add.
            b : int
                The second number to add.
            '''
            return a + b


        chat = ChatOpenAI()
        chat.register_tool(add)
        chat.chat("What is 2 + 2?")
        ```

        If your tool has more complex input parameters, you can provide a Pydantic
        model that corresponds to the input parameters for the function, This way, you
        can have fields that hold other model(s) (for more complex input parameters),
        and also more directly document the input parameters:

        ```python
        from chatlas import ChatOpenAI, Tool
        from pydantic import BaseModel, Field


        class AddParams(BaseModel):
            '''Add two numbers together.'''

            a: int = Field(description="The first number to add.")

            b: int = Field(description="The second number to add.")


        def add(a: int, b: int) -> int:
            return a + b


        chat = ChatOpenAI()
        chat.register_tool(add, model=AddParams)
        chat.chat("What is 2 + 2?")
        ```

        Parameters
        ----------
        func
            The function to be invoked when the tool is called.
        model
            A Pydantic model that describes the input parameters for the function.
            If not provided, the model will be inferred from the function's type hints.
            The primary reason why you might want to provide a model in
            Note that the name and docstring of the model takes precedence over the
            name and docstring of the function.
        """
        tool = Tool(func, model=model)
        self._tools[tool.name] = tool

    def on_tool_request(self, callback: Callable[[ContentToolRequest], None]):
        """
        Register a callback for a tool request event.

        A tool request event occurs when the assistant requests a tool to be
        called on its behalf. Before invoking the tool, `on_tool_request`
        handlers are called with the relevant `ContentToolRequest` object. This
        is useful if you want to handle tool requests in a custom way, such as
        requiring logging them or requiring user approval before invoking the
        tool

        Parameters
        ----------
        callback
            A function to be called when a tool request event occurs.
            This function must have a single argument, which will be the
            tool request (i.e., a `ContentToolRequest` object).

        Returns
        -------
        A callable that can be used to remove the callback later.
        """
        return self._on_tool_request_callbacks.add(callback)

    def on_tool_result(self, callback: Callable[[ContentToolResult], None]):
        """
        Register a callback for a tool result event.

        A tool result event occurs when a tool has been invoked and the
        result is ready to be provided to the assistant. After the tool
        has been invoked, `on_tool_result` handlers are called with the
        relevant `ContentToolResult` object. This is useful if you want to
        handle tool results in a custom way such as logging them.

        Parameters
        ----------
        callback
            A function to be called when a tool result event occurs.
            This function must have a single argument, which will be the
            tool result (i.e., a `ContentToolResult` object).

        Returns
        -------
        A callable that can be used to remove the callback later.
        """
        return self._on_tool_result_callbacks.add(callback)

    @property
    def current_display(self) -> Optional[MarkdownDisplay]:
        """
        Get the currently active markdown display, if any.

        The display represents the place where `.chat(echo)` content is
        being displayed. In a notebook/Quarto, this is a wrapper around
        `IPython.display`. Otherwise, it is a wrapper around a
        `rich.live.Live()` console.

        This is primarily useful if you want to add custom content to the
        display while the chat is running, but currently blocked by something
        like a tool call.

        Example
        -------
        ```python
        import requests
        from chatlas import ChatOpenAI

        chat = ChatOpenAI()


        def get_current_weather(latitude: float, longitude: float):
            "Get the current weather given a latitude and longitude."

            lat_lng = f"latitude={latitude}&longitude={longitude}"
            url = f"https://api.open-meteo.com/v1/forecast?{lat_lng}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
            response = requests.get(url)
            json = response.json()
            if chat.current_display:
                chat.current_display.echo("My custom tool display!!!")
            return json["current"]


        chat.register_tool(get_current_weather)

        chat.chat("What's the current temperature in Duluth, MN?", echo="text")
        ```


        Returns
        -------
        Optional[MarkdownDisplay]
            The currently active markdown display, if any.
        """
        return self._current_display

    def _echo_content(self, x: str):
        if self._current_display:
            self._current_display.echo(x)

    def export(
        self,
        filename: str | Path,
        *,
        turns: Optional[Sequence[Turn]] = None,
        title: Optional[str] = None,
        content: Literal["text", "all"] = "text",
        include_system_prompt: bool = True,
        overwrite: bool = False,
    ):
        """
        Export the chat history to a file.

        Parameters
        ----------
        filename
            The filename to export the chat to. Currently this must
            be a `.md` or `.html` file.
        turns
            The `.get_turns()` to export. If not provided, the chat's current turns
            will be used.
        title
            A title to place at the top of the exported file.
        overwrite
            Whether to overwrite the file if it already exists.
        content
            Whether to include text content, all content (i.e., tool calls), or no
            content.
        include_system_prompt
            Whether to include the system prompt in a <details> tag.

        Returns
        -------
        Path
            The path to the exported file.
        """
        if not turns:
            turns = self.get_turns(include_system_prompt=False)
        if not turns:
            raise ValueError("No turns to export.")

        if isinstance(filename, str):
            filename = Path(filename)

        filename = filename.resolve()
        if filename.exists() and not overwrite:
            raise ValueError(
                f"File {filename} already exists. Set `overwrite=True` to overwrite."
            )

        if filename.suffix not in {".md", ".html"}:
            raise ValueError("The filename must have a `.md` or `.html` extension.")

        # When exporting to HTML, we lean on shiny's chat component for rendering markdown and styling
        is_html = filename.suffix == ".html"

        # Get contents from each turn
        content_arr: list[str] = []
        for turn in turns:
            turn_content = "\n\n".join(
                [
                    str(x).strip()
                    for x in turn.contents
                    if content == "all" or isinstance(x, ContentText)
                ]
            )
            if is_html:
                msg_type = "user" if turn.role == "user" else "chat"
                content_attr = html_escape(turn_content)
                turn_content = f"<shiny-{msg_type}-message content='{content_attr}'></shiny-{msg_type}-message>"
            else:
                turn_content = f"## {turn.role.capitalize()}\n\n{turn_content}"
            content_arr.append(turn_content)
        contents = "\n\n".join(content_arr)

        # Shiny chat message components requires container elements
        if is_html:
            contents = f"<shiny-chat-messages>\n{contents}\n</shiny-chat-messages>"
            contents = f"<shiny-chat-container>{contents}</shiny-chat-container>"

        # Add title to the top
        if title:
            if is_html:
                contents = f"<h1>{title}</h1>\n\n{contents}"
            else:
                contents = f"# {title}\n\n{contents}"

        # Add system prompt to the bottom
        if include_system_prompt and self.system_prompt:
            contents += f"\n<br><br>\n<details><summary>System prompt</summary>\n\n{self.system_prompt}\n\n</details>"

        # Wrap in HTML template if exporting to HTML
        if is_html:
            contents = self._html_template(contents)

        with open(filename, "w") as f:
            f.write(contents)

        return filename

    @staticmethod
    def _html_template(contents: str) -> str:
        version = "1.2.1"
        shiny_www = (
            f"https://cdn.jsdelivr.net/gh/posit-dev/py-shiny@{version}/shiny/www/"
        )

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
          <script src="{shiny_www}/py-shiny/chat/chat.js"></script>
          <link rel="stylesheet" href="{shiny_www}/py-shiny/chat/chat.css">
          <link rel="stylesheet" href="{shiny_www}/shared/bootstrap/bootstrap.min.css">
        </head>
        <body>
          <div style="max-width:700px; margin:0 auto; padding-top:20px;">
            {contents}
          </div>
        </body>
        </html>
        """

    @overload
    def _chat_impl(
        self,
        user_turn: Turn,
        echo: EchoOptions,
        content: Literal["text"],
        stream: bool,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> Generator[str, None, None]: ...

    @overload
    def _chat_impl(
        self,
        user_turn: Turn,
        echo: EchoOptions,
        content: Literal["all"],
        stream: bool,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> Generator[str | ContentToolRequest | ContentToolResult, None, None]: ...

    def _chat_impl(
        self,
        user_turn: Turn,
        echo: EchoOptions,
        content: Literal["text", "all"],
        stream: bool,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> Generator[str | ContentToolRequest | ContentToolResult, None, None]:
        user_turn_result: Turn | None = user_turn
        while user_turn_result is not None:
            for chunk in self._submit_turns(
                user_turn_result,
                echo=echo,
                stream=stream,
                kwargs=kwargs,
            ):
                yield chunk

            turn = self.get_last_turn(role="assistant")
            assert turn is not None
            user_turn_result = None

            results: list[ContentToolResult] = []
            for x in turn.contents:
                if isinstance(x, ContentToolRequest):
                    if echo == "output":
                        self._echo_content(f"\n\n{x}\n\n")
                    if content == "all":
                        yield x
                    res = self._invoke_tool(x)
                    if echo == "output":
                        self._echo_content(f"\n\n{res}\n\n")
                    if content == "all":
                        yield res
                    results.append(res)

            if results:
                user_turn_result = Turn("user", results)

    @overload
    def _chat_impl_async(
        self,
        user_turn: Turn,
        echo: EchoOptions,
        content: Literal["text"],
        stream: bool,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> AsyncGenerator[str, None]: ...

    @overload
    def _chat_impl_async(
        self,
        user_turn: Turn,
        echo: EchoOptions,
        content: Literal["all"],
        stream: bool,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> AsyncGenerator[str | ContentToolRequest | ContentToolResult, None]: ...

    async def _chat_impl_async(
        self,
        user_turn: Turn,
        echo: EchoOptions,
        content: Literal["text", "all"],
        stream: bool,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> AsyncGenerator[str | ContentToolRequest | ContentToolResult, None]:
        user_turn_result: Turn | None = user_turn
        while user_turn_result is not None:
            async for chunk in self._submit_turns_async(
                user_turn_result,
                echo=echo,
                stream=stream,
                kwargs=kwargs,
            ):
                yield chunk

            turn = self.get_last_turn(role="assistant")
            assert turn is not None
            user_turn_result = None

            results: list[ContentToolResult] = []
            for x in turn.contents:
                if isinstance(x, ContentToolRequest):
                    if echo == "output":
                        self._echo_content(f"\n\n{x}\n\n")
                    if content == "all":
                        yield x
                    res = await self._invoke_tool_async(x)
                    if echo == "output":
                        self._echo_content(f"\n\n{res}\n\n")
                    if content == "all":
                        yield res
                    else:
                        yield "\n\n"
                    results.append(res)

            if results:
                user_turn_result = Turn("user", results)

    def _submit_turns(
        self,
        user_turn: Turn,
        echo: EchoOptions,
        stream: bool,
        data_model: type[BaseModel] | None = None,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> Generator[str, None, None]:
        if any(x._is_async for x in self._tools.values()):
            raise ValueError("Cannot use async tools in a synchronous chat")

        def emit(text: str | Content):
            self._echo_content(str(text))

        emit("<br>\n\n")

        if echo == "all":
            emit_user_contents(user_turn, emit)

        if stream:
            response = self.provider.chat_perform(
                stream=True,
                turns=[*self._turns, user_turn],
                tools=self._tools,
                data_model=data_model,
                kwargs=kwargs,
            )

            result = None
            for chunk in response:
                text = self.provider.stream_text(chunk)
                if text:
                    emit(text)
                    yield text
                result = self.provider.stream_merge_chunks(result, chunk)

            turn = self.provider.stream_turn(
                result,
                has_data_model=data_model is not None,
            )

            if echo == "all":
                emit_other_contents(turn, emit)

        else:
            response = self.provider.chat_perform(
                stream=False,
                turns=[*self._turns, user_turn],
                tools=self._tools,
                data_model=data_model,
                kwargs=kwargs,
            )

            turn = self.provider.value_turn(
                response, has_data_model=data_model is not None
            )
            if turn.text:
                emit(turn.text)
                yield turn.text

            if echo == "all":
                emit_other_contents(turn, emit)

        self._turns.extend([user_turn, turn])

    async def _submit_turns_async(
        self,
        user_turn: Turn,
        echo: EchoOptions,
        stream: bool,
        data_model: type[BaseModel] | None = None,
        kwargs: Optional[SubmitInputArgsT] = None,
    ) -> AsyncGenerator[str, None]:
        def emit(text: str | Content):
            self._echo_content(str(text))

        emit("<br>\n\n")

        if echo == "all":
            emit_user_contents(user_turn, emit)

        if stream:
            response = await self.provider.chat_perform_async(
                stream=True,
                turns=[*self._turns, user_turn],
                tools=self._tools,
                data_model=data_model,
                kwargs=kwargs,
            )

            result = None
            async for chunk in response:
                text = self.provider.stream_text(chunk)
                if text:
                    emit(text)
                    yield text
                result = self.provider.stream_merge_chunks(result, chunk)

            turn = self.provider.stream_turn(
                result,
                has_data_model=data_model is not None,
            )

            if echo == "all":
                emit_other_contents(turn, emit)

        else:
            response = await self.provider.chat_perform_async(
                stream=False,
                turns=[*self._turns, user_turn],
                tools=self._tools,
                data_model=data_model,
                kwargs=kwargs,
            )

            turn = self.provider.value_turn(
                response, has_data_model=data_model is not None
            )
            if turn.text:
                emit(turn.text)
                yield turn.text

            if echo == "all":
                emit_other_contents(turn, emit)

        self._turns.extend([user_turn, turn])

    def _invoke_tool(self, x: ContentToolRequest) -> ContentToolResult:
        tool_def = self._tools.get(x.name, None)
        func = tool_def.func if tool_def is not None else None

        if func is None:
            e = RuntimeError(f"Unknown tool: {x.name}")
            return ContentToolResult(value=None, error=e, request=x)

        # First, invoke the request callbacks. If a ToolRejectError is raised,
        # treat it like a tool failure (i.e., gracefully handle it).
        result: ContentToolResult | None = None
        try:
            self._on_tool_request_callbacks.invoke(x)
        except ToolRejectError as e:
            result = ContentToolResult(value=None, error=e, request=x)

        # Invoke the tool (if it hasn't been rejected).
        if result is None:
            try:
                if isinstance(x.arguments, dict):
                    res = func(**x.arguments)
                else:
                    res = func(x.arguments)

                if isinstance(res, ContentToolResult):
                    result = res
                else:
                    result = ContentToolResult(value=res)

                result.request = x
            except Exception as e:
                result = ContentToolResult(value=None, error=e, request=x)

        # If we've captured an error, notify and log it.
        if result.error:
            warnings.warn(
                f"Calling tool '{x.name}' led to an error.",
                ToolFailureWarning,
                stacklevel=2,
            )
            traceback.print_exc()
            log_tool_error(x.name, str(x.arguments), result.error)

        self._on_tool_result_callbacks.invoke(result)
        return result

    async def _invoke_tool_async(self, x: ContentToolRequest) -> ContentToolResult:
        tool_def = self._tools.get(x.name, None)
        func = None
        if tool_def:
            if tool_def._is_async:
                func = tool_def.func
            else:
                func = wrap_async(tool_def.func)

        if func is None:
            e = RuntimeError(f"Unknown tool: {x.name}")
            return ContentToolResult(value=None, error=e, request=x)

        # First, invoke the request callbacks. If a ToolRejectError is raised,
        # treat it like a tool failure (i.e., gracefully handle it).
        result: ContentToolResult | None = None
        try:
            await self._on_tool_request_callbacks.invoke_async(x)
        except ToolRejectError as e:
            result = ContentToolResult(value=None, error=e, request=x)

        # Invoke the tool (if it hasn't been rejected).
        if result is None:
            try:
                if isinstance(x.arguments, dict):
                    res = await func(**x.arguments)
                else:
                    res = await func(x.arguments)

                if isinstance(res, ContentToolResult):
                    result = res
                else:
                    result = ContentToolResult(value=res)

                result.request = x
            except Exception as e:
                result = ContentToolResult(value=None, error=e, request=x)

        # If we've captured an error, notify and log it.
        if result.error:
            warnings.warn(
                f"Calling tool '{x.name}' led to an error.",
                ToolFailureWarning,
                stacklevel=2,
            )
            traceback.print_exc()
            log_tool_error(x.name, str(x.arguments), result.error)

        await self._on_tool_result_callbacks.invoke_async(result)
        return result

    def _markdown_display(self, echo: EchoOptions) -> ChatMarkdownDisplay:
        """
        Get a markdown display object based on the echo option.

        The idea here is to use rich for consoles and IPython.display.Markdown
        for notebooks, since the latter is much more responsive to different
        screen sizes.
        """
        if echo == "none":
            return ChatMarkdownDisplay(MockMarkdownDisplay(), self)

        # rich does a lot to detect a notebook environment, but it doesn't
        # detect Quarto (at least not yet).
        from rich.console import Console

        is_web = Console().is_jupyter or os.getenv("QUARTO_PYTHON", None) is not None

        opts = self._echo_options

        if is_web:
            display = IPyMarkdownDisplay(opts)
        else:
            display = LiveMarkdownDisplay(opts)

        return ChatMarkdownDisplay(display, self)

    def set_echo_options(
        self,
        rich_markdown: Optional[dict[str, Any]] = None,
        rich_console: Optional[dict[str, Any]] = None,
        css_styles: Optional[dict[str, str]] = None,
    ):
        """
        Set echo styling options for the chat.

        Parameters
        ----------
        rich_markdown
            A dictionary of options to pass to `rich.markdown.Markdown()`.
            This is only relevant when outputting to the console.
        rich_console
            A dictionary of options to pass to `rich.console.Console()`.
            This is only relevant when outputting to the console.
        css_styles
            A dictionary of CSS styles to apply to `IPython.display.Markdown()`.
            This is only relevant when outputing to the browser.
        """
        self._echo_options: EchoDisplayOptions = {
            "rich_markdown": rich_markdown or {},
            "rich_console": rich_console or {},
            "css_styles": css_styles or {},
        }

    def __str__(self):
        turns = self.get_turns(include_system_prompt=False)
        res = ""
        for turn in turns:
            icon = "👤" if turn.role == "user" else "🤖"
            res += f"## {icon} {turn.role.capitalize()} turn:\n\n{str(turn)}\n\n"
        return res

    def __repr__(self):
        turns = self.get_turns(include_system_prompt=True)
        tokens = sum(sum(turn.tokens) for turn in turns if turn.tokens)
        res = f"<Chat turns={len(turns)} tokens={tokens}>"
        for turn in turns:
            res += "\n" + turn.__repr__(indent=2)
        return res + "\n"

    def __deepcopy__(self, memo):
        result = self.__class__.__new__(self.__class__)

        # Avoid recursive references
        memo[id(self)] = result

        # Copy all attributes except the problematic provider attribute
        for key, value in self.__dict__.items():
            if key != "provider":
                setattr(result, key, copy.deepcopy(value, memo))
            else:
                setattr(result, key, value)

        return result


class ChatResponse:
    """
    Chat response object.

    An object that, when displayed, will simulatenously consume (if not
    already consumed) and display the response in a streaming fashion.

    This is useful for interactive use: if the object is displayed, it can
    be viewed as it is being generated. And, if the object is not displayed,
    it can act like an iterator that can be consumed by something else.

    Attributes
    ----------
    content
        The content of the chat response.

    Properties
    ----------
    consumed
        Whether the response has been consumed. If the response has been fully
        consumed, then it can no longer be iterated over, but the content can
        still be retrieved (via the `content` attribute).
    """

    def __init__(self, generator: Generator[str, None]):
        self._generator = generator
        self.content: str = ""

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        chunk = next(self._generator)
        self.content += chunk  # Keep track of accumulated content
        return chunk

    def get_content(self) -> str:
        """
        Get the chat response content as a string.
        """
        for _ in self:
            pass
        return self.content

    @property
    def consumed(self) -> bool:
        return inspect.getgeneratorstate(self._generator) == inspect.GEN_CLOSED

    def __str__(self) -> str:
        return self.get_content()


class ChatResponseAsync:
    """
    Chat response (async) object.

    An object that, when displayed, will simulatenously consume (if not
    already consumed) and display the response in a streaming fashion.

    This is useful for interactive use: if the object is displayed, it can
    be viewed as it is being generated. And, if the object is not displayed,
    it can act like an iterator that can be consumed by something else.

    Attributes
    ----------
    content
        The content of the chat response.

    Properties
    ----------
    consumed
        Whether the response has been consumed. If the response has been fully
        consumed, then it can no longer be iterated over, but the content can
        still be retrieved (via the `content` attribute).
    """

    def __init__(self, generator: AsyncGenerator[str, None]):
        self._generator = generator
        self.content: str = ""

    def __aiter__(self) -> AsyncIterator[str]:
        return self

    async def __anext__(self) -> str:
        chunk = await self._generator.__anext__()
        self.content += chunk  # Keep track of accumulated content
        return chunk

    async def get_content(self) -> str:
        "Get the chat response content as a string."
        async for _ in self:
            pass
        return self.content

    @property
    def consumed(self) -> bool:
        if sys.version_info < (3, 12):
            raise NotImplementedError(
                "Checking for consumed state is only supported in Python 3.12+"
            )
        return inspect.getasyncgenstate(self._generator) == inspect.AGEN_CLOSED


# ----------------------------------------------------------------------------
# Helpers for emitting content
# ----------------------------------------------------------------------------


def emit_user_contents(
    x: Turn,
    emit: Callable[[Content | str], None],
):
    if x.role != "user":
        raise ValueError("Expected a user turn")
    emit(f"## 👤 User turn:\n\n{str(x)}\n\n")
    emit_other_contents(x, emit)
    emit("\n\n## 🤖 Assistant turn:\n\n")


def emit_other_contents(
    x: Turn,
    emit: Callable[[Content | str], None],
):
    # Gather other content to emit in _reverse_ order
    to_emit: list[str] = []

    if x.finish_reason:
        to_emit.append(f"\n\n<< 🤖 finish reason: {x.finish_reason} \\>\\>\n\n")

    has_text = False
    has_other = False
    for content in reversed(x.contents):
        if isinstance(content, ContentText):
            has_text = True
        else:
            has_other = True
            to_emit.append(str(content))

    if has_text and has_other:
        if x.role == "user":
            to_emit.append("<< 👤 other content >>")
        else:
            to_emit.append("<< 🤖 other content >>")

    to_emit.reverse()

    emit("\n\n".join(to_emit))


# Helper/wrapper class to let Chat know about the currently active display
class ChatMarkdownDisplay:
    def __init__(self, display: MarkdownDisplay, chat: Chat):
        self._display = display
        self._chat = chat

    def __enter__(self):
        self._chat._current_display = self._display
        return self._display.__enter__()

    def __exit__(self, *args, **kwargs):
        result = self._display.__exit__(*args, **kwargs)
        self._chat._current_display = None
        return result

    def append(self, content):
        return self._display.echo(content)


class ToolFailureWarning(RuntimeWarning):
    pass


# By default warnings are shown once; we want to always show them.
warnings.simplefilter("always", ToolFailureWarning)
