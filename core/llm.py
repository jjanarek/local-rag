from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from openai import AsyncStream
    from openai.types.chat import ChatCompletionChunk


class BaseChatService(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
        """
        Sends a list of messages to the LLM and returns a single string response.
        Useful for simple queries or when not streaming.
        """

        pass

    @abstractmethod
    def chat_stream(self, messages: list[dict[str, Any]], **kwargs: Any) -> AsyncIterator[str]:
        """
        Sends a list of messages to the LLM and yields chunks of text as they are generated.
        This gives a "typing" effect in the UI.
        """
        pass


class OpenAIChatService(BaseChatService):
    def __init__(self, base_url: str, model: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key="ollama")
        self.model = model

    async def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            stream=False,
            **kwargs,
        )
        if not isinstance(response, ChatCompletion):
            raise ValueError(f"Expected ChatCompletion, got {type(response)}")
        return response.choices[0].message.content or ""

    async def chat_stream(
        self, messages: list[dict[str, Any]], **kwargs: Any
    ) -> AsyncIterator[str]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]
            stream=True,
            **kwargs,
        )

        stream_response = cast("AsyncStream[ChatCompletionChunk]", response)
        async for chunk in stream_response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def setup_chat_service(base_url: str, model: str) -> OpenAIChatService:
    """Factory function for LLM chat service."""
    return OpenAIChatService(base_url=base_url, model=model)
