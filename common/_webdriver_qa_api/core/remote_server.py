import os
import logging
import time
import requests

from common._libs.helpers.os_helpers import get_platform_type
from common._shell_qa_api.subprocess_command import subprocess_send_command_asynchronous, subprocess_send_command
from common.config_parser.config_dto import WebDriverSettingsDTO, MobileDriverSettingsDTO

logger = logging.getLogger(__name__)


class BaseRemoteServer:

    def __init__(self, address, port, server_type):
        self.address = address
        self.port = port
        self.server_type = server_type
        self.platform_name = get_platform_type()
        self.is_linux = self.platform_name in ("Darwin", "Linux")

    def stop_server(self):
        """
        Stop remote server process (depending on the platform)
        """
        logger.info(f"stop {self.server_type} server on {self.address}:{self.port}")
        for _ in range(5):
            if self._is_session_exist() is False:
                time.sleep(2)

        if self._is_session_exist() is False:
            if self.is_linux:
                cmd = f"lsof -i:{self.port} | grep LISTEN | awk '{{print $2}}' | xargs kill"
            else:
                cmd = f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr \":{self.port}\"') do taskkill /F /PID %a"
            subprocess_send_command(cmd)
        else:
            logger.info(f"The {self.server_type} server was not stopped because an active session was found")

    def _is_session_exist(self):
        try:
            response = requests.get(f"http://{self.address}:{self.port}/wd/hub/sessions")
        except requests.exceptions.ConnectionError:
            return False
        return True if len(response.json()["value"]) > 0 else False


class AppiumRemoteServer(BaseRemoteServer):

    def __init__(self, config: MobileDriverSettingsDTO, address: str = '127.0.0.1',
                 port: int = 4723, log_path: str = "Logs"):
        super().__init__(address, port, server_type="Appium")
        self._config = config
        self.log = os.path.join(log_path, 'appium.log')

    def start_server(self):
        """
        Start appium remote server process (for mobile testing)
        """
        logger.info(f"Start Appium Server - {self.address}:{self.port}")
        if self.is_local_server_running() is False:
            server_cmd = list()
            server_cmd.append(self._config.node_executable_path)
            server_cmd.append(self._config.appium_server_path)
            server_cmd.append(f'--address {self.address}')
            server_cmd.append(f'--port {self.port}')
            server_cmd.append(f'--log "{self.log}"')

            subprocess_send_command_asynchronous(' '.join(server_cmd))
            time.sleep(20)

            try:
                self.is_local_server_running()
            except AssertionError:
                logger.exception(f'Could not start Appium Server. Please check log: {self.log}')
                raise
        else:
            logger.info("Appium Server already running, trying to connect to it")

    def is_local_server_running(self):
        """
        Try to get process info and return True if port now used.
        """
        if self.is_linux:
            cmd = f"lsof -i -P | grep '{self.port} (LISTEN)'"
        else:
            # todo: try on windows (and modify cmd if needed)
            cmd = f"netstat -na | find \"{self.port}\""
        out, err, rc = subprocess_send_command(cmd, exp_rc=None)
        return bool(out[0] and 'node' in out[0])


class SeleniumServer(BaseRemoteServer):

    def __init__(self, config: WebDriverSettingsDTO, address: str = '127.0.0.1',
                 port: int = 4444, log_path: str = "Logs"):
        super().__init__(address, port, server_type="Selenium")
        self._config = config
        self.log = os.path.join(log_path, 'selenium.log')

    def stop_server(self):
        if self._config.stop_server is True:
            super().stop_server()
        else:
            logger.info("Skip stopping server due to config value")

    def start_server(self):
        """
        Start webdriver remote server process (for web testing)
        """
        logger.info(f"Start Selenium Server - {self.address}:{self.port}")
        if os.path.exists(self.log):
            os.remove(self.log)

        if self.is_local_server_running() is False:
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
            cmd = f"lsof -i -P | grep {self.port}"
        else:
            cmd = f"netstat -na | find \"{self.port}\""
        out, err, rc = subprocess_send_command(cmd, exp_rc=None)
        return True if out[0] and ('LISTENING' or 'java') in out[0] else False
