# src/darca_storage/decorators/scoped_backend.py

import os
from typing import List, Optional, Union

from darca_storage.exceptions import StorageClientPathViolation
from darca_storage.interfaces.file_backend import FileBackend


class ScopedFileBackend(FileBackend):
    """
    Scoped façade over a FileBackend.

    Every path the caller supplies is interpreted *relative* to `base_path` and
    is first normalised through `_full_path` to prevent path-escape attacks.
    """

    def __init__(self, backend: FileBackend, base_path: str) -> None:
        self._backend: FileBackend = backend
        self._base_path: str = os.path.abspath(base_path)

    def _full_path(self, relative_path: str) -> str:
        """
        Resolve *relative_path* against `self._base_path` and reject escapes.

        Raises:
            StorageClientPathViolation - when traversal attempts to break
            out of the scoped root (e.g. '../../etc/passwd').
        """
        full = os.path.realpath(
            os.path.abspath(os.path.join(self._base_path, relative_path))
        )
        base = os.path.realpath(self._base_path)

        if not (full == base or full.startswith(base + os.sep)):
            raise StorageClientPathViolation(
                attempted_path=full, base_path=base
            )
        return full

    async def read(
        self, relative_path: str, *, binary: bool = False
    ) -> Union[str, bytes]:
        return await self._backend.read(
            self._full_path(relative_path), binary=binary
        )

    async def write(
        self,
        relative_path: str,
        content: Union[str, bytes],
        *,
        binary: bool = False,
        permissions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> None:
        await self._backend.write(
            path=self._full_path(relative_path),
            content=content,
            binary=binary,
            permissions=permissions,
            user=user,
        )

    async def delete(self, relative_path: str) -> None:
        await self._backend.delete(self._full_path(relative_path))

    async def exists(self, relative_path: str) -> bool:
        return await self._backend.exists(self._full_path(relative_path))

    async def list(
        self,
        relative_path: str = ".",
        *,
        recursive: bool = False,
    ) -> List[str]:
        return await self._backend.list(
            self._full_path(relative_path), recursive=recursive
        )

    async def mkdir(
        self,
        relative_path: str,
        *,
        parents: bool = True,
        permissions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> None:
        await self._backend.mkdir(
            path=self._full_path(relative_path),
            parents=parents,
            permissions=permissions,
            user=user,
        )

    async def rmdir(self, relative_path: str) -> None:
        await self._backend.rmdir(self._full_path(relative_path))

    async def rename(self, src_relative: str, dest_relative: str) -> None:
        await self._backend.rename(
            self._full_path(src_relative),
            self._full_path(dest_relative),
        )

    async def stat_mtime(self, relative_path: str) -> float:
        return await self._backend.stat_mtime(self._full_path(relative_path))
