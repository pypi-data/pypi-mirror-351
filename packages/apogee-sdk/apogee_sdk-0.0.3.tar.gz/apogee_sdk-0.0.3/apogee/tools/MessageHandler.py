import logging

class MessageHandler:
    def __init__(self):
        self.logger = logging.getLogger("my_sdk")
        self.set_level("WARNING")  # default level

        ch = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.propagate = False

    def set_level(self, level):
        """
        Accepts either a logging level integer or string name, e.g. logging.INFO or "INFO".
        """
        if isinstance(level, int):
            self.logger.setLevel(level)
        elif isinstance(level, str):
            level = level.upper()
            if level in logging._nameToLevel:
                self.logger.setLevel(logging._nameToLevel[level])
            else:
                raise ValueError(f"Invalid log level string: {level}")
        else:
            raise TypeError("Level must be int or str")

    #region METHODS
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
    #endregion


# shared logger instance
LoggingMessages = MessageHandler()