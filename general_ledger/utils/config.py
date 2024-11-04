from typing import Optional


class Config:
    """this is a singleton class that for config items that need to be migrated into dedicated classes"""

    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        instance: Config
        if cls._instance is None:
            instance = object.__new__(cls)
            cls._instance = instance
        else:
            instance = cls._instance
        return instance
