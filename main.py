import asyncio
from db import init_models
from service import run


if __name__ == "__main__":
    asyncio.run(init_models())
    run()
