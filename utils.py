from enum import Enum
import traceback


class ERROR_CODES(Enum):
    DB_ERROR = "DB_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


def return_on_failure(value, logger):
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args,**kwargs)
            except Exception as e:
                logger.error(e)
                return value
        return applicator
    return decorate
    