import logging
import os
import re
import subprocess

from time import sleep
from typing import Union, Optional
from appium.webdriver.connectiontype import ConnectionType

from common._webdriver_qa_api.mobile.mobile_driver import get_mobile_driver_session

logger = logging.getLogger(__name__)

# todo: should be updated for ios platform - bundle id and move to methods
APP_BUNDLE_ID = None


def background_app(seconds: Union[int, float] = -1):
    """
    Background app for a {} seconds and open again
    :param seconds: time to background app in seconds
    """
    logger.info("Background app for a {} seconds".format(seconds))
    get_mobile_driver_session().driver.background_app(seconds)


def awake_android():
    """
    Wakes up the device. Behaves somewhat like KEYCODE_POWER but it has no effect if the device is already awake.
    Will be ignored for iOS platform
    """
    if get_platform() == 'Android':
        get_mobile_driver_session().driver.press_keycode(224)


def lock_device(seconds: Optional[int] = None):
    """
    Lock device for a {seconds} seconds, device will be unlocked automatically after timeout.
    :param seconds: time to lock device in seconds, will be locked forever if value is None or equal/less than zero
    """
    logger.info("Lock device")
    get_mobile_driver_session().driver.lock(seconds=seconds)


def unlock_device():
    """
    Unlock the device. No changes are made if the device is already locked.
     Will be ignored for iOS platform
    """
    if get_platform() == 'Android':
        logger.info("Unlock device")
        get_mobile_driver_session().driver.unlock()


def launch_app():
    """
    Activates the application if it is not running or is running in the background.
    """
    session = get_mobile_driver_session().driver

    logger.info("Launch app from desired capabilities on device")

    if get_platform() == 'iOS':
        session.execute_script('mobile: launchApp', {'bundleId': APP_BUNDLE_ID})
    else:
        app_package = session.desired_capabilities["appPackage"]
        awake_android()
        session.activate_app(app_id=app_package)


def get_platform() -> str:
    """ Return actual platform from WebDriver session """
    return get_mobile_driver_session().driver.desired_capabilities['platformName']


def close_app():
    """ Close the application if it is running. """
    logger.info("Stop app from desired capabilities on device")
    if get_platform() == 'iOS':
        get_mobile_driver_session().driver.terminate_app(app_id=APP_BUNDLE_ID)
    else:
        get_mobile_driver_session().driver.close_app()


def launch_previous_app_from_background():
    """ Switch to previous launched active app """
    if get_mobile_driver_session().driver:
        logger.info("open previous launched app")
        get_mobile_driver_session().driver.press_keycode(187)
        sleep(1)
        get_mobile_driver_session().driver.press_keycode(187)


def get_android_wlan_data() -> str:
    """ Get wlan ssid for android device """
    cmd = "adb -s {} shell dumpsys netstats | grep -E 'iface=wlan'".format(os.environ["android_device"])
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    result_output = result.stdout.decode('utf-8')
    ssid_list = re.findall(r'\"(.+?)\"', result_output)
    return ssid_list[0] if len(ssid_list) > 0 else None


def turn_off_wlan():
    """ Disable wlan on mobile device """
    logger.info("Turn off wlan on mobile device")
    network_connection = get_mobile_driver_session().driver.network_connection
    if network_connection not in (ConnectionType.NO_CONNECTION, ConnectionType.AIRPLANE_MODE):
        get_mobile_driver_session().driver.set_network_connection(ConnectionType.NO_CONNECTION)


def turn_on_wlan():
    """ Enable wlan on mobile device """
    logger.info("Turn on wlan on mobile device")
    network_connection = get_mobile_driver_session().driver.network_connection
    if network_connection not in (ConnectionType.WIFI_ONLY, ConnectionType.ALL_NETWORK_ON):
        get_mobile_driver_session().driver.set_network_connection(ConnectionType.WIFI_ONLY)
