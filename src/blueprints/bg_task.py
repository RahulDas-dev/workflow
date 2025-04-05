import asyncio
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


async def rm_directory(pth: Path) -> None:
    for child in pth.iterdir():
        if child.is_file():
            await asyncio.to_thread(Path(child).unlink)
        else:
            await rm_directory(child)
    pth.rmdir()


async def cleanup_temp_files(file_paths: List[Path]) -> None:
    logger.info("House keeping Going on ...")
    try:
        for f_path in file_paths:
            if f_path.is_file():
                await asyncio.to_thread(Path(f_path).unlink)
            if f_path.is_dir():
                await rm_directory(f_path)
        logger.info("House keeping Complited")
    except Exception as e:
        logger.error(f"Error while removing file {file_paths}: {e}")
