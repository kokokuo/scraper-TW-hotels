# -*- coding: utf-8 -*-
import os
import logging
import logging.config
from logging import Logger
from http import HTTPStatus
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from . import loader


class LoggerFactory(object):
    def __init__(self):
        self._format_loader = {
            '.yml': loader.YamlLoader,
            '.json': loader.JsonLoader}

    def __str__(self):
        for name in logging.Logger.manager.loggerDict:
            print('logger name:', name, ', handlers:',
                  logging.getLogger(name).handlers)
        return 'Done'

    @property
    def show_loggers(self):
        """
        取得製作好的 Logger 名稱
        Returns:
        """
        return logging.Logger.manager.loggerDict

    def _set_formatter(self, source, level, format):
        """
        設定 handler 的 formatter
        Args:
            source (handler): 來自 logging 或 logging.handlers 底下的處理器
            level(int): 回報的等級
            format(str): 格式化的設定
        Return:
            source: 回傳設定好的 handler
        """
        source.setLevel(level)
        formatter = logging.Formatter(format)
        source.setFormatter(formatter)
        return source

    def _check_extension(self, path: str):
        support_extension = ['.yml', '.json']
        for extension in support_extension:
            if path.endswith(extension):
                return extension
        raise Exception('Non-Support Format')

    def _check_logging_path_dir(self, content: dict):
        handlers = content["handlers"]
        for name, settings in handlers.items():
            if "filename" in settings.keys():
                pathdir = os.path.dirname(settings["filename"])
                if not os.path.exists(pathdir):
                    os.makedirs(pathdir)

    def load_config(self, path: str) -> None:
        """
        載入已經地義好的 Logger 設定檔，並載入初始化。
        支援 json 與 yaml 格式，
        Args:
            path (str): 檔案來源位置
        Raises:
            Exception: 載入失敗
        """

        try:
            ext = self._check_extension(path)
            content = self._format_loader[ext].load(path)
            # 檢查載入的 yaml 字典格式中的所有 filename 有無路徑
            self._check_logging_path_dir(content)
            logging.config.dictConfig(content)
        except Exception as err:
            raise Exception('Load Failure :' + repr(err))

    def get_logger(self, name: str) -> Logger:
        return logging.getLogger(name)

    def make_console(self, name, level, format) -> Logger:
        logger = logging.getLogger(name)
        if logging.StreamHandler not in logger.handlers:
            # 建立預設的 StreamHandler ，此時在 logger.handlers 中便會建立
            handler = logging.StreamHandler()
            handler = self._set_formatter(handler, level, format)
            logger.addHandler(handler)
        return logger

    def make_file(self, name, filepath, level, format):
        logger = logging.getLogger(name)
        if logging.FileHandler not in logger.handlers:
            handler = logging.FileHandler(filepath)
            handler = self._set_formatter(handler, level, format)
            logger.addHandler(handler)
        return logger

    def make_rotating_file(self,
                           name,
                           filepath,
                           level,
                           format,
                           max_bytes=128,
                           backup_count=0) -> Logger:
        """
        透過 addHandler 的方式，建立 建立 RotatingFileHandler
        判斷是否有 RotatingFileHandler Logger 已經建立，有的話則直接回傳
        Args:
            max_bytes(int, optional): 檔案最大可寫入到多少 bytes。
                如果沒有搭配 backup_count 設定，便不會有作用，在同一份檔案一直 append 寫入下去。
                e.g backup = 2, 那麼表示除了 original 外，除了
            backup_count(int, optional): 可以寫入的備份檔案數量 e.g backup = 2, 那麼表示除了 original 外，當 size 不夠時，可以產生 file.1 與 file.2。

            如果 max_bytes 有搭配 backup_count >=1 ，那麼當該檔案超過 max_bytes 時，便會依照建立 backup_count 的數量，
            e.g backup_count = 2, max_byte = 18, 要寫入 log 有 3 筆，分別是 18 bytes 共 54 bytes ，則除了 original 外，會依序因為每份 file 的 max_bytes 只到 18 bytes
            依序建立了 file.1, file.2 。

            但是，如果 log 的內容很多，backup 也不夠用時，便會重新再以正本覆蓋寫入, 如此一直反覆，如下
            e.g backup_count = 2, max_byte = 18, 要寫入 log 有 5 筆，分別是 18 bytes 共 90 bytes, 則
            第 1 筆 18 bytes -> original
            第 2 筆 18 bytes -> file.1
            第 3 筆 18 bytes -> file.2
            第 4 筆 18 bytes -> 因為只能建立 backup = 2, 所以回到 original 覆蓋寫入
            第 5 筆 18 bytes -> file.1

            最後會看到， original 的 資料是第 4 筆 log, file.1 是第 5 筆, 而 file.2 則是第 3 筆
        Returns:
            Logger: 回傳 logger 物件
        """
        logger = logging.getLogger(name)
        if RotatingFileHandler not in logger.handlers:
            handler = RotatingFileHandler(
                filepath,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf8')
            handler = self._set_formatter(handler, level, format)
            logger.addHandler(handler)
        return logger

    def make_time_rotating_file(self,
                                name,
                                filepath,
                                level,
                                format,
                                backup_count=0,
                                when='s',
                                interval=60) -> Logger:
        """
        透過 addHandler 的方式，建立 建立 TimeRotatingFileHandler
        判斷是否有 TimeRotatingFileHandler Logger 已經建立，有的話則直接回傳
        Args:
            backup_count(int, optional): 可以寫入的備份檔案數量
            when(string, optional): 何時建立新的檔案，可以建立的單位如下
                S: 秒, M: 分, H: 時, D: 日, W:  W0 - W6 (表示星期幾 0=Monday), midnight: 午夜 midnight
                保存日誌時，會以 %Y-%m-%d_%H-%M-%S 格式保存
            interval(int, optional): 時間間隔，搭配 when, 例如 when = s, interval = 30
                表示每格 30 秒, 如果在 backup_count 允許的數量內，寫入新的日誌檔。
                而如果當 when = w 時， interval = 0 - 6 分別表示星期幾, 但如果 when = w0 - w6 時, interval 便不作用 。
            如同 RotatingFileHandler，如果新的資料超過 backup_count 的量時，就會回到一開始檔案並覆蓋，並依序重新產生新的檔案
        Returns:
            Logger: 回傳 logger 物件
        """
        logger = logging.getLogger(name)
        if TimedRotatingFileHandler not in logger.handlers:
            handler = TimedRotatingFileHandler(
                filepath,
                when=when,
                interval=interval,
                backupCount=backup_count,
                encoding='utf8')
            handler = self._set_formatter(handler, level, format)
            logger.addHandler(handler)
        return logger
