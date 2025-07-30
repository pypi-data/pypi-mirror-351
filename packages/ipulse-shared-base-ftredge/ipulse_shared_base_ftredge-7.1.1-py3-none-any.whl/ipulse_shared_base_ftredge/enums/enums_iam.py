# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import Enum, auto


class AutoStrEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    def __str__(self) -> str:
        return self.value


class IAMUnitType(AutoStrEnum):
    GROUPS = auto()
    ROLES = auto()
    PERMISSIONS = auto()


class IAMAction(AutoStrEnum):
    ALLOW = auto()
    DENY = auto()
    GRANT = auto()
    REVOKE = auto()


class IAMUserType(AutoStrEnum):
    ANONYMOUS = auto()
    AUTHENTICATED = auto()
    CUSTOMER = auto()
    EXTERNAL = auto()
    PARTNER = auto()
    INTERNAL = auto()
    EMPLOYEE = auto()
    SYSTEM = auto()
    ADMIN = auto()
    SUPERADMIN = auto()
