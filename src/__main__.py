"""Allow ``python -m src`` (Apify CLI local runs) to execute the Actor."""

from src.main import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
