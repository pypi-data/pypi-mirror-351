# darca_storage/client.py

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from darca_storage.interfaces.file_backend import FileBackend


class StorageClient(FileBackend):
    """
    Session-aware client wrapping a ScopedFileBackend.

    Implements the full FileBackend interface with added support for:
      - Session metadata
      - Optional user and credential context
      - Introspection and future hooks (e.g. refresh, flush, presign_url)

    All paths are relative to the scoped root directory
    enforced by the backend.
    """

    def __init__(
        self,
        backend: FileBackend,
        *,
        session_metadata: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        credentials: Optional[Dict[str, str]] = None,
    ) -> None:
        self._backend = backend
        self._session_metadata = session_metadata or {}
        self._user = user
        self._credentials = credentials or {}

    async def read(
        self, relative_path: str, *, binary: bool = False
    ) -> Union[str, bytes]:
        return await self._backend.read(
            relative_path=relative_path, binary=binary
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
            relative_path=relative_path,
            content=content,
            binary=binary,
            permissions=permissions,
            user=user or self._user,
        )

    async def delete(self, relative_path: str) -> None:
        await self._backend.delete(relative_path=relative_path)

    async def exists(self, relative_path: str) -> bool:
        return await self._backend.exists(relative_path=relative_path)

    async def list(
        self, relative_path: str = ".", *, recursive: bool = False
    ) -> List[str]:
        return await self._backend.list(
            relative_path=relative_path, recursive=recursive
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
            relative_path=relative_path,
            parents=parents,
            permissions=permissions,
            user=user or self._user,
        )

    async def rmdir(self, relative_path: str) -> None:
        await self._backend.rmdir(relative_path=relative_path)

    async def rename(self, src_relative: str, dest_relative: str) -> None:
        await self._backend.rename(
            src_relative=src_relative,
            dest_relative=dest_relative,
        )

    async def stat_mtime(self, relative_path: str) -> float:
        return await self._backend.stat_mtime(relative_path=relative_path)

    @property
    def backend(self) -> FileBackend:
        """Access the underlying backend (for diagnostics or chaining)."""
        return self._backend

    @property
    def session(self) -> Dict[str, Any]:
        """Arbitrary metadata describing the active storage session."""
        return self._session_metadata

    @property
    def user(self) -> Optional[str]:
        """Logical user this session may be scoped to."""
        return self._user

    @property
    def credentials(self) -> Dict[str, str]:
        """Credentials associated with this session (if any)."""
        return self._credentials

    def context(self) -> Dict[str, Any]:
        """
        Return contextual information for debugging or observability.
        Redacts credentials by default.
        """
        return {
            "user": self._user,
            "session_metadata": self._session_metadata,
            "backend_type": type(self._backend).__name__,
            "credentials": (
                {k: "***" for k in self._credentials}
                if self._credentials
                else None
            ),
        }

    async def refresh(self) -> None:
        """
        Hook for refreshing credentials, tokens, or connections.
        Override in cloud-capable subclasses.
        """
        pass

    async def flush(self) -> None:
        """
        Hook for flushing buffered data to storage.
        Useful for future implementations (e.g., batching or append-only logs).
        """
        pass

    async def presign_url(
        self, relative_path: str, expires_in: int
    ) -> Optional[str]:
        """
        Generate a presigned download URL (only meaningful for cloud backends).

        Returns:
            URL string or None (default no-op).
        """
        return None
