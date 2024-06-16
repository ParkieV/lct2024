from datetime import datetime
from genericpath import exists
import logging
import logging.config
import os


_DEFAULT_LOGGING = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': "%(asctime)s - %(levelname)s(%(pathname)s. %(funcName)s(%(lineno)d)) - %(message)s"},
    },
    'handlers': {
        'debuges':     {'class': "app.shared.logger_handlers.DebugLoggerHandler",
                     'formatter': "standard",
                     'level': 'DEBUG',
                     'filename': "../logs/debuges/{}.log".format(str(datetime.now().strftime("%d-%m-%Y"))),
                     'mode': 'a'
                     },
        'defaults':     {'class': "app.shared.logger_handlers.DefaultLoggerHandler",
                     'formatter': "standard",
                     'level': 'INFO',
                     'filename': "../logs/defaults/{}.log".format(str(datetime.now().strftime("%d-%m-%Y"))),
                     'mode': 'a'
                     },
        'errors':     {'class': "app.shared.logger_handlers.ErrorLoggerHandler",
                     'formatter': "standard",
                     'level': 'ERROR',
                     'filename': "../logs/errors/{}.log".format(str(datetime.now().strftime("%d-%m-%Y"))),
                     'mode': 'a'
                     },
        'criticals':     {'class': "app.shared.logger_handlers.CriticalLoggerHandler",
                     'formatter': "standard",
                     'level': 'CRITICAL',
                     'filename': "../logs/criticals/{}.log".format(str(datetime.now().strftime("%d-%m-%Y"))),
                     'mode': 'a'
                     },
    },
    'loggers': {
        __name__:   {'level': 'DEBUG',
                     'handlers': ['debuges', 'defaults', 'errors', 'criticals'],
                     'propagate': False },
    }
}

if not exists(os.path.abspath('../logs')):
    os.makedirs(os.path.abspath('../logs'))
for handler in _DEFAULT_LOGGING['handlers'].keys():
    if not exists(f"{os.path.abspath('../logs')}/{handler}"):
        os.makedirs(f"{os.path.abspath('../logs')}/{handler}")
    _DEFAULT_LOGGING['handlers'][handler]['mode'] = 'a+'
logging.config.dictConfig(_DEFAULT_LOGGING)
logger = logging.getLogger(__name__)
