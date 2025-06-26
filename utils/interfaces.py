# create an interface to create structure from json
from abc import ABC, abstractmethod 
from typing import Dict, Any

class JsonSerializable(ABC):
    """
    An interface for classes that can be serialized from a JSON structure.
    """

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JsonSerializable':
        """
        Create an instance of the class from a dictionary representation.

        Args:
            data (Dict[str, Any]): The dictionary representation of the object.

        Returns:
            JsonSerializable: An instance of the class.
        """
        pass

    @classmethod
    @abstractmethod
    def to_dict(cls) -> Dict[str, Any]:
        """
        Convert the instance to a dictionary representation.

        Returns:
            Dict[str, Any]: The dictionary representation of the object.
        """
        pass