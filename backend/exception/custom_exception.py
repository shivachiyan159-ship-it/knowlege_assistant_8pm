import sys
from typing import Optional
import traceback
from backend.logger import GLOBAL_LOGGER as log


class CustomException(Exception):
    # attributes
    # methods
    # special method
    def __init__(self, error_message, error_detail: Optional[object] = None):
        # normalize message
        normal_message = str(error_message)

        exc_type = exc_value = exc_tb = None

        # checking exception types
        if error_detail is None:  # CustomException("Division failed")
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_detail, "exc_info"):  # CustomException("Division failed",sys)
                exc_type, exc_value, exc_tb = error_detail.exc_info()
            # CustomException("Division failed",e)
            elif isinstance(error_detail, BaseException):
                exc_type, exc_value, exc_tb = type(
                    error_detail), error_detail, error_detail.__traceback__
            else:
                exc_type, exc_value, exc_tb = sys.exc_info()

        # walk through last tarce back
        last_tb = exc_tb
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next

        # setting all properties from laststarce back
        self.file_name = last_tb.tb_frame.f_code.co_filename
        self.lineno = last_tb.tb_lineno
        self.error_message = normal_message

        if exc_type and exc_tb:
            self.traceback_str = "".join(
                traceback.format_exception(*sys.exc_info()))
        else:
            self.traceback_str = ""

        super().__init__(self.__str__())

    def __str__(self):
        log.info("str method")
        return f"""
           Error in [{self.file_name}] at line [{self.lineno}]
           Message: {self.error_message}
           Traceback: {self.traceback_str}
    
        """
