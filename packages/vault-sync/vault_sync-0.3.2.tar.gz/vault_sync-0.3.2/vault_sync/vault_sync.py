import json
from os import environ
from pathlib import Path
from typing import List, Union

import hvac
from hvac.api.auth_methods import Kubernetes
from hvac.exceptions import Forbidden, InvalidPath, InvalidRequest
from loguru import logger
from pydantic import ValidationError

from vault_sync.config import AuthMethod, Config, Vault
from vault_sync.exceptions import ConfigException, VaultLoginException


class VaultSync:
    """
    A class to synchronize secrets between a source Vault and a destination Vault.

    This class is responsible for automating the process of retrieving, parsing, and
    transferring structured data (secrets) from a source HashiCorp Vault instance
    to a destination HashiCorp Vault instance. It supports listing secrets,
    retrieving paths, fetching secrets, and updating destination secrets with
    the intention of maintaining consistent state between the two Vault instances.
    """

    def __init__(self, config_file: str):
        self.config = self.load_config(config_file)
        self.source_client = hvac.Client(url=self.config.source.url)
        self.destination_client = hvac.Client(url=self.config.destination.url)

    @staticmethod
    def load_config(config_file: Union[Path, str]) -> Config:
        """
        Loads a configuration file, parses its contents, and returns a Config object.

        This method expects a JSON format for the configuration data and attempts to
        deserialize it into a Config object. It validates the configuration format
        using strict adherence to rules defined in the Config data model.

        Arguments:
        config_file: Path or str
            Path to the configuration file on disk, given as either a pathlib.Path
            object or a string representing file path.

        Returns:
        Config
            A fully initialized and validated Config object created using the
            parsed JSON data.

        Raises:
        ConfigException
            If the content of the provided file is not valid JSON or fails
            to match the validation criteria imposed by the Config model.
        """
        try:
            with open(config_file) as json_file:
                data = json.load(json_file)
            config = Config(**data)
            return config
        except (json.JSONDecodeError, ValidationError) as err:
            raise ConfigException(str(err))

    @staticmethod
    def authenticate_client(client: hvac.Client, config: Vault) -> None:
        if config.auth_method == AuthMethod.APPROLE:
            client.auth.approle.login(
                role_id=config.role_id,
                secret_id=config.secret_id,
            )
        elif config.auth_method == AuthMethod.KUBERNETES:
            try:
                with open(config.token_path) as token_file:
                    token = token_file.read()
            except FileNotFoundError:
                raise VaultLoginException("token file not found.")

            Kubernetes(client.adapter).login(config.role_name, token)
        else:
            client.token = config.token
            if environ.get("VAULT_TOKEN"):
                client.token = environ.get("VAULT_TOKEN")

        # raise if we are still not authenticated
        if not client.is_authenticated():
            raise VaultLoginException("failed to authenticate.")

    def authenticate_clients(self) -> None:
        """
        Authenticate clients with Vault services.

        This method attempts to authenticate both source and destination clients
        using approle-based login. If the clients are already authenticated, the
        method exits without re-authentication.

        Raises:
            VaultLoginException: Raised when authentication fails due to invalid
                requests or forbidden access.

        """
        try:
            if self.source_client.is_authenticated() and self.destination_client.is_authenticated():
                logger.debug("clients already authenticated.")
                return

            logger.info("signin to source vault...")
            self.authenticate_client(client=self.source_client, config=self.config.source)

            logger.info("signin to destination vault...")
            self.authenticate_client(client=self.destination_client, config=self.config.destination)
        except (InvalidRequest, Forbidden) as err:
            raise VaultLoginException(str(err))

    @staticmethod
    def list_keys(client: hvac.Client, kv_path: str, mount_point: str) -> List[str]:
        """
        Retrieve a list of keys from a specified Vault KV v2 path.

        This method interacts with the Vault KV v2 secret engine to list the secrets
        available at the provided path. It returns a list of keys, excluding folder
        keys (i.e., keys ending with '/').

        Parameters:
            client (hvac.Client): Vault HVAC client instance to interact with the Vault API.
            kv_path (str): The path within the KV v2 secrets engine to list keys from.
            mount_point (str): The mount point of the KV v2 secrets engine.

        Returns:
            List[str]: A list of keys available at the given KV v2 path, excluding
            folder keys.
        """
        list_response = client.secrets.kv.v2.list_secrets(path=kv_path, mount_point=mount_point)
        return [key for key in list_response["data"]["keys"] if not key.endswith("/")]

    @staticmethod
    def list_folders(client: hvac.Client, kv_path: str, mount_point: str) -> List[str]:
        """
        Lists all folder names from a Vault KV2 secrets engine at a specific path. The method
        uses the provided Vault client to access the secrets engine and fetch the folder
        keys that represent subdirectories.

        Parameters
        ----------
        client : hvac.Client
            The Vault client used to connect to the KV2 secrets engine.
        kv_path : str
            The path to the key-value secrets engine where the folders are listed.
        mount_point : str
            The mount point of the KV2 secrets engine within the Vault instance.

        Returns
        -------
        List[str]
            A list of folder names, where each folder name ends with a forward slash ("/").
        """
        list_response = client.secrets.kv.v2.list_secrets(path=kv_path, mount_point=mount_point)
        return [key for key in list_response["data"]["keys"] if key.endswith("/")]

    def list_all_paths(self, client: hvac.Client, mount_point: str) -> List[str]:
        """
        Lists all paths available at a given mount point within a Vault system.

        This function explores and retrieves all available paths in a specified
        mount point of a HashiCorp Vault system by recursively walking through
        the directory structure. It starts from the root and dives deeper to
        collect a complete list of paths.

        Parameters:
            client (hvac.Client): The HVAC client instance used to interact
                with the Vault API.
            mount_point (str): The mount point in Vault where the paths
                should be listed from.

        Returns:
            List[str]: A list of string paths representing all accessible
                paths within the specified mount point.

        Raises:
            None
        """
        return self.walk_paths(client, "", [""], mount_point=mount_point)

    def walk_paths(self, client: hvac.Client, root: str, folders: List[str], mount_point: str) -> List[str]:
        """
        Recursively traverse paths in a secret management system to collect all sub-paths.

        This method generates a list of all paths (including sub-paths) starting from the
        specified root path in a secret management system. It utilizes recursive traversal
        to explore all available folders and collect their respective paths.

        Parameters:
        client (hvac.Client): The client instance used to interact with the secret
            management system.
        root (str): The root path from which the traversal starts.
        folders (List[str]): A list to store the collected paths during traversal.
        mount_point (str): The mount point in the secret management system.

        Returns:
        List[str]: A list containing all paths collected, including sub-paths and folders.
        """
        paths = [f"{root}{folder}" for folder in self.list_folders(client, root, mount_point=mount_point)]
        folders.extend(paths)
        for folder in paths:
            self.walk_paths(client, folder, folders, mount_point=mount_point)
        return folders

    def list_all_keys(self, client: hvac.Client, mount_point: str) -> List[str]:
        """
        Summarize and list all keys from the specified source paths.

        The method retrieves all base paths defined in the source, iterates through them,
        and gathers every key from each specified path. The resulting list provides an
        aggregated view of all keys that can be accessed from the given source structure.

        Returns:
            List[str]: A list containing the aggregated keys as strings.
        """
        return [
            f"{explore}{key}"
            for explore in self.list_all_paths(client, mount_point=mount_point)
            for key in self.list_keys(client, explore, mount_point=mount_point)
        ]

    @staticmethod
    def get_secret(client: hvac.Client, secret_path: str, mount_point: str) -> dict | None:
        """
        Fetches a secret from a specified path in a key-value store using the provided Vault client.
        This function tries to read a secret version from the Vault server. If the secret path does
        not exist, it logs this information and returns None. Otherwise, it retrieves the secret data.

        Args:
            client (hvac.Client): The Vault client used for the request. It is expected to be an
                instance of the hvac.Client class, configured to communicate with the Vault server.
            secret_path (str): The path to the secret that needs to be retrieved. This is the logical
                path used to locate the secret in the key-value store.
            mount_point (str): The mount point for the key-value secrets engine. Specifies the base
                path where the engine is located in Vault.

        Returns:
            dict | None: The function returns the secret data as a dictionary if successful. If the
                specified secret path does not exist or an error occurs during retrieval, it returns None.

        Raises:
            InvalidPath: If the specified path is invalid or cannot be accessed during the operation.
        """
        try:
            secret_version_response = client.secrets.kv.v2.read_secret_version(
                path=secret_path, mount_point=mount_point
            )
        except InvalidPath:
            logger.debug(f"secret {secret_path} not found in source, skipping...")
            return None

        return secret_version_response["data"]["data"]

    def update_destination_secret(self, secret_path: str, secret_data: dict) -> None:
        """
        Updates or creates a secret at the destination path.

        This function checks if a secret exists at the specified destination path and
        compares it with the provided secret data. If the secret exists and the data
        matches, the update is skipped. If the secret does not exist or the data
        differs, the secret is updated or created accordingly.

        Args:
            secret_path: The path to the secret in the destination key-value store.
            secret_data: The data to be stored in the secret.

        Raises:
            InvalidPath: If the specified secret path is invalid.

        Returns:
            None
        """
        try:
            secret_version_response = self.destination_client.secrets.kv.v2.read_secret_version(
                path=secret_path, mount_point=self.config.destination.kv_store
            )

            if secret_version_response["data"]["data"] == secret_data:
                logger.debug(f"skipping {secret_path}, secret is up to date.")
                return

            logger.info(f"secret {secret_path} in destination differs, updating...")
        except InvalidPath:
            logger.info(f"secret {secret_path} not found in destination, creating...")

        self.destination_client.secrets.kv.v2.create_or_update_secret(
            path=secret_path, mount_point=self.config.destination.kv_store, secret=secret_data
        )

    def sync(self, secret_path: str, mount_point: str) -> None:
        """
        Synchronizes secrets between source and destination clients.

        This method retrieves a secret from the source client and updates the
        destination client with the same secret if it exists. It operates based
        on the specified secret path and mount point. The synchronization ensures
        that the destination client has the latest version of the secret available
        from the source client.

        Parameters:
            secret_path (str): The path to the secret in the source client.
            mount_point (str): The mount point where the secret is located in the
                source client.

        Returns:
            None
        """
        secret = self.get_secret(self.source_client, secret_path=secret_path, mount_point=mount_point)
        if secret:
            self.update_destination_secret(secret_path, secret)

    def clean_orphans(self, secret_path):
        source_mount_point = self.config.source.kv_store
        dest_mount_point = self.config.destination.kv_store

        dest_secret = self.get_secret(self.destination_client, secret_path=secret_path, mount_point=dest_mount_point)
        source_secret = self.get_secret(self.source_client, secret_path=secret_path, mount_point=source_mount_point)
        if dest_secret and source_secret is None:
            logger.info(f"destination secret {secret_path} not found in source, deleting...")
            self.destination_client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=secret_path, mount_point=dest_mount_point
            )

    def sync_all(self) -> None:
        """
        Synchronizes all secrets between source and destination.

        This method iterates over all keys retrieved from the source and
        synchronizes each one using the `sync` method. Upon completion,
        a log message is generated to indicate the process has finished.

        Returns:
            None
        """
        source_mount_point = self.config.source.kv_store
        dest_mount_point = self.config.destination.kv_store

        for secret_path in self.list_all_keys(client=self.source_client, mount_point=source_mount_point):
            self.sync(secret_path, mount_point=source_mount_point)

        for secret_path in self.list_all_keys(client=self.destination_client, mount_point=dest_mount_point):
            self.clean_orphans(secret_path)
        logger.info("all done.")
