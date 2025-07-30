# src/darca_storage/interfaces/file_backend.py
# License: MIT

from typing import List, Optional, Protocol, Union


class FileBackend(Protocol):
    """
    Async-first contract for storage back-ends.

    All operations are coroutines.  Concrete implementations may delegate to
    thread-pool helpers or native async SDKs, but callers can always:

        await backend.read(...)
    """

    async def read(
        self, path: str, *, binary: bool = False
    ) -> Union[str, bytes]:
        """
        Return the full contents of *path*.

        Args:
            path: Absolute path of the file.
            binary: If True, return bytes; otherwise decode as text.
        """
        ...

    async def write(
        self,
        path: str,
        content: Union[str, bytes],
        *,
        binary: bool = False,
        permissions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> None:
        """
        Overwrite or create *path* with *content*.

        Optional:
            permissions - chmod bits (e.g. 0o644)
            user        - chown to given username (requires privilege)
        """
        ...

    async def delete(self, path: str) -> None:
        """Remove a regular file."""
        ...

    async def exists(self, path: str) -> bool:
        """Return True if *path* exists (file or directory)."""
        ...

    async def list(
        self, base_path: str, *, recursive: bool = False
    ) -> List[str]:
        """
        List directory *base_path*.

        Returns:
            List of paths, relative to *base_path* when recursive=True,
            otherwise direct children.
        """
        ...

    async def mkdir(
        self,
        path: str,
        *,
        parents: bool = True,
        permissions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> None:
        """Create directory *path* (and parents if requested)."""
        ...

    async def rmdir(self, path: str) -> None:
        """Recursively remove directory *path*."""
        ...

    async def rename(self, src: str, dest: str) -> None:
        """Move or rename a file/directory."""
        ...

    async def stat_mtime(self, path: str) -> float:
        """
        Return last-modified time (UNIX epoch seconds) for *path*.

        Raises:
            FileUtilsException if *path* does not exist.
        """
        ...
