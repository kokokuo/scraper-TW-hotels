import os
from .factory import LoggerFactory


proj_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
logging_conf = os.path.abspath(os.path.join(proj_path, 'logging.conf.yml'))

factory = LoggerFactory()
factory.load_config(logging_conf)
scraping_logger = factory.get_logger("hotel_scraping")
