from enum import Enum
from os import environ
from typing import Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Extra, root_validator, validator


class AuthMethod(str, Enum):
    APPROLE = "approle"
    KUBERNETES = "kubernetes"
    TOKEN = "token"


def is_valid_uuid(value: str) -> bool:
    try:
        val = UUID(value)
        return str(val) == value
    except (TypeError, ValueError, AttributeError):
        return False


class StrictModel(BaseModel):
    """Represents a Pydantic model with strict configuration settings.

    This class extends the BaseModel from Pydantic and configures model behavior
    to be strict in nature. Mutations are not allowed, making instances
    of this model immutable after creation. Enumerations used within
    the model are automatically converted to their values. Additionally,
    any extra fields not explicitly defined in the model schema are forbidden.

    Attributes:
        Config (class): Configuration class for the Pydantic model. Specifies
            behavior such as immutability, enumerated value usage, and handling
            of extra fields.

    """

    class Config:
        allow_mutation = False
        use_enum_values = True
        extra = Extra.forbid


class Vault(StrictModel):
    """
    Attributes:
        url: The URL of the Vault instance.
        auth_method: The authentication method to use, defaults to APPROLE. Can be optional.
        role_id: The ID of the role when using APPROLE authentication. Can be optional.
        secret_id: The secret associated with the role_id when using APPROLE authentication.
            Can be optional.
        token_path: Path to the token file when using KUBERNETES authentication. Can be
            optional.
        role_name: The name of the role when using KUBERNETES authentication. Can be
            optional.
        kv_store: The name of the key-value store.

    """

    url: AnyUrl
    auth_method: Optional[AuthMethod] = AuthMethod.APPROLE
    role_id: Optional[str]
    secret_id: Optional[str]
    token: Optional[str] = environ.get("VAULT_TOKEN")
    token_path: Optional[str]
    role_name: Optional[str]
    kv_store: str

    @root_validator
    def required_fields(cls, values):
        """
        Validates that all required fields for the selected authentication method
        are provided. This root validator checks the presence of necessary fields
        based on the chosen `auth_method` and raises a `ValueError` if any required
        fields are missing.

        Parameters
        ----------
        cls: Type[BaseModel]
            The class being validated.
        values: Dict[str, Any]
            The values dictionary containing fields to validate.

        Returns
        -------
        Dict[str, Any]
            Returns the original values dictionary if all required fields are present.

        Raises
        ------
        ValueError
            If one or more required fields are missing for the chosen
            authentication method.
        """
        auth_method = values.get("auth_method", AuthMethod.APPROLE)
        missing_fields = []
        if auth_method == AuthMethod.KUBERNETES:
            for key in ["token_path", "role_name"]:
                if values.get(key) is None:
                    missing_fields.append(key)
        elif auth_method == AuthMethod.APPROLE:
            for key in ["role_id", "secret_id"]:
                if values.get(key) is None:
                    missing_fields.append(key)
        else:
            if values.get("token") is None:
                missing_fields.append("token")

        if missing_fields:
            plural = "are" if len(missing_fields) > 1 else "is"
            msg = f"{', '.join(missing_fields)} {plural} required for auth method {auth_method.value}"
            raise ValueError(msg)

        return values

    @validator("role_id", "secret_id")
    def must_be_uuid(cls, value):
        """
        Validates that the provided values are valid UUIDs.

        This function acts as a validator for the specified parameters to ensure
        that they conform to the UUID format. If the provided value does not fit
        the UUID standard, an exception is raised. This is primarily used within
        the context of schema or data validation where UUIDs are required.

        Parameters:
            cls (Any): The class under validation, usually provided by the
                validator decorator.
            value: The value that needs to be checked if it is a valid UUID.

        Raises:
            ValueError: If the provided value is not a valid UUID.

        Returns:
            The validated value if it meets the UUID criteria.
        """
        if not is_valid_uuid(value):
            raise ValueError("must be a valid uuid")
        return value


class Schedule(StrictModel):
    """
    Represents a schedule configuration for periodic or single execution.

    This class defines a schedule model which determines the frequency at
    which specific actions or operations are executed. The `every` attribute
    controls the time interval in seconds, with `0` indicating a one-time-only
    execution.

    Attributes:
    every (int): The interval in seconds at which actions are executed. Setting
    to `0` means the operation runs only once.
    """

    every: int = 0


class Config(StrictModel):
    source: Vault
    destination: Vault
    schedule: Schedule = Schedule()
