# darca_storage/interfaces/credential_aware.py
# License: MIT

from abc import ABC, abstractmethod
from typing import Dict


class CredentialAware(ABC):
    """
    Interface for backends or connectors that accept runtime credentials.

    Implementations may use credentials for authentication, authorization,
    token exchange, scoped access, or other runtime configuration.
    """

    @abstractmethod
    def inject_credentials(self, credentials: Dict[str, str]) -> None:
        """
        Provide credential material to the backend or connector.

        Args:
            credentials (dict): Key-value credential map
        """
        ...
