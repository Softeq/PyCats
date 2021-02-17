import os
import logging
from functools import wraps
from typing import List

from common._libs.helpers.os_helpers import get_timestamp, create_folder
from common._libs.helpers.singleton import Singleton
from common._libs.helpers.utils import slugify


def set_logger_format(format_string):
    def outer_wrapper(func):
        @wraps(set_logger_format)
        def inner_wrapper(self, *args, **kwargs):
            def set_formatter(formatter):
                if len(self.logger.handlers) > 0:
                    logger = self.logger
                else:
                    logger = logging.getLogger()
                for handler in logger.handlers:
                    handler.setFormatter(formatter)

            original_formatter = logging.getLogger().handlers[0].formatter
            new_formatter = logging.Formatter(format_string)

            set_formatter(new_formatter)
            func(self, *args, **kwargs)
            set_formatter(original_formatter)

        return inner_wrapper

    return outer_wrapper


class Counter(metaclass=Singleton):

    def __init__(self):
        self.generator = self.get_step_number()
        self.generator.__next__()

    @staticmethod
    def get_step_number():
        step = 0
        while True:
            start_from = yield step
            if isinstance(start_from, int):
                step = start_from - 1
            else:
                step += 1

    def __getattr__(self, item):
        return getattr(self.generator, item)


class PyCatsLogger:
    enable_libs_logging = False
    log_level = None
    base_log_dir = None
    time_log_dir = get_timestamp()

    step_generator = type("StepCounter", (Counter,), {})()
    prec_generator = type("PrecCounter", (Counter,), {})()
    __tab_alignment = "\t\t\t\t"
    __separator_line_length = 60
    log_format = (
        '%(asctime)s - '
        '%(levelname)s: '
        '[%(name)s]: '
        '%(message)s'
    )
    _logger_instances: List[logging.Logger] = list()

    @property
    def base_log_path(self):
        path = os.path.join(self.base_log_dir, self.time_log_dir)
        create_folder(path)
        return path

    def __init__(self, logger: logging.Logger, log_level: int = None):
        self.log_level = log_level or PyCatsLogger.log_level
        self.logger = logger

        self._file_handler = None
        self._stream_handler = logging.StreamHandler()
        self._stream_handler.setLevel(self.log_level)
        self._stream_handler.setFormatter(logging.Formatter(self.log_format))

        if not self.enable_libs_logging:
            self.logger.propagate = False
            self.logger.addHandler(self._stream_handler)

        logging.basicConfig(level=self.log_level, handlers=[self._stream_handler])
        self._logger_instances.append(self.logger)

    def switch_test(self, filename: str):
        filename = slugify(filename)
        if not filename.endswith(".log"):
            filename += ".log"

        # self.base_log_path = os.path.join(self.base_log_dir, self.time_log_dir)
        # create_folder(self.base_log_path)

        # prepare file handler for new test
        self._file_handler = logging.FileHandler(f"{self.base_log_path}/{filename}")
        self._file_handler.setLevel(self.log_level)
        self._file_handler.setFormatter(logging.Formatter(self.log_format))

        logging.root.handlers.clear()

        if self.enable_libs_logging:
            logging.basicConfig(level=self.log_level, handlers=[self._stream_handler, self._file_handler])
        else:
            for logger in self._logger_instances:
                logger.handlers.clear()
                logger.addHandler(self._stream_handler)
                logger.addHandler(self._file_handler)

        self.reset_counters()

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def exception(self, message: str):
        self.logger.exception(message)

    @staticmethod
    def _split_line(text, maxlen):
        msg_list = []
        text1 = ''
        c = 0
        result_max_len = 0
        for i in text.split():
            if c + len(i) > maxlen:
                msg_list.append(text1[:-1])
                result_max_len = c - 1 if c - 1 > result_max_len else result_max_len
                text1 = ''
                c = 0
            text1 += i + ' '
            c += len(i) + 1
        if len(text1) != 0:
            msg_list.append(text1[:-1])
            result_max_len = len(text1) if result_max_len < len(text1) else result_max_len
        return msg_list, result_max_len

    @set_logger_format(format_string="%(asctime)s - %(levelname)s: %(message)s")
    def log_step(self, description: str, precondition: bool = False):
        """
        Log the step of the test
        :param description: description of the step (actions that will be performed)
        :param precondition: flag is step of precondition (False by default):
            False - tests step
            True - precondition step
        """
        if precondition is True:
            step = f"PRECONDITION {self.prec_generator.__next__()}"
        else:
            step = f"STEP {self.step_generator.__next__()}"

        message = f"{step}: {description}"
        msg_lines_list, max_line_len = self._split_line(message, 50)

        border = self.__tab_alignment + '-' * self.__separator_line_length
        self.info(border)
        for msg_line in msg_lines_list:
            alignment_indent = ' ' * (((self.__separator_line_length - len(msg_line)) // 2) - 2)
            line = alignment_indent + msg_line + alignment_indent
            self.info(self.__tab_alignment + f"| {line} |")
        self.info(border)

    @set_logger_format(format_string="%(asctime)s - %(levelname)s: %(message)s")
    def log_fail(self, message):
        self._add_section('!!! TEST RESULT: FAIL !!!', message)

    @set_logger_format(format_string="%(asctime)s - %(levelname)s: %(message)s")
    def log_title(self, message):
        """
        Log as title in format: %(levelname)s - %(asctime)s - %(message)s \t\t\t\t <message>
        :param message: log message (actions that will be performed)
        """
        self.logger.info("")
        msg_lines_list, max_line_len = self._split_line(message, 50)
        for msg_line in msg_lines_list:
            line = ' ' * ((self.__separator_line_length - len(msg_line)) // 2) + msg_line
            self.logger.info(self.__tab_alignment + line)
        self.logger.info("")

    def _add_section(self, header_msg, message=None):
        header = f"{self.__tab_alignment}{header_msg}"
        border = '-' * self.__separator_line_length
        self.info(f"{border}")
        self.info(f"{header}")
        if message:
            self.info(f"{message}")
        self.info(f"{border}")

    @classmethod
    def reset_counters(cls):
        PyCatsLogger.step_generator.send(1)
        PyCatsLogger.prec_generator.send(1)
