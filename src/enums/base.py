from enum import Enum

class Module(str, Enum):
    NOTE = "note"
    ORGANIZATION = "organization"
    USER = "user"
    PERMISSION = "permssions"
    ADMIN = "admin"


class Action(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE =  "inactive"


class AdminRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"


class OrganizationRole(str, Enum):
    MODERATOR = "moderator"
    BASE_USER = "base user"


