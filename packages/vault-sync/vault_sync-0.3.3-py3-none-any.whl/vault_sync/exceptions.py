class ConfigException(Exception):
    """The given configuration file is not valid"""


class VaultLoginException(Exception):
    """Incorrect credentials (role_id/secret_id) given for vault login"""
