import logging
import os
import subprocess

class BaseClass:
    """
    A base class that provides logging functionality.
    """
    
    def __init__(self, is_loggable: bool = False):
        """
        Initializes the instance with optional logging capability.

        Args:
            is_loggable (bool, optional): If True, initializes a logger for the instance. Defaults to False.

        Attributes:
            logger: Logger instance if is_loggable is True, otherwise None.
        """
        self.logger = None
        if is_loggable:
            self.logger = self.get_logger(self.__class__.__name__)

    @staticmethod
    def get_logger(name=None):
        """
        Returns a configured logger instance with appropriate handlers and formatting based on the environment.

        If the logger does not already have handlers, this method sets up a handler:
        - In the "production" environment, logs are written to a file ("svs-core.log") at INFO level.
        - In other environments, logs are output to the console at DEBUG level.
        The log format includes the timestamp, log level, and message.

        Args:
            name (str, optional): The name of the logger. Defaults to None.

        Returns:
            logging.Logger: The configured logger instance.
        """

        env = os.getenv("ENV", "development")

        logger = logging.getLogger(name)
        logger.handlers.clear()  # Clear existing handlers to ensure fresh setup
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        if env == "production":
            handler = logging.FileHandler("svs-core.log")
            handler.setLevel(logging.INFO)
        else:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

class Executable(BaseClass):
    """
    A class to execute commands in a shell environment.
    """

    def __init__(self):
        super().__init__(is_loggable=True)

    def execute(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """
        Executes a shell command and returns the CompletedProcess object.

        Args:
            command (str): The command to execute.
            check (bool, optional): If True, raises CalledProcessError on non-zero exit. Defaults to True.

        Returns:
            subprocess.CompletedProcess: The result of the executed command.

        Raises:
            subprocess.CalledProcessError: If check is True and the command returns a non-zero exit status.
            Exception: For any other unexpected errors.
        """
        try:
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command '{command}' failed with error: {e.stderr}")
            return e
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}")
            raise
