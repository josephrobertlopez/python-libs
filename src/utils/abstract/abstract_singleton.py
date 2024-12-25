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
                    # Ensure only subclasses of AbstractSingleton are instantiated
                    if not issubclass(cls, AbstractSingleton):
                        raise TypeError(
                            "Only subclasses of AbstractSingleton can be instantiated."
                        )
                    cls._instances[cls] = super(AbstractSingleton, cls).__new__(
                        cls, *args, **kwargs
                    )
                    cls._instances[cls]._setup_called = (
                        False  # Initialize the setup called flag
                    )
        return cls._instances[cls]

    def setup(self):
        """Setup method that can only be called once per instance."""
        if self._setup_called:
            raise RuntimeError(
                f"{self.__class__.__name__} setup() has already been called."
            )
        self._setup_called = True
        self._setup()

    @abstractmethod
    def _setup(self):
        """Abstract method that each subclass must implement for its own setup process."""
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


class SampleConcreteSingleton(AbstractSingleton):
    """Concrete class that implements the abstract singleton setup."""

    def _setup(self):
        """Setup method implementation."""
        # Example setup process
        self._initialized = True
