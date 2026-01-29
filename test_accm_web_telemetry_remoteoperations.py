import logging

import pytest

from rpi_bench.libs.selenium_lib.lib_selenium import BaseTestClass, Actions
from rpi_bench.libs.selenium_lib.webpages import HomePage, VehiclesPage
from rpi_bench.test_api.Webutility_AP.webuitlity import Utility
from rpi_bench.test_api.tools import get_bench_configuration
from rpi_bench.libs.selenium_lib.webpages import WebLoginPage, HomePage, VehiclesPage, DashBoardPage, DevicePage, \
    ConfigPage, DevicesPage, UpgradePage, AdminPage, environment, VhOperation, Inventory, Eventslog, SummaryPage, Trip

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
class Test_telemetry_remoteoperation:

    def setup_method(self):
        self.driver = BaseTestClass.set_up(self)
        self.wb = Utility(self.driver)
        self._bt = Actions(self.driver)

    def teardown_method(self):
        BaseTestClass.teardown(self)

    def test_C20398346_TelemetryTimestamp(self):
        """
        Test : Verify the vehicles telemetry time stamp
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.first_timestamp_cell])
        assert element is True, "Timestamp data not found"
        logging.info(element_data)

    def test_C20398335_odometer(self):
        """
        Test : Verify the vehicles telemetry odometer
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.first_odometer_cell])
        assert element is True, "Odometer data not found"
        logging.info(element_data)

    def test_C20398335_fuel(self):
        """
        Test : Verify the vehicles telemetry fuel
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.first_fuel_cell])
        assert element is True, "Fuel data not found"
        logging.info(element_data)

    def test_C20398349_ignition(self):
        """
        Test : Verify the vehicles telemetry ignition
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.first_ignition_cell])
        assert element is True, "ignition data not found"
        logging.info(element_data)

    def test_C20398368_coolant(self):
        """
        Test : Verify the vehicles telemetry ignition
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.coolant_cell])
        assert element is True, "Coolant data not found"
        logging.info(element_data)

    def test_C20398350_transmission(self):
        """
        Test : Verify the vehicles telemetry transmission
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.transmission_cell])
        assert element is True, "transmission data not found"
        logging.info(element_data)

    def test_C20398353_telemetric_tpms(self):
        """
        Test : Verify the vehicles telemetry tpms
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.tpms_cell])
        assert element is True, "TPMS data not found"
        logging.info(element_data)

    def test_C20398351_Telemetry_RPM(self):
        """
        Test : Verify the vehicles telemetry RPM
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.select_item("RPM")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.rpm_cell])
        assert element is True, "RPM data not found"
        logging.info(element_data)

    def test_C20398352_Telemetry_speed(self):
        """
        Test : Verify the vehicles telemetry speed
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.speed_cell])
        assert element is True, "Speed data not found"
        logging.info(element_data)

    def test_C20398352_Telemetry_Engine(self):
        """
        Test : Verify the vehicles Engine oil telemetry
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.select_item("Engine Oil (%)")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.engine_cell])
        assert element is True, "Engine Oil data not found"
        logging.info(element_data)

    def test_C20466049_Backend_vehicle_unlock(self):
        """
        Test : Verify the Backend vehicle unlock functionality
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        msg = self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.door_unlock_button])
        assert msg == bc['Signpage.unlock_succesful'], "unlock unsuccessful"

    def test_C20398494_Backend_vehicle_lock(self):
        """
        Test : Verify the Backend vehicle lock
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        msg = self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.door_lock_button])
        assert msg == bc['Signpage.lock_succesful'], "lock unsuccessful"

    def test_C20398495_Backend_vehicle_trunk_release(self):
        """
        Test : Verify the Backend vehicle trunk release functionality
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        msg = self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.trunk_release_button])
        assert msg == bc['Signpage.trunk_release'], "trunk release unsuccessful"

    def test_C20398496_Backend_vehicle_start_auth_enable(self):
        """
        Test : Verify the Backend vehicle trunk release functionality
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        msg = self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.start_auth_enable])
        assert msg == bc['Signpage.start_auth_enable'], "start authorization unsuccessful"

    def test_C20398498_Backend_vehicle_ask_telemetry(self):
        """
        Test : Verify the Backend vehicle ask telemetry
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        msg = self.wb.backend_vehicle_car_data_refresh(locators[DashBoardPage.car_refresh_data])
        assert msg == bc['Signpage.car_refresh_data'], "ask telemetry unsuccessful"

    def test_C20398497_Backend_vehicle_unlock_and_enable(self):
        """
        Test : Verify the Backend vehicle unlock and enable
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        msg = self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.door_unlock_and_enable_button])
        assert msg == bc['Signpage.unlock_and_enable'], "start authorization unsuccessful"

    def test_C20658771_CONFIG_time_interval_setting(self):
        """
        TestCase :config time interval setting
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        assert self.wb.set_config_time_interval(offtime, readytime, chargingtime, startedtime, drivingtime) is True, \
            "off time data is wrong"
