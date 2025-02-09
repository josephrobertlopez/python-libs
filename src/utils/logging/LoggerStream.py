class LoggerStream:
    """A stream that redirects writes to a logger."""

    def __init__(self, level):
        """
        Initialize the stream with a logging level.

        Args:
            level (callable): A logging method (e.g., logger.info, logger.error).
        """
        self.level = level
        self.buffer = ""

    def write(self, message: str) -> None:
        """
        Write a message to the logger. Ensure the message is logged continuously on the same line.

        Args:
            message (str): The message to log.
        """
        self.buffer += message  # Accumulate the message
        if message.endswith("\n"):  # If a newline is encountered, log the entire buffer
            self.level(self.buffer.strip())
            self.buffer = ""  # Reset the buffer

    def flush(self) -> None:
        """Flush buffered messages, if any."""
        if self.buffer:
            self.level(self.buffer.strip())
        self.buffer = ""  # Clear the buffer after flushing
