# darca_storage/factory.py
# License: MIT

"""
StorageConnectorFactory

Resolves URL-based schemes (e.g. file:///data) into a connected,
scoped StorageClient.

This factory guarantees that all returned clients operate over a
ScopedFileBackend,
preventing directory traversal and enforcing per-root isolation.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional
from urllib.parse import unquote, urlparse

from darca_storage.client import StorageClient
from darca_storage.connectors.local import LocalStorageConnector
from darca_storage.decorators.scoped_backend import ScopedFileBackend
from darca_storage.interfaces.credential_aware import CredentialAware
from darca_storage.interfaces.file_backend import FileBackend


class StorageConnectorFactory:
    """
    Entrypoint for resolving a URL into a ready-to-use StorageClient.

    Guarantees that the returned client uses a securely scoped backend.
    """

    @staticmethod
    async def from_url(
        url: str,
        *,
        session_metadata: Optional[Dict[str, Any]] = None,
        credentials: Optional[Dict[str, str]] = None,
        parameters: Optional[Dict[str, str]] = None,
    ) -> StorageClient:
        """
        Parse a URL and return a connected, scoped StorageClient.

        Args:
            url (str): A storage URL (e.g., file:///data)
            session_metadata (dict, optional): Metadata associated with
            this session credentials (dict, optional): Credential map
            (e.g., {"user": "...", "token": "..."})
            parameters (dict, optional): Additional connection parameters

        Returns:
            StorageClient: Session-aware client wrapping a ScopedFileBackend

        Raises:
            ValueError: If the scheme is unsupported
            RuntimeError: If backend returned is not safely scoped
            PermissionError: If access to the base path is denied
        """
        parsed = urlparse(url)
        scheme = parsed.scheme
        path = unquote(parsed.path)

        if scheme == "file":
            base_path = os.path.abspath(path or "/")

            connector = LocalStorageConnector(
                base_path=base_path,
                credentials=credentials,
                parameters=parameters,
            )

            # Inject credentials if the connector supports it
            if isinstance(connector, CredentialAware) and credentials:
                connector.inject_credentials(credentials)

            backend: FileBackend = await connector.connect()

            # Enforce scoped backend invariant
            if not isinstance(backend, ScopedFileBackend):
                raise RuntimeError(
                    f"Connector '{connector.__class__.__name__}' returned "
                    "an unscoped backend. "
                    "All backends must be wrapped in ScopedFileBackend to "
                    "ensure path isolation."
                )

            return StorageClient(
                backend=backend,
                session_metadata={
                    **(session_metadata or {}),
                    "scheme": "file",
                    "base_path": base_path,
                },
                credentials=credentials,
            )

        raise ValueError(f"Unsupported storage scheme: '{scheme}'")
