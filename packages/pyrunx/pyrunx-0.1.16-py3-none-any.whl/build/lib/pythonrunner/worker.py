import logging
import requests


class Worker:
    def __init__(self, config: dict = None):
        self.logger = logging.getLogger("main")
        self.config = config or {}

    def debug(self, msg: str):
        self.logger.debug(f"[{self.__class__.__name__}] {msg}")

    def info(self, msg: str):
        self.logger.info(f"[{self.__class__.__name__}] {msg}")

    def warning(self, msg: str):
        self.logger.warning(f"[{self.__class__.__name__}] {msg}")

    def error(self, msg: str):
        self.logger.error(f"[{self.__class__.__name__}] {msg}")

    def http_post(self, url: str, data: dict):
        if not url:
            self.error("No URL provided")
            return
        try:
            response = requests.post(url, json=data, timeout=5)
            if response.status_code != 204:
                self.error(
                    f"Error while sending POST request: "
                    f"{response.status_code} - {response.text}"
                )
        except Exception as e:
            self.error(f"Exception while sending the message: {e}")
