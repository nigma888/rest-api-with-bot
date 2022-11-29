import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    COPYWRITER = "COPYWRITER"
    MANAGER = "MANAGER"
