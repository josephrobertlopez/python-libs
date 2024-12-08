class LoggerStream:
    """A stream that redirects writes to a logger."""

    def __init__(self, level):
        """
        Initialize the stream with a logging level.

        Args:
            level (callable): A logging method (e.g., logger.info, logger.error).
        """
        self.level = level
        self.buffer = []  # Store messages temporarily if buffering is required.

    def write(self, message: str) -> None:
        """
        Write a message to the logger.

        Args:
            message (str): The message to log.
        """
        message = message.strip()
        if message:
            self.level(message)

    def flush(self) -> None:
        """Flush buffered messages, if any."""
        for buffered_message in self.buffer:
            self.level(buffered_message)
        self.buffer.clear()