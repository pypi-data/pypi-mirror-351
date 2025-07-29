import traceback


def serialize_exception(exception: BaseException) -> dict:
    return {
        "errorMessage": str(exception),
        "traceBack": traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ),
    }
