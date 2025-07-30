AioAllay WIP


> 🌐 [English](https://github.com/yurasulima/AioAllay/blob/main/README.en.md) | 🇺🇦 [Українська](https://github.com/yurasulima/AioAllay/blob/main/README.uk.md)

AioAllay is an asynchronous client for interacting with the [Dangerous](https://mblueberry.fun) Minecraft Bedrock server API.

Features

    🌀 Asynchronous (based on aiohttp)

    🛠️ Easy integration into asyncio applications

    📦 Interaction with user profiles, orders, logs, and more

Installation

Install via PyPI:

pip install aioallay

Or install from source:

git clone https://github.com/yurasulima/AioAllay.git
cd AioAllay
pip install .

Example usage
    
    import asyncio
    from typing import List
    from aioallay.types import User
    from aioallay import Client
    
    TOKEN = "your-token"
    
    client = Client(token=TOKEN)
    
    async def main() -> None:
        users: List[User] = await client.get_all_user()
        print(users)
    
    if __name__ == "__main__":
        asyncio.run(main())

Requirements

    Python 3.10 or higher

    pydantic~=2.11.5

    aiohttp~=3.10.11

License

MIT © Yurii Sulima