from abc import abstractmethod, ABC


class AbstractStrategy(ABC):
    """Abstract base class for all patching strategies."""

    @abstractmethod
    def execute(self, *args):
        """Execute the patching logic. Subclasses will implement their specific patching behavior.

        Args:
            *args: Variable arguments to be used in patching (target_path, name, behavior, etc.)

        Returns:
            A patch object or a mock object.
        """
        pass
