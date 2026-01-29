#!/usr/bin/env python

import logging
import os
import socket
from datetime import datetime
import traceback

import pytest
import yaml

from rpi_bench.libs.appium.lib_appium import start_single_appium_service
from rpi_bench.libs.lib_xray_jira import upload_results_in_jira, common_fpath
from rpi_bench.test_api.tools import get_bench_configuration, get_environment_configuration
from rpi_bench.test_api.env_report_utils import save_backend_version_environment_report, \
    save_devices_version_environment_report, get_environment_report
from rpi_bench.test_api.constants import ACCM_VEHICLES

logger = logging.getLogger("ACCM_campaign")
APPIUM_SERVICE = None

KNOWN_ISSUES = get_bench_configuration().get("KNOWN_ISSUES", default=dict())
jira_flag = get_environment_configuration().get("NEED_RESULTS_IN_JIRA", default=False)

logger.info(f"jira_flag : {jira_flag}")

def get_appium_service():
    global APPIUM_SERVICE
    if not APPIUM_SERVICE:
        APPIUM_SERVICE = start_single_appium_service()

    return APPIUM_SERVICE


def pytest_configure(config):
    #Save some element on environment.yaml file in reports folder
    save_backend_version_environment_report()
    save_devices_version_environment_report()



def pytest_sessionstart(session):
    appium_service = get_appium_service()
    assert appium_service.is_running
    logger.info("Appium server started")


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    env_report = get_environment_report()
    session.config._metadata.update(env_report)

    appium_service = get_appium_service()
    logger.info("Stopping Appium server ...")
    if appium_service and appium_service.is_running:
        appium_service.stop()
    assert not appium_service.is_running
    logger.info("Appium server stopped")

    if jira_flag:
        # reset the execution_key in yaml file to ""
        with open(common_fpath) as f:
            doc = yaml.safe_load(f)
        doc["JIRA"]["EXECUTION_KEY"] = ""
        with open(common_fpath, 'w') as f:
            yaml.dump(doc, f)


def pytest_addoption(parser):
    parser.addoption("--app_version", action="store", default=None)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def skip_if_known_issue(request):
    if request.function.__name__ in KNOWN_ISSUES.keys():
        pytest.skip("Skipped because: {}".format(KNOWN_ISSUES[request.function.__name__]))


def pytest_html_report_title(report):
    report.title = "ACCM automation campaign on {hostname} at {date}".format(hostname=socket.gethostname(),
                                                                             date=datetime.now())



@pytest.fixture(scope="function")
def update_results_to_jira(request):
    outcome = yield
    if jira_flag:
        logger.info("try to export result in Jira")
        testname = os.environ.get('PYTEST_CURRENT_TEST')
        test_name = testname.split("::")[len(testname.split("::")) - 1].split(" ")[0].replace("[", "").replace("]", "")


        if request.node.rep_call.passed:
            upload_results_in_jira(test_name, "pass")
            logger.info("result update is done for test case " + test_name)
        else:
            traces = request.node.rep_call.longreprtext
            upload_results_in_jira(test_name, "fail", traces)
    else:
        logger.info("results are not updated in jira as the flag is set to 'no'")
