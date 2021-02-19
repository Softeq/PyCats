import logging

from .mobile_element import MobileElement
from .utils import get_platform

logger = logging.getLogger(__name__)


class MobileSwitch(MobileElement):

    # region Actions

    def set_switcher_state(self, checked: bool = True):
        """
        Changes Switch state
        :param checked: if True sets switch to Checked, otherwise sets switch to Unchecked
        """
        is_element_checked = self.is_checked()
        logger.info("Switch status is - {}".format(is_element_checked))
        if is_element_checked != checked:
            self.click()

    # endregion

    # region Checks

    def is_checked(self) -> bool:
        """ Get switch state (checked / not checked) """
        attribute = 'checked' if get_platform() == 'Android' else 'value'
        result = 'false' if get_platform() == 'Android' else '0'

        return not(self.get_attribute(attribute) == result)
    # endregion
