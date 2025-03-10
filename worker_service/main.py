import asyncio

from logger import configure_logging
from rabbit.consumer import main

logger = configure_logging(__name__)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service was stopped!")
