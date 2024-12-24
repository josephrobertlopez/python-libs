import threading
from abc import ABC, abstractmethod


class AbstractSingleton(ABC):
    """Abstract base class to enforce singleton behavior."""

    _instances = {}
    _lock = threading.Lock()  # Thread safety for the singleton

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    # Ensure only subclasses of SingletonBase are instantiated
                    if not issubclass(cls, AbstractSingleton):
                        raise TypeError(
                            "Only subclasses of SingletonBase can be instantiated."
                        )
                    cls._instances[cls] = super(AbstractSingleton, cls).__new__(
                        cls, *args, **kwargs
                    )
        return cls._instances[cls]

    @abstractmethod
    def setup(self):
        """Abstract method to define the setup process."""
        pass

    @classmethod
    def test_initialization(cls):
        """Check if the class has already been instantiated."""
        return cls in cls._instances

    @classmethod
    def delete_instance(cls):
        """Remove the instance from the singleton cache."""
        with cls._lock:
            if cls in cls._instances:
                del cls._instances[cls]
