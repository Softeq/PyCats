from appium.webdriver.common.mobileby import MobileBy

from common._webdriver_qa_api.mobile.mobile_element import MobileElement
from common._webdriver_qa_api.mobile.mobile_page import MobilePage


class LocationPermissionAndroid(MobilePage):
    def __init__(self, should_present=True):
        super().__init__(locator_type=MobileBy.XPATH,
                         locator='//android.widget.TextView[@text="Allow Weather to access this device\'s location?"]',
                         name='Location Permission Confirmation',
                         should_present=should_present)
        self.btn_allow = MobileElement(MobileBy.ID, 'com.android.permissioncontroller:id/'
                                                    'permission_allow_always_button')
        self.btn_deny = MobileElement(MobileBy.ID, 'com.android.permissioncontroller:id/permission_deny_button')

    def allow(self):
        """ Click Allow button  """
        self.btn_allow.click()

    def deny(self):
        """ Click Deny button """
        self.btn_deny.click()
