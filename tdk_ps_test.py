import time
import logging
import re
from pathlib import Path
from datetime import datetime
from factorystand.lib.sequence import TaskSequence
from factorystand.test_equipment.core.visa import VisaPlug


#class PowerSupplyCycle(TaskSequence):
class PowerSupplyCycle(TaskSequence):
    """
    Task Sequence for running on/off cycles on power supplies.
    """
    
    CONTINUE_ON_FAILURE = True

    def __init__(self) -> None:
        self.voltage_value = 5
        self.current_value = 100
        self.output_delay = 60 * 10
        self.rest_delay = 60 * 5
        self.power_supply_name = "tdk-lambda"
        self.tdk_lambda_ps = True if self.power_supply_name == "tdk-lambda" else False
        self.cycle_count = 0
        self.ps_address = '06'
    

    def setup(self):
        '''
        self.voltage_value = self.get_config_value("voltage_value")
        self.current_value = self.get_config_value("current_value")
        self.output_delay = 60 * self.get_config_value("output_delay_min")
        self.rest_delay = 60 * self.get_config_value("rest_delay_min")
        self.power_supply_name = self.get_config_value("power_supply_name")
        self.tdk_lambda_ps = True if self.power_supply_name == "tdk-lambda" else False
        self.cycle_count = 0
        '''
        self.start_time = datetime.today()
        self.data_dir = Path(
            f"./test_data/power_supply_cycle/{self.start_time:%Y-%m-%d_%H-%M}/"
        ).resolve()
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.power_supply = VisaPlug(self.get_config_value("visa_resource_name"))
        self.power_supply.open()
        #self.create_logger()
        if self.tdk_lambda_ps:
            #self.info(self.get_config_value("visa_resource_name"))
            self.power_supply.write(f"ADR {self.ps_address}")
            time.sleep(5)
            self.power_supply.write("CLS")
            time.sleep(2)
            self.power_supply.write("RST")
            time.sleep(5)

    '''
    def create_logger(self, level: int = logging.INFO) -> None:
        self.log_file_path = self.data_dir / ("test_logs.log")
        self.local_logger = logging.getLogger("Power Supply Cycling")
        self.local_logger.setLevel(level)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.local_logger.addHandler(file_handler)

    def log(self, msg, level: str = "info") -> None:
        if level == "info":
            self.local_logger.info(msg)
            self.info(msg)
        if level == "error":
            self.local_logger.error(msg)
            self.error(msg)
        elif level == "debug":
            self.local_logger.debug(msg)
    '''
    def teardown(self) -> None:
        #self.log(f"Stopping Power . Completed {self.cycle_count} cycles.")
        self.stop_output()

    def task_list(self) -> list:
        """Add task methods to the list in chosen run order"""
        return [
            self.start_output,
            self.output_delay,
            self.stop_output,
            self.rest_delay,
        ]

    def start_output(self):
        #self.log("Starting ouput.")
        if self.tdk_lambda_ps:
            self.power_supply.write("OUT 1")
            time.sleep(2)
            self.power_supply.write(f"PV {self.voltage_value}")
            time.sleep(2)
            self.power_supply.write(f"PC {self.current_value}")
        else:
            self.power_supply.write(
                f"VOLTage {self.voltage_value};CURRent {self.current_value};:OUTPut ON;PROTection:CLEar"
            )

    def output_delay(self):
        #self.log(f"Output for {int(self.output_delay/60)} minutes.")
        end_time = time.monotonic() + self.output_delay
        while time.monotonic() < end_time:
            if self.stopping:
                break
            time.sleep(1)

    def stop_output(self):
        #self.log("Stopping output.")
        if self.tdk_lambda_ps:
            self.power_supply.write("OUT 0")
            time.sleep(2)
            self.power_supply.write("RST")
        else:
            self.power_supply.write("OUTPut OFF")

    def rest_delay(self):
        #self.log(f"Resting for {int(self.rest_delay/60)} minutes.")
        end_time = time.monotonic() + self.rest_delay
        while time.monotonic() < end_time:
            if self.stopping:
                break
            time.sleep(1)
        self.cycle_count += 1



ps_obj = PowerSupplyCycle()
print('start output')
ps_obj.start_output()
print('output delay')
ps_obj.output_delay()
print('stop output')
ps_obj.stop_output()
print('rest delay')
ps_obj.rest_delay()
print('tear down')
ps_obj.teardown()
print('finished')



