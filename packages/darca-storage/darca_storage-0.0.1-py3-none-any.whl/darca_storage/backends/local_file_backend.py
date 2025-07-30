# src/darca_storage/backends/local_file_backend.py
# License: MIT
"""
Async local-disk backend that delegates to darca_file_utils under the hood,
executed via asyncio.to_thread so the event-loop remains free.
"""

from __future__ import annotations

import asyncio
import os
from typing import List, Optional, Union

from darca_file_utils.directory_utils import DirectoryUtils
from darca_file_utils.file_utils import FileUtils, FileUtilsException

from darca_storage.interfaces.file_backend import FileBackend


class LocalFileBackend(FileBackend):  # noqa: D101  (docstring inherited)

    async def read(
        self, path: str, *, binary: bool = False
    ) -> Union[str, bytes]:
        # FileUtils.read_file auto-detects binary vs text
        return await asyncio.to_thread(
            FileUtils.read_file, file_path=path, binary=binary
        )

    async def write(
        self,
        path: str,
        content: Union[str, bytes],
        *,
        binary: bool = False,
        permissions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> None:
        await asyncio.to_thread(
            FileUtils.write_file,
            file_path=path,
            content=content,
            binary=binary,
            permissions=permissions,
            user=user,
        )

    async def delete(self, path: str) -> None:
        await asyncio.to_thread(FileUtils.remove_file, path)

    async def exists(self, path: str) -> bool:
        return await asyncio.to_thread(
            lambda p=path: FileUtils.file_exist(p)
            or DirectoryUtils.directory_exist(p)
        )

    async def list(
        self, base_path: str, *, recursive: bool = False
    ) -> List[str]:
        return await asyncio.to_thread(
            DirectoryUtils.list_directory, base_path, recursive
        )

    async def mkdir(
        self,
        path: str,
        *,
        parents: bool = True,
        permissions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> None:
        await asyncio.to_thread(
            DirectoryUtils.create_directory,
            path,
            permissions=permissions,
            user=user,
        )

    async def rmdir(self, path: str) -> None:
        await asyncio.to_thread(DirectoryUtils.remove_directory, path)

    async def rename(self, src: str, dest: str) -> None:
        await asyncio.to_thread(self._rename_sync, src, dest)

    def _rename_sync(self, src: str, dest: str) -> None:
        if FileUtils.file_exist(src):
            FileUtils.rename_file(src, dest)
        elif DirectoryUtils.directory_exist(src):
            DirectoryUtils.rename_directory(src, dest)
        else:
            raise FileUtilsException(
                message=f"Cannot rename: source path does not exist: {src}",
                error_code="RENAME_SOURCE_NOT_FOUND",
                metadata={"src": src, "dest": dest},
            )

    async def stat_mtime(self, path: str) -> float:
        if not await self.exists(path):
            raise FileUtilsException(
                message=f"Cannot stat: path does not exist: {path}",
                error_code="STAT_MTIME_NOT_FOUND",
                metadata={"path": path},
            )
        return await asyncio.to_thread(os.path.getmtime, path)
