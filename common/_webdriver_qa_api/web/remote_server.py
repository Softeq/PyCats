import os
import logging
import time

import requests

from common.config_manager import ConfigManager
from common._libs.helpers.os_helpers import get_platform_type
from common._shell_qa_api.subprocess_command import subprocess_send_command_asynchronous, subprocess_send_command

logger = logging.getLogger(__name__)


class BaseRemoteServer:

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.platform_name = get_platform_type()
        self.is_linux = self.platform_name in ("Darwin", "Linux")

    def stop_server(self):
        """
        Stop remote server process (depending on the platform)
        """
        logger.info(f"stop webdriver server on {self.address}:{self.port}")
        if not self._get_current_sessions():
            if self.is_linux:
                cmd = f"lsof -ti:{self.port} | xargs kill"
            else:
                cmd = f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr \":{self.port}\"') do taskkill /F /PID %a"
            subprocess_send_command(cmd)

    def _get_current_sessions(self):
        try:
            response = requests.get(f"http://{self.address}:{self.port}/wd/hub/sessions")
        except requests.exceptions.ConnectionError:
            return False
        return response.json()["value"]


class SeleniumServer(BaseRemoteServer):

    def __init__(self, config: ConfigManager, address='127.0.0.1', port=4444, log_path="Logs"):
        super().__init__(address, port)
        self._config = config.get_webdriver_settings()
        self.log = os.path.join(log_path, 'selenium.log')

    def start_server(self):
        """
        Start webdriver remote server process (for web testing)
        """
        logger.info(f"Start Selenium Server - {self.address}:{self.port}")
        if os.path.exists(self.log):
            os.remove(self.log)

        if self._get_current_sessions() is False:
            server_cmd = list()
            server_cmd.append('java')
            server_cmd.append(f'-Dwebdriver.{self._config.browser}.driver="{self._config.driver_path}"')
            server_cmd.append(f'-jar "{self._config.selenium_server_executable}"')
            server_cmd.append(f'-port {self.port}')
            server_cmd.append(f'-log "{self.log}"')
            subprocess_send_command_asynchronous(' '.join(server_cmd))
            time.sleep(4)
            try:
                self.is_local_server_running()
            except AssertionError:
                logger.exception(f'Could not start Selenium Server. Please check log: {self.log}')
                raise
        else:
            logger.info("Selenium Server already running, trying to connect to it")

    def is_local_server_running(self):
        """
        Try to get process info and return True if port now used.
        """
        if self.is_linux:
            cmd = f"lsof -i -n -P | grep {self.port}"
        else:
            cmd = f"netstat -na | find \"{self.port}\""
        out, err, rc = subprocess_send_command(cmd)
        return True if out[0] and ('LISTENING' or 'java') in out[0] else False
