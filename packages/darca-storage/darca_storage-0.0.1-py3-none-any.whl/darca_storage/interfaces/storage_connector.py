# src/darca_storage/interfaces/storage_connector.py
# License: MIT
"""
Async interface for creating scoped StorageClient instances.

A connector encapsulates whatever is needed to reach a given storage backend
(local path, S3 bucket, in-memory store…).  Implementations must:
- Verify the backend is reachable (`verify_connection`)
- Verify the caller has access rights (`verify_access`)
- Produce a ready-to-use `StorageClient` (`connect`)
All three operations are *coroutines* so event-loop callers remain
non-blocking.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from darca_storage.backends.local_file_backend import LocalFileBackend


class StorageConnector(ABC):
    """
    Abstract contract for connecting to any storage backend.

    Concrete implementations typically carry configuration (e.g. `base_path`
    for local disk, bucket + credentials for S3) and perform lightweight
    health checks before handing back a `StorageClient`.
    """

    # ──────────────────────────── lifecycle ─────────────────────────── #

    @abstractmethod
    async def connect(self) -> LocalFileBackend:
        """
        Return a SCOPED FileBackend instance, ready for use.

        Raises:
            RuntimeError   - backend not reachable
            PermissionError - access denied


        Implementations MUST wrap raw backends with ScopedFileBackend
        (or equivalent)
        to enforce path confinement and prevent directory escape.
        """
        ...

    # ──────────────────────────── probes ────────────────────────────── #

    @abstractmethod
    async def verify_connection(self) -> bool:
        """
        Lightweight check: does the backend exist / respond?

        Examples:
            • Local path exists
            • S3 bucket HeadBucket succeeds
        """
        ...

    @abstractmethod
    async def verify_access(
        self,
        *,
        user: Optional[str] = None,
        permissions: Optional[int] = None,
    ) -> bool:
        """
        Verify caller can create, write, and delete inside the backend root.

        Args:
            user:        POSIX username to test chown operations (optional)
            permissions: chmod bits to test permission propagation (optional)
        """
        ...
