import json
import logging
import requests

logger = logging.getLogger(__name__)


class TestRailApiClient:
    """ Class to interact with TestRail via API. Used to work with TestRuns.
    Latest stable version - v5.3.0.

    Sample of Using:
    def close_tests_run(run_id, project_id, suite_id):
        def _is_run_active():
            active_runs = tr_client.get_test_runs(project_id=project_id,
                                                  suite_id=suite_id,
                                                  is_completed=False)
            if active_runs:
                for run in active_runs:
                    if run["id"] == run_id:
                        return True
            return False

        tr_client = TestRailApiClient(url="https://fake_url.io", user="Ivan", password="QWERTY")
        if _is_run_active():
            logger.info("close Test Rail Run with id - {}".format(run_id))
            tr_client.close_run(run_id=run_id)
        else:
            logger.info("Can't found active Test Rail Run with id - {}".format(run_id))
    """

    default_headers = {'Content-Type': 'application/json'}
    bad_response_codes = [400, 401, 403, 404, 405, 500, 502, 503, 504]

    def __init__(self, url, user, password):
        self.base_api_url = url
        self.user = user
        self.password = password

    def _send_get_request(self, url, params=None):
        """
        Send generic GET request with given URL, default headers and auth.
        """
        response = requests.get(url=url,
                                params=params,
                                auth=(self.user, self.password),
                                headers=self.default_headers)
        assert response.status_code not in self.bad_response_codes, 'Invalid response code: %s' % response.status_code
        return response

    def _send_post_request(self, url, params=None, data=None):
        """
        Send generic POST request with given URL, default headers and auth.
        """
        response = requests.post(url=url,
                                 params=params,
                                 data=data,
                                 auth=(self.user, self.password),
                                 headers=self.default_headers)
        assert response.status_code not in self.bad_response_codes, 'Invalid response code: %s' % response.status_code
        return response

    def get_users(self):
        """
        Get mapping between user names and user IDs.
        :return: Mapping between user names and user IDs.
        """
        url = '{base_url}/get_users'.format(base_url=self.base_api_url)
        response = self._send_get_request(url)
        return response.json()

    def get_run_tests(self, run_id):
        """
        Get list of tests from run.

        :param run_id: run ID.
        :return: List of tests from run.
        """
        url = '{base_url}/get_tests/{run_id}'.format(
            base_url=self.base_api_url,
            run_id=run_id
        )
        response = self._send_get_request(url)
        return response.json()

    def get_test_runs(self, project_id, suite_id=None, is_completed=None):
        """
        Get list of test runs by project id.

        :param project_id: The ID of project in which placed test run.
        :param suite_id: The ID of the test suite (optional, using for filter).
        :param is_completed: Test run status: True - completed, False - active (optional, using for filter).
        :return: List of test runs.
        """
        url = '{base_url}/get_runs/{project_id}'.format(base_url=self.base_api_url,
                                                        project_id=project_id)

        params = {}
        if suite_id is not None:
            params["suite_id"] = suite_id
        if is_completed is not None:
            params["is_completed"] = int(is_completed)

        response = self._send_get_request(url, params=params)
        return response.json()

    def add_test_run(self, project_id, suite_id, name, assignedto_id, case_ids=None):
        """
        Create new test run with name {name} in project:suite {project_id}:{suite_id}

        :param project_id: ID of the project the test run should be added to
        :param suite_id: ID of the test suite for the test run
        :param name: Name of the test run
        :param assignedto_id: ID of the user the test run should be assigned to
        :param case_ids: List of case IDs for the custom case selection
        """
        url = '{base_url}/add_run/{project_id}'.format(base_url=self.base_api_url,
                                                       project_id=project_id)
        body = {
            "suite_id": suite_id,
            "name": name,
            "assignedto_id": assignedto_id,
            "include_all": False,
            "case_ids": case_ids
        }

        response = self._send_post_request(url, data=json.dumps(body))
        return response.json()

    def close_run(self, run_id):
        """
        Close test run by id
        """
        url = '{base_url}/close_run/{run_id}'.format(base_url=self.base_api_url,
                                                     run_id=run_id)
        response = self._send_post_request(url)
        return response.json()

    def get_cases(self, project_id, suite_id=None, section_id=None):
        """
        Get cases by TestCase ID.

        :param project_id: The ID of the project.
        :param suite_id: The ID of the test suite (optional if the project is operating in single suite mode).
        :param section_id: The ID of the section (optional).
        :return: Parsed test case data.
        """
        section = "&section_id={section_id}".format(section_id=section_id) if section_id else ""
        suite = "&suite_id={suite_id}".format(suite_id=suite_id) if suite_id else ""
        url = '{base_url}/get_cases/{project_id}{suite_id}{section_id}'.format(base_url=self.base_api_url,
                                                                               project_id=project_id,
                                                                               suite_id=section,
                                                                               section_id=suite)
        response = self._send_get_request(url)
        return response.json()

    def get_cases_by_custom_field(self, project_id, field_name, field_value, suite_id=None, section_id=None):
        all_cases = self.get_cases(project_id, suite_id, section_id)
        custom_field = "custom_" + field_name
        return [case for case in all_cases if case.get(custom_field) == field_value]
