import asyncio

from core.llm import setup_chat_service


async def main() -> None:
    service = setup_chat_service(base_url="http://localhost:11434/v1", model="llama3")
    messages = [{"role": "user", "content": "Tell my a very short joke."}]
    print("Streaming response:")
    async for token in service.chat_stream(messages):
        print(token, end="", flush=True)
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
