from dataclasses import dataclass, asdict
from enum import Enum


from enum import Enum


class Height(Enum):
    """
    Enumeration representing different height categories.

    Attributes:
        TALL (int): Represents tall height (4).
        MEDIUM (int): Represents medium height (3).
        SHORT (int): Represents short height (2).
        VERY_SHORT (int): Represents very short height (1).
        NONE (int): Represents no height (0).
    """

    TALL = 4
    MEDIUM = 3
    SHORT = 2
    VERY_SHORT = 1
    NONE = 0


class Stamina(Enum):
    """
    Represents the stamina levels for altar servers.

    Attributes:
        HIGH (int): The highest stamina level.
        MEDIUM (int): The medium stamina level.
        LOW (int): The lowest stamina level.
        NONE (int): No stamina level.
    """

    HIGH = 3
    MEDIUM = 2
    LOW = 1
    NONE = 0


@dataclass(slots=True)
class Server:
    """
    Represents a server.

    Attributes:
        name (str): The name of the server.
        height (Height): The height category of the server.
        stamina (Stamina): The stamina category of the server.
        is_senior (bool): Indicates if the server is a senior server.
        is_young (bool): Indicates if the server is a young server.
        is_older (bool): Indicates if the server is an older server.
        jobs_doing (int): The number of jobs the server is currently doing.

    Methods:
        to_json(): Converts the server object to a JSON-compatible dictionary.
        from_json(data: dict): Creates a server object from a JSON-compatible dictionary.
    """

    name: str
    height: Height
    stamina: Stamina
    is_senior: bool
    is_young: bool
    is_older: bool

    jobs_doing: int = 0

    def to_json(self) -> dict:
        """
        Converts the server object to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representing the server object in JSON format.
        """
        data = asdict(self)
        data["height"] = data["height"].name
        data["stamina"] = data["stamina"].name
        del data["jobs_doing"]
        return data

    @classmethod
    def from_json(cls, data: dict):
        """
        Creates a server object from a JSON-compatible dictionary.

        Args:
            data (dict): A dictionary representing the server object in JSON format.

        Returns:
            Server: A server object created from the provided JSON data.
        """
        data["height"] = Height[data["height"]]
        data["stamina"] = Stamina[data["stamina"]]
        return cls(**data)

    def __hash__(self):
        return hash(self.name)


@dataclass(slots=True)
class Job:
    """
    Represents a job object.

    Attributes:
        name (str): The name of the job.
        min_height (Height): The minimum height required for the job.
        min_stamina (Stamina): The minimum stamina required for the job.
        senior_required (bool): Indicates if seniority is required for the job.
        younger_required (bool): Indicates if being younger is required for the job.
        older_required (bool): Indicates if being older is required for the job.
        requires_pair (bool): Indicates if the job requires a pair.

    Methods:
        to_json(): Converts the job object to a JSON dictionary.
        from_json(data: dict): Creates a job object from a JSON dictionary.
    """

    name: str
    min_height: Height
    min_stamina: Stamina
    senior_required: bool
    younger_required: bool
    older_required: bool
    requires_pair: bool

    def to_json(self) -> dict:
        """
        Convert the object to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representation of the object.
        """
        data = asdict(self)
        data["min_height"] = data["min_height"].name
        data["min_stamina"] = data["min_stamina"].name
        return data

    @classmethod
    def from_json(cls, data: dict):
        """
        Creates an instance of the class from a JSON dictionary.

        Args:
            cls: The class to create an instance of.
            data: The JSON dictionary containing the data for the instance.

        Returns:
            An instance of the class with the data from the JSON dictionary.
        """
        data["min_height"] = Height[data["min_height"]]
        data["min_stamina"] = Stamina[data["min_stamina"]]
        return cls(**data)
