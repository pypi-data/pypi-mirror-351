import logging
from datetime import datetime
from http import HTTPStatus
from qtools.writing import Fg, Style, Screen

def get_status_phrase(status_code):
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Unknown Status Code"

class CustomFormatter(logging.Formatter):
    def __init__(self, tz, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_message = None
        self.count = 0
        self.tz = tz
    
    def format(self, record):
        message = record.msg
        if record.msg=="REQUEST-LOG":
            message = f"{record.levelname} \"{record.method} {record.path}\" Status: [{record.status_code}] {get_status_phrase(record.status_code)}"
            
        if message == self.last_message:
            self.count += 1
        else:
            self.last_message = message
            self.count = 1
            
        if self.count > 1:
            return Screen.clearline+self.finalize(f"{message} [x{self.count}]", record)
            
        return self.finalize(message, record)
    
    def finalize(self, message, record):
        message = f"{datetime.fromtimestamp(record.created, self.tz).strftime('%H:%M:%S')} {message}"
        match record.levelno:
            case logging.INFO:
                return f"{Fg.green}{message}{Style.resetall}"
            case logging.WARNING:
                return f"{Fg.yellow}{message}{Style.resetall}"
            case logging.ERROR:
                return f"{Fg.red}{message}{Style.resetall}"
            case logging.CRITICAL:
                return f"{Fg.magenta}{message}{Style.resetall}"
            case _:
                return f"{Fg.blue}{message}{Style.resetall}"

def setup_logger(name: str, local_tz=datetime.now().astimezone().tzinfo):
    logger = logging.getLogger(name,)
    handler = logging.StreamHandler()
    formatter = CustomFormatter(tz=local_tz)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    class ForwardingHandler(logging.Handler):
        def emit(self, record):
            logger.log(record.levelno, f'WEB SERVER GATEWAY {record.getMessage()}')

    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    werkzeug_handler = ForwardingHandler()
    werkzeug_logger.addHandler(werkzeug_handler)
    return logger