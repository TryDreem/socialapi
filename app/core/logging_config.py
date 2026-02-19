import logging
import sys

def setup_logging():
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(funcName)s:%(lineno)d | %(message)s"
    )

    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    #handler for console
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)

    #root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)


    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")