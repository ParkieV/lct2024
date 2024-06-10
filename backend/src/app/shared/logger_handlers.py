from logging import FileHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL


class LoggerHandler(FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False, logger_level: int | tuple[int, int] = DEBUG):
        super().__init__(filename, mode, encoding, delay)
        self.logger_level = logger_level

    def emit(self, record):
        if isinstance(self.logger_level, int):
            if not (record.levelno == self.logger_level):
                return
        elif isinstance(self.logger_level, tuple):
            if not (self.logger_level[0] <= record.levelno <= self.logger_level[1]):
                return
        super().emit(record)


class DebugLoggerHandler(LoggerHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False, logger_level = DEBUG):
        super().__init__(filename, mode, encoding, delay, logger_level)


class DefaultLoggerHandler(LoggerHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False, logger_level = (INFO, WARNING)):
        super().__init__(filename, mode, encoding, delay, logger_level)


class ErrorLoggerHandler(LoggerHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False, logger_level = ERROR):
        super().__init__(filename, mode, encoding, delay, logger_level)


class CriticalLoggerHandler(LoggerHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False, logger_level = CRITICAL):
        super().__init__(filename, mode, encoding, delay, logger_level)
