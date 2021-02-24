# project - Web application

The part contains sample of web UI automation sources and tests

Web tests based on UI interactions using Selenium WebDriver and rest API endpoint from common framework Part:

* Wrapper under WebDriver tool from core layer - [webdriver](../../common/_webdriver_qa_api/web)
* Rest API endpoints - [api_steps](../api/steps)

## code structure

We support 3 layers structure for code base:

* Builder layer - implementation of Page Object pattern
* Steps layer - steps functions that used from tests
* Tests layer - tests functions


## Development practices:

### Builder layer
 Implementation of Page object pattern based on Page classes (For each web page we have separate class).
 This layer describes web interface and Actions that we can do using web interface.
 
 That layer placed in `pages` directory, e.g. for Home Page - [home_page.py](pages/home_page.py).
 
The Page object implementation should include following rules:

1. The page class must inherit from [WebPage](../../common/_webdriver_qa_api/web/web_pages.py) class and implement `super` call for `__init__` method
1. All page elements should be defined in `__init__` method as [WebElement](../../common/_webdriver_qa_api/web/web_elements.py) related objects
1. All elements variable names starts with element type shortcut: button - `seld.btn_name`, text_box - `self.txb_name` etc
1. Class methods should implement only actions on the page using elements from `__init__` section by `self.` call and methods from `WebElement` / `WebPage` classes

sample of Page class:
```python
from common._webdriver_qa_api.web.web_pages import WebPage
from selenium.webdriver.common.by import By
from common._webdriver_qa_api.web.web_elements import WebElement


class HomePage(WebPage):

    def __init__(self):
        super().__init__(By.ID, "myTab", "Account Home Page")
        self.lnk_api_keys = WebElement(By.XPATH, "//li/a[@href='/api_keys']")
        self.lbl_api_key = WebElement(By.XPATH, "//table//pre")

    def click_api_keys_menu(self):
        self.lnk_api_keys.click()
```

### Steps layer
Steps layer - it's a function set which combine Action methods from Builder layer and expands them with test checks.
This solution help us to have clear structure of tests and avoid code duplication (save time on test supporting)

 That layer placed in `steps` directory and divided to 3 main parts:
* [navigation](steps/navigation) - function that used for navigation between web pages
* [page steps](steps/page_object_steps/pages) - steps related with Pages, based on classes that inherit from Page Object classes
* [global steps](steps/global_steps) - functions that combine many actions for frequent uses (like login)


The `navigation` keywords should include following rules:

1. Navigation function combine actions from: another steps, PO classes, checks
1. Should return an object of PageStep class
1. Have a log_title message with action message
1. Function should be added to `__all__` module list 

sample of navigation method:
```python
from common._webdriver_qa_api.web.web_driver import navigate_to
from common.facade import logger, raw_config
from sample import web

__all__ = ['navigate_to_sign_in_page']


def navigate_to_sign_in_page():
    logger.log_title(f"Navigate to Sign in page")
    navigate_to(raw_config.project_settings.web_app_url)

    main_steps = web.pages.MainPageSteps()
    main_steps.click_sign_in()
    return web.pages.SignInSteps()
```


The `page steps` keywords should include following rules:

1. The step class must inherit from PO class for same page (e.g. if you have HomePage on PO layer, steps class will be - `class HomePageSteps(HomePage)`)
1. Step class haven't `__init__` section or have a super call of `__init__` from PO class
1. Class methods should implement steps related with inherited page using: actions from Page class, checks, additional object from Builder layer (e.g. popup's)
1. Python module should be added to `__all__` variable in `__init__.py` file of pages or subdirectory (e.g. [\_\_init__.py`](steps/page_object_steps/pages/__init__.py))

sample of page steps implementation:
```python
from common.facade import logger
from sample.web.pages.home_page import HomePage


class HomePageSteps(HomePage):

    def get_api_key(self):
        logger.log_title("Get REST API key")
        self.click_api_keys_menu()
        return self.lbl_api_key.text
```


The `global steps` keywords should include following rules:

1. Function combine actions from: another steps, page steps classes, checks
1. Have a log_title call with action message
1. Function should be added to `__all__` module list 

sample of steps method:
```python
# TBU
```

#### Test layer
Test layer include python modules with tests and pytest fixtures.

That layer placed in `tests` directory that can include subdirectories and modules by test types or target,
 e.g. for Sign In page - [tests for sign in page](../tests/web_tests/test_sign_in_page.py)

there are a few rules that we hold:

1. Test module name should starts from `test_`
1. Test Class name should starts from `Test`
1. Test function should starts from `test`
1. Create test Classes to organize logical test suites and implement flexible mechanism of fixtures
1. Place fixtures in `conftest.py` on test layer when this fixture can be reused from different packages, modules
1. Place fixture in local python test module/conftest file when fixture used by single test/module
1. Tests function use actions from: keyword layer calls (page steps, global steps, navigation steps)
 
Code sample:
```python
import pytest

from common.facade import logger
from sample import web


@pytest.mark.usefixtures('open_main_page')
class TestSignIn:
    """ Weather - sign in to account tests """

    def test_sign_in_page_displayed(self):
        """ Recover account button transaction """
        logger.log_step("Open sign in page", precondition=True)
        sign_in_page = web.navigation_steps.navigate_to_sign_in_page()

        logger.log_step("Verify default elements on the page")
        sign_in_page.verify_default_elements()
```