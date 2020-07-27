# PyCats (Python Common Automation Test Solution)
The PyCats aims to provide the well-structured framework with libraries created based on the popular python solutions intended for testing purposes and to make it universal for testing across different domain areas - Web, Mobile, IoT, Embedded.

It uses the [pytest](https://docs.pytest.org/en/latest/ "pytest") library as a test runner, [Selenium Web Driver](https://www.selenium.dev/projects/ "Selenium Web Driver") for Web UI testing, [Appium](http://appium.io/ "Appium") for mobile testing (Coming Soon), contains wrappers over the Web Driver to simplify its usage, provides layered architecture and recommendations how to organize tests.

## Getting Started

TBU

### Requirements

The minimal python version is 3.7

To enable Web UI testing, need to download Web drivers for your browsers versions and provide their names and path to the directory via a configuration file or command-line interface:

[Chrome Drivers](https://chromedriver.chromium.org/downloads "Chrome Drivers")
[Firefox Drivers](https://github.com/mozilla/geckodriver/releases "Firefox Drivers")
[Microsof Edge](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/ "Microsoft Edge")
Safari Drivers are delivered together with browser

PyCats uses WebDriver's RemoteDriver to be able to run a browser remotely. You need to download [selenium server](https://www.selenium.dev/downloads/ "selenium server") and provide its path in the configuration file.


### Installation

To install the required packages, download GitHub project and execute the following command in the root project's directory:

```bash
pip3 install -r requirements.txt
```

### Configuration
Prepare the config file `config.ini` in config directory of PyCats:

Example of `config.ini`:
```
[global]
logdir = Logs
log_level = DEBUG
enable_libs_logging = True
sections = api web

[api]
api_url = http://api.openweathermap.org/data/2.5/

[api_validation]
validate_status_code = True
validate_headers = True
validate_body = True
validate_is_field_missing = True

[web]
app_url = https://openweathermap.org/
webdriver_folder = /home/test/web/webdrivers/
webdriver_default_wait_time = 20
webdriver_implicit_wait_time = 60
selenium_server_executable = /home/test/web/webdrivers/selenium-server-standalone-3.141.59.jar
chrome_driver_name = chromedriver
firefox_driver_name = gecodriver
browser = chrome
```

The mandatory settings for `global` section are:

- `logdir = Logs` - path to folder to keep the log files. Folder will be created if if does not exist
- `sections = api web` - space-separated list of section to enable during config parsing. If you do not want to use API - leave only web, the same for other sections.

for `api` section:

- `api_url = http://api.openweathermap.org/data/2.5/` - URL to API to use in API project

for `web` section:

- `app_url = https://openweathermap.org/` - URL to Web Site to use in WEB project
- `webdriver_folder = /home/test/web/webdrivers/` - Folder where browsers drivers are located
- `chrome_driver_name = chromedriver` - Chrome driver filename
- `firefox_driver_name = gecodriver` - Firefox driver filename
- `browser = chrome` - Browser to use in a testing (depending on this field value - appropriate driver name will be looked up in webdriver_folder)

The following parameters are optional:

for `global` section:

- `log_level = INFO` - (INFO if omited). Log level. The same for all streams.
- `enable_libs_logging = True` - (False if omitted). If True, the logging from 3-d party libraries like Selenium, requests, etc, will be included in log file

for `web` section:

- `webdriver_default_wait_time = 20` - Time to wait until element appears on the page (default is 20)
- `webdriver_implicit_wait_time = 60` - Webdriver implicit wait time (default is 60)

for `api` the `api_validation` section is optional with the following optional parameters:

- `validate_status_code = True` - Should the API validator verify response status code (default is True)
- `validate_headers = True` - Should the API validator verify response headers (default is True)
- `validate_body = True` - Should the API validator verify response body (default is True)
- `validate_is_field_missing = True` - Should the API validator raise exception if some field from model is absent in response (default is True)

#### Access Facade API

To access Facade API you can use shortcut from common.facade.\_\_init__.py

```python
from common.facade import raw_config, logger
```

- `raw_config` -  shortcut to access pycats.config_manager.config object from Facade
- `logger` -  shortcut to access pycats.logger object from Facade

## Writing UI tests
TBU

## Writing API  tests

The PyCats's API testing main feature is the ability to use models to validate request/response automatically on the core level without test layer impact.
On the tests layer it is needed to prepare a response model and specify expected conditions, and the system does the rest for you.

Detailed description and example you can find on wiki page: [Writing API tests](https://github.com/Softeq/PyCats/wiki/Writing-API--tests "Writing API tests")


## License

This project is licensed under the Apache2 License - see the [LICENSE](LICENSE) file for details
