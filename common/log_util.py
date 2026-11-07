import logging
import os
from datetime import datetime

LOG_DIR = 'logs'

def get_logger(name: str = "api_auto")->logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:  #存放输出管道的列表
        return logger

    os.makedirs(LOG_DIR, exist_ok=True)
    log_file= os.path.join(LOG_DIR,f"{datetime.now().strftime('%Y%m%d')}.log")
    file_handler= logging.FileHandler(log_file,encoding="utf-8")
    formatter= logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                                 datefmt="%Y-%m-%d %H:%M:%S",
                                 )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger= get_logger()

