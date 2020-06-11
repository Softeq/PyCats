from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from common import scaf

logger = scaf.get_logger(__name__)


class DynamicElement:
    def __init__(self, locator_type, locator, driver, name=None, parent=None):
        self.__driver = driver
        self.__locator_type = locator_type
        self.__locator = locator
        self.__name = locator if name is None else name
        self.__parent = parent

    @property
    def name(self):
        return self.__name

    @property
    def selenium_element(self):
        if self.__parent is None:
            try:
                logger.info(f"Looking for element {self.__locator}")
                return self.__driver.find_element(self.__locator_type, self.__locator)
            except NoSuchElementException:
                logger.exception("An element '{0}' {1}could not be located on the page.".format(
                    self.__name, "" if self.__locator == self.__name else "with locator '{}' ".format(self.__locator)))
        else:
            try:
                return self.__parent().find_element(self.__locator_type, self.__locator)
            except NoSuchElementException:
                logger.exception("An element '{0}' {1}for __parent '{2}' could not be located on the page.".format(
                    self.__name, "" if self.__locator == self.__name else "with locator '{}' ".format(self.__locator),
                    self.__parent.name))

    def __log(self, item, attribute):
        name = object.__getattribute__(self, "name")

        if callable(attribute):
            logger.info(f"Call method {item} in element {name}")
        else:
            logger.info(f"get attribute {item} in element {name}")

    def __call__(self):
        return self.selenium_element

    def __getattribute__(self, item):
        attribute = object.__getattribute__(self, item)

        if "_DynamicElement__" not in item:
            object.__getattribute__(self, "_DynamicElement__log")(
                item, attribute)
            logger.info(f"attribute getattribute {attribute} {item}")
        return attribute

    def __getattr__(self, item):
        try:
            attribute = getattr(self.selenium_element, item)
        except StaleElementReferenceException:
            attribute = getattr(self.selenium_element, item)
        object.__getattribute__(self, "_DynamicElement__log")(item, attribute)
        logger.info(f"attribute getattr {attribute}")
        return attribute


class DynamicElements(DynamicElement):
    def __init__(self, locator_type, locator, driver, name=None,
                 parent=None):
        self.parent = parent
        self.driver = driver
        self.locator_type = locator_type
        self.locator = locator
        super().__init__(locator_type, locator, driver, name=name,
                         parent=parent)

    @property
    def selenium_element(self):
        if self.parent is None:
            return self.driver.find_elements(self.locator_type, self.locator)
        else:
            return self.parent().find_elements(self.locator_type, self.locator)
