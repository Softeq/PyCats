# SCAF (Softeq Common Automation Framework)
The SCAF aims to provide the well-structured framework with libraries created based on the popular python solutions intended for testing purposes and to make it universal for testing across different domain areas - Web, Mobile, IoT, Embedded.

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

SCAF uses WebDriver's RemoteDriver to be able to run a browser remotely. You need to download [selenium server](https://www.selenium.dev/downloads/ "selenium server") and provide its path in the configuration file.


### Installation

To install the required packages, download GitHub project and execute the following command in the root project's directory:

```bash
pip3 install -r requirements.txt
```

### Configuration
Prepare the config file `config.ini` in config directory of SCAF:

Example of `config.ini`:
```
[global]
logdir = Logs
log_level = DEBUG
enable_libs_logging = True
sections = api web

[api]
api_url = http://api.openweathermap.org/data/2.5/

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
- `webdriver_implicit_wait_time = 60` -Webdriver implicit wait time (default is 60)

#### Access Facade API

To access Facade API you can use shortcut from scaf.py

```python
from common.scaf import config, logger, get_logger
```

- `config` -  shortcut to access scaf.config_manager.config object from Facade
- `logger` -  shortcut to access scaf.logger object from Facade
- `get_logger` - function to initailize new logger for core modules or utils.


## Writing UI tests
TBU

## Writing API  tests

The SCAF's API testing main feature is the ability to use models to validate request/response automatically on the core level without test layer impact.
On the tests layer, you need to prepare a response model and specify expected conditions, and the system does the rest for you.

The right way to use rest_qa_api module is to create the Models that represent your API endpoint's Request and Response, wrap them to Builder and create necessary "build" methods:

**scaf/project/api/endpoints/user_endpoint.py**

```python
from typing import Dict
from common.rest_qa_api.base_endpoint import BaseRequestModel, BaseResponseModel, endpoint_factory
from common.rest_qa_api.rest_checkers import check_status
from common.rest_qa_api.rest_utils import SKIP, scaf_dataclass

# URL to API
base_url = "https://reqres.in/api/"

# Builder class contains request/response Models, endpoint object
# and methods (a.k.a "builders") to construct the request to the API
@scaf_dataclass
class UserEndpointBuilder:
    # HTTP Request Model for /users Endpoint
    @scaf_dataclass
    class _UsersEndpointRequestModel(BaseRequestModel):
        # URL's endpoint part.
        # You can use type annotation here from typing module: str, Dict, etc, or you can omit this
        endpoint: str = 'users'
        # Headers need to send in request
        headers: Dict = {"Content-Type": "application/json"}
        # JSON format for POST and PUT methods's body
        post_data = {"name": "morpheus", "job": "leader"}
        put_data = {"name": "morpheus", "job": "leader"}
        # Here we say that for PATCH and DELETE methods there is no payload to send
        patch_data = None
        delete_data = None
        # Data to append to URL as parameters
        params = "page=1"
        # Define what kind of methods are allowed to be called for this endpoint
        allowed_methods = ("get", "post", "patch", "delete")

    # HTTP Response Model for /users Endpoint
    @scaf_dataclass
    class _UsersEndpointResponseModel(BaseResponseModel):
        # Default status code you expect from this endpoint
        status_code = 200
        # Default headers you expect server sends in response
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        # Default response format with expected data from this endpoint for GET request
        get_data = {
            # If key has value it will be validated during response handling
            "page": 2,
            "per_page": 6,
            # Using SKIP keyword you can tell to skip validation for this field
            "total": SKIP,
            "total_pages": SKIP,
            "data": [
                {
                    "id": 7,
                    "email": "michael.lawson@reqres.in",
                    "first_name": "Michael",
                    "last_name": "Lawson",
                    # None value is valid value. Will be treated as 'null'
                    "avatar": None
                },
                # SKIP in list means skip this list item during validation
                SKIP,
                {
                    "id": 9,
                    "email": "tobias.funke@reqres.in",
                    "first_name": "Tobias",
                    "last_name": "Funke",
                    "avatar": "https://s3.amazonaws.com/uifaces/faces/twitter/vivekprvr/128.jpg"
                }
            ]
        }
        post_data = {"name": "morpheus", "job": SKIP, "id": SKIP, "createdAt": SKIP}
        put_data = {"name": SKIP, "job": "leader", "id": SKIP, "createdAt": SKIP}
        # Expected response's body for the HTTP DELETE method is null (empty).
        delete_data = None
        patch_data = {"name": SKIP, "job": "leader", "id": SKIP, "createdAt": SKIP}
        error_data = {"error": SKIP}
        custom_checkers = [check_status(200)]

    # Create endpoint object and pass Models as arguments
    endpoint = endpoint_factory(base_url, "UsersEndpoint",
                                          _UsersEndpointRequestModel,
                                          _UsersEndpointResponseModel)

    # Builder contains methods to "build" the request to API properly.
    # This methods should be used in steps.
    def create_user(self, first_name, job):
        self.endpoint.request_model.post_data["name"] = first_name
        self.endpoint.request_model.post_data["job"] = job
        self.endpoint.response_model.post_data["name"] = first_name
        self.endpoint.response_model.post_data["job"] = job
        user_info = self.endpoint.post().post_data
        return user_info["id"]

    def get_user_info(self, user_id, email=SKIP, first_name=SKIP, last_name=SKIP, avatar=SKIP):
        user_response_model = {
          "data": {
              "id": user_id,
              "email": email,
              "first_name": first_name,
              "last_name": last_name,
              "avatar": avatar
          }
        }
        self.endpoint.request_model.endpoint += f"/{user_id}"
        self.endpoint.response_model.get_data = user_response_model
        user_info = self.endpoint.get().get_data
        return user_info
```

Then you can create necessary steps for tests on the steps layer and combine logic from different builders in one step:

**scaf/project/api/steps/user_steps.py**

```python
from project.api.endpoints.user_endpoint import UserEndpointBuilder

def get_user_info(user_id):
    user_info = UserEndpointBuilder().get_user_info(1)
    return user_info
```
After this, you can use these keywords in your tests.

### Custom checkers usage

The SCAF API part provides the ability to add your custom response validation logic if you don't want to use internal or want to extend it.
You can create custom checkers on the project layer or add them directly to common/rest_qa_api/rest_checkers.py
You can implement checkers as callable objects that accept expected status and BaseResponseModel. For example:

```python
def check_status(status: int):
    @wraps(check_status)
    def internal_check_status(response: BaseResponseModel):
        logger.info(f"check that status code is {status}")
        assert response.raw_response.status_code == status, \
            f"Invalid status code. Expected {status}, bug got {response.raw_response.status_code}"
    return internal_check_status
```

To add created checker to Response Model:

```python
from project.api.endpoints.user_endpoint import UserEndpointBuilder

endpoint = UserEndpointBuilder().endpoint
endpoint.response_model.custom_checkers.append(check_status(201))
user_info = endpoint.post().post_data
```

If you want to store some checkers in one place and run them all automatically without the necessity to specify them one by one you can create your class container inherited from
**common/rest_qa_api/rest_checkers.py:BaseRESTCheckers** class:

```python
class JSONCheckers(BaseRESTCheckers):
    status = None
    expected_json_structure = None

    @classmethod
    def check_json_keys(cls, response: BaseResponseModel):
        expected_keys = list(cls.expected_json_structure.keys())
        expected_keys.sort()
        json_keys = list(response.raw_response.json().keys())
        json_keys.sort()
        assert json_keys == expected_keys, "Invalid JSON Structure"

    @classmethod
    def check_status(cls, response: BaseResponseModel):
        logger.info(f"check that status code is {cls.status}")
        assert response.raw_response.status_code == cls.status, \
            f"Invalid status code. Expected {cls.status}, bug got {response.raw_response.status_code}"
```

In this case, you can pass the JSONCheckers class directly to checkers list:

```python
from project.api.endpoints.user_endpoint import UserEndpointBuilder
from common.rest_qa_api.rest_checkers import JSONCheckers
from common.rest_qa_api.rest_utils import SKIP

endpoint = UserEndpointBuilder().endpoint
endpoint.request_model.post_data["name"] = first_name
endpoint.request_model.post_data["job"] = job
endpoint.response_model.post_data = SKIP
endpoint.response_model.status_code = SKIP
JSONCheckers.status = 201
JSONCheckers.expected_json_structure = {"name": first_name, "job": job, "id": 5, "createdAt": "2020-01-01"}
endpoint.response_model.custom_checkers.append(JSONCheckers)
user_info = endpoint.post().post_data
```

You are also able to exclude some checkers from the class using BaseRESTCheckers.deactivate() method:

```python
from project.api.endpoints.user_endpoint import UserEndpointBuilder
from common.rest_qa_api.rest_checkers import JSONCheckers

endpoint = UserEndpointBuilder().endpoint
endpoint.request_model.post_data["name"] = first_name
endpoint.request_model.post_data["job"] = job
endpoint.response_model.post_data["name"] = first_name
endpoint.response_model.post_data["job"] = job
JSONCheckers.status = 201
JSONCheckers.deactivate(JSONCheckers.check_json_structure)
endpoint.response_model.custom_checkers.append(JSONCheckers)
user_info = endpoint.post().post_data
```

## License

This project is licensed under the Apache2 License - see the [LICENSE](LICENSE) file for details