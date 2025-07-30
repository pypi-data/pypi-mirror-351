import logging
import logging.config
import sys


class SmartFormatter(logging.Formatter):
    """Custom formatter that applies different formats based on logger name"""

    def __init__(self):
        # Define formats for different loggers
        self.formatters = {
            'detailed': logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d]%(message)s'),
            'simple': logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]%(message)s'),
        }

    def format(self, record):
        # Use detailed format for ci_agents and tests, simple for others
        if record.name.startswith('ci_agents'):
            return self.formatters['detailed'].format(record)
        else:
            return self.formatters['simple'].format(record)


# Logging configuration for the SDK
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'smart': {
            '()': SmartFormatter,
        }
    },
    'handlers': {
        'console_unified': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'smart',
            'stream': sys.stdout
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console_unified']
    },
    'loggers': {
        # Unified CI Agents SDK - use detailed format
        'ci_agents': {
            'handlers': ['console_unified'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # OpenAI agents logger - use simple format  
        'openai.agents': {
            'handlers': ['console_unified'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Global logger for the entire SDK - import this instead of creating new loggers
logger = logging.getLogger("ci_agents")


def configure_root_logger():
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info("Logging configured for SDK")
