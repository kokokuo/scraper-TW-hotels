from settings.config import Config
from infra.logging import scraping_logger
from .header import FakeHeaderGenerator
from .requester import RetryableRequester

fake_header_generator = FakeHeaderGenerator(scraping_logger)
retryable_requester = RetryableRequester(scraping_logger, Config.ABNORMAL_URL)
