import sys
import traceback
from typing import Optional, cast

class CustomException(Exception):
    def __init__(self, error_message: str, error_details: Optional[object] = None):
        if isinstance(error_message, BaseException):
            norm_msg = str(error_message)
        else:
            norm_msg = str(error_message)

        exe_type = exe_value = exe_tb = None
        if error_details is None:
            exe_type, exe_value, exe_tb = sys.exc_info()
        else:
            if hasattr(error_details, "exec_info"):
                exe_info_obj = cast(sys, error_details)
                exe_type = exe_value = exe_tb = exe_info_obj.exc_info()
            elif isinstance(error_details, BaseException):
                exe_type = type(error_details)
                exe_value = error_details
                exe_tb = error_details.__traceback__
            else:
                exe_type, exe_value, exe_tb = sys.exc_info()

        last_tb = exe_tb
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next

        self.file_name = last_tb.tb_frame.f_code.co_filename if last_tb else "Unknown"
        self.line_number = last_tb.tb_lineno if last_tb else -1
        self.error_message = norm_msg

        if exe_type and exe_value and exe_tb:
          self.traceback_str = ''.join(traceback.format_exception(exe_type, exe_value, exe_tb))
        else:
          self.traceback_str = "No traceback available"

        super().__init__(self.__str__())

    def __str__(self):
        base = f"Error in file '{self.file_name}' at line {self.line_number}: {self.error_message}"
        if self.traceback_str:
            return f"{base}\nTraceback:\n{self.traceback_str}"
        return base

    def __repr__(self):
        return f"CustomException(file_name='{self.file_name!r}', line_number={self.line_number}, error_message='{self.error_message!r}')"
    
if __name__ == "__main__":
    try:
        a = 1 / 0
    except Exception as e:
        raise CustomException("An error occurred while performing division.", e) from e