import logging

import pytest

from rpi_bench.libs.selenium_lib.lib_selenium import BaseTestClass
from rpi_bench.libs.selenium_lib.webpages import HomePage, VehiclesPage
from rpi_bench.test_api.Webutility_AP.webuitlity import Utility, wait_time
from rpi_bench.test_api.tools import get_bench_configuration
from rpi_bench.libs.selenium_lib.webpages import WebLoginPage, HomePage, VehiclesPage, DashBoardPage, DevicePage, \
    ConfigPage, DevicesPage, UpgradePage, AdminPage, environment, VhOperation, Inventory, Eventslog, SummaryPage, Trip

bc = get_bench_configuration()
locators = BaseTestClass.load_pages()

bc = get_bench_configuration()
url = bc['Signpage.web_url']
email = bc['Signpage.email']
password = bc['Signpage.pwd']
invalidpwd = bc['Signpage.invalidpwd']
superemail = bc['Signpage.superadmin']
superpwd = bc['Signpage.superpwd']
vehiclename = bc['Signpage.vhName']
offtime = bc['Signpage.offtime']
readytime = bc['Signpage.readytime']
chargingtime = bc['Signpage.chargingtime']
startedtime = bc['Signpage.startedtime']
drivingtime = bc['Signpage.drivingtime']
org_list = bc['Signpage.org_expected']


@pytest.mark.usefixtures("update_results_to_jira")
class Test_privatemode:

    def setup_method(self):
        self.driver = BaseTestClass.set_up(self)
        self.wb = Utility(self.driver)

    def teardown_method(self):
        BaseTestClass.teardown(self)

    def test_C20398469_synunlock(self):
        """
        Test : Verify the events for the synthesis unlock
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.disable_privatemode()
        self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.door_unlock_button])
        wait_time(offtime)
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info(element_data)

    def test_C20398470_lockevent(self):
        """
        Test : Verify the Backend vehicle lock functionality
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.disable_privatemode()
        self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.door_lock_button])
        wait_time(offtime)
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info(element_data)

    def test_C20398471_Backend_vehicle_start_auth_enable(self):
        """
        Test : Verify the Backend vehicle start auth functionality
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.disable_privatemode()
        self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.start_auth_enable])
        wait_time(offtime)
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info(element_data)

    def test_C20398473_Event_synthesis_for_UNLOCK(self):
        """
        Test : Verify the event under the vehicle data is not generated when the mode private is enabled for unlock operation
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.privateMode("ENGINE_SPEED")
        self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.door_unlock_button])
        wait_time(offtime)
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info(element_data)

    def test_C20398474_Event_synthesis_for_LOCK(self):
        """
        Test : Verify the event under the vehicle data is not generated when the mode private is enabled for Lock operation
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.privateMode("FUEL_LEVEL")
        self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.door_lock_button])
        wait_time(offtime)
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info(element_data)

    def test_C20398475_Event_synthesis_for_ENGINE_START(self):
        """
        Test : Verify the event under the vehicle data is not generated when the mode private is enabled for start operation
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.privateMode("GNSS_VEHICLESPEED")
        self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.start_auth_enable])
        wait_time(offtime)
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info(element_data)

    def test_C20398472_Event_synthesis_for_ENGINE_STOP(self):
        """
        Test : Verify the event under the vehicle data is not generated when the mode private is enabled for disable operation
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.privateMode("GNSS_VEHICLESPEED")
        self.wb.backend_vehicle_remote_assistance(locators[DevicesPage.disable_btn])
        wait_time(offtime)
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info(element_data)
