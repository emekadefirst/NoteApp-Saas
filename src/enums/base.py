from enum import Enum

class Module(str, Enum):
    NOTE = "note"
    ORGANIZATION = "organization"
    USER = "user"
    PERMISSION = "permssions"


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


class OrganizationModule(str, Enum):
    NOTE = "note"
    USER = "user"
    ORG_PERMISSION = "ogranization_permssions"