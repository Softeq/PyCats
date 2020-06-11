import os
import platform
import time

import requests

from common.shell_qa_api.subprocess_command import subprocess_send_command_asynchronous, subprocess_send_command
from common.scaf import get_logger, config, logger

log = get_logger(__name__)


class BaseRemoteServer:

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def stop_server(self):
        """
        Stop remote server process (depending on the platform)
        """
        log.info(f"stop webdriver server on {self.address}:{self.port}")
        if not self._get_current_sessions():
            platform_name = platform.system()
            if platform_name in ("Darwin", "Linux"):
                cmd = f"lsof -ti:{self.port} | xargs kill"
            elif platform_name == "Windows":
                cmd = f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr \":{self.port}\"') do taskkill /F /PID %a"
            else:
                raise EnvironmentError("unknown os")
            subprocess_send_command(cmd)

    def _get_current_sessions(self):
        try:
            response = requests.get(f"http://{self.address}:{self.port}/wd/hub/sessions")
        except requests.exceptions.ConnectionError:
            return False
        return response.json()["value"]


class SeleniumServer(BaseRemoteServer):

    def __init__(self, address='127.0.0.1', port=4444, browser=config.web_settings.browser, log_path=None):
        super().__init__(address, port)

        self.browser = browser
        self.log = os.path.join(log_path if log_path else logger.base_log_path, 'selenium.log')

    def start_server(self):
        """
        Start webdriver remote server process (for web testing)
        """
        log.info(f"Start Selenium Server - {self.address}:{self.port}")
        if os.path.exists(self.log):
            os.remove(self.log)

        if self._get_current_sessions() is False:
            server_cmd = list()
            server_cmd.append('java')
            server_cmd.append(f'-Dwebdriver.{self.browser}.driver="{config.web_settings.get_driver_path()}"')
            server_cmd.append(f'-jar "{config.web_settings.selenium_server_executable}"')
            server_cmd.append(f'-port {self.port}')
            server_cmd.append(f'-log "{self.log}"')
            subprocess_send_command_asynchronous(' '.join(server_cmd))
            time.sleep(4)
            try:
                self.is_local_server_running()
            except AssertionError:
                log.exception(f'Could not start Selenium Server. Please check log: {self.log}')
                raise
        else:
            log.info("Selenium Server already running, trying to connect to it")

    def is_local_server_running(self):
        """
        Try to get process info and return True if port now used.
        """
        cmd = f"lsof -i -n -P | grep {self.port}"
        out, err, rc = subprocess_send_command(cmd)
        return True if out[0] and 'java' in out[0] else False
