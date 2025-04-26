import os
import shutil
import hashlib
import asyncio
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Assuming logger is imported from another module
from utils.logger import logger

class FileOperations:
    MAX_WORKERS = 4
    _executor = concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS)

    @staticmethod
    async def copy_with_verification(src: str, dest: str) -> bool:
        """Copy a file and verify the hash matches"""
        try:
            src_hash = await FileOperations.compute_file_hash(src)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)
            dest_hash = await FileOperations.compute_file_hash(dest)

            if src_hash != dest_hash:
                await logger.error(f"Hash mismatch after copying {src} to {dest}")
                return False

            return True
        except Exception as error:
            await logger.error(f"Error copying file {src} to {dest}", error)
            return False

    @staticmethod
    async def compute_file_hash(file_path: str) -> str:
        """Compute SHA-256 hash of a file"""
        loop = asyncio.get_event_loop()
        
        def _hash_file():
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        
        return await loop.run_in_executor(FileOperations._executor, _hash_file)

    @staticmethod
    async def ensure_dir(dir_path: str) -> None:
        """Create directory if it doesn't exist"""
        os.makedirs(dir_path, exist_ok=True)

    @staticmethod
    async def copy_dir_concurrent(src: str, dest: str, compute_hash: bool = False) -> bool:
        """Copy directory contents concurrently using process pool"""
        try:
            await FileOperations.ensure_dir(dest)
            entries = os.listdir(src)
            tasks = []

            for entry in entries:
                src_path = os.path.join(src, entry)
                dest_path = os.path.join(dest, entry)

                if os.path.isdir(src_path):
                    await FileOperations.ensure_dir(dest_path)
                    # Recursively copy subdirectories
                    task = asyncio.create_task(
                        FileOperations.copy_dir_concurrent(src_path, dest_path, compute_hash)
                    )
                    tasks.append(task)
                else:
                    # Process files using worker processes
                    if compute_hash:
                        task = asyncio.create_task(
                            FileOperations.copy_with_verification(src_path, dest_path)
                        )
                    else:
                        task = asyncio.create_task(
                            FileOperations._copy_file(src_path, dest_path)
                        )
                    tasks.append(task)

            if not tasks:
                return True

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)
            return all(results)

        except Exception as error:
            await logger.error(f"Error copying directory {src} to {dest}", error)
            return False

    @staticmethod
    async def _copy_file(src: str, dest: str) -> bool:
        """Simple file copy without verification"""
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                FileOperations._executor, 
                lambda: shutil.copyfile(src, dest)
            )
            return True
        except Exception:
            return False

    @staticmethod
    async def create_backup(path: str) -> Optional[str]:
        """Create a backup of a file with timestamp in the name"""
        try:
            backup_path = f"{path}.backup-{int(datetime.now().timestamp() * 1000)}"
            shutil.copyfile(path, backup_path)
            await logger.info(f"Created backup at {backup_path}")
            return backup_path
        except Exception as error:
            await logger.error(f"Failed to create backup of {path}", error)
            return None

    @staticmethod
    async def cleanup(directory: str, older_than_days: int) -> None:
        """Remove files and directories older than the specified days"""
        try:
            now = datetime.now()
            max_age = timedelta(days=older_than_days)
            
            for entry in os.scandir(directory):
                try:
                    mtime = datetime.fromtimestamp(entry.stat().st_mtime)
                    if now - mtime > max_age:
                        if entry.is_dir():
                            shutil.rmtree(entry.path)
                        else:
                            os.unlink(entry.path)
                        await logger.info(f"Cleaned up old file/directory: {entry.path}")
                except Exception as e:
                    await logger.error(f"Error cleaning up {entry.path}", e)
        except Exception as error:
            await logger.error(f"Error during cleanup of {directory}", error)