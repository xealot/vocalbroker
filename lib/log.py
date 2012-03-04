from logging import config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        },
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers':['console'],
        'level':'DEBUG',
    },
    'loggers': {
        'MODULENAME': {
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        },
    }
}

config.dictConfig(LOGGING)