# apogee-sdk

## Table of Contents

- [Installation](#installation)
- [Bluetooth](#bluetooth)
  - [BleScanner](#blescanner)
    - [scan](#scan)
    - [set_min_scan_time](#set-min-scan-time)
  - [BleClient](#bleclient)
    - [Alias](#alias)
      - [get_alias](#get_alias)
      - [set_alias](#set_alias)
    - [Battery Level](#battery-level)
      - [get_battery_level](#get_battery_level)
    - [Calibration Coefficients](#calibration-coefficients)
      - [get_coefficients](#get_coefficients)
      - [get_coefficients_1](#get_coefficients_1)
      - [get_coefficients_2](#get_coefficients_2)
      - [set_coefficients_1](#set_coefficients_1)
      - [set_coefficients_2](#set_coefficients_2)
    - [Connecting](#connecting)
      - [connect](#connect)
      - [disconnect](#disconnect)
      - [is_connected](#is_connected)
    - [Dark Offset](#dark-offset)
      - [start_dark_offset_calibration](#start_dark_offset_calibration)
      - [get_dark_offset_calibration_enabled](#get_dark_offset_calibration_enabled)
      - [reset_dark_offset_calibration](#reset_dark_offset_calibration)
    - [Data Logging](#data-logging)
      - [start_data_logging](#start_data_logging)
      - [get_logging_active](#get_logging_active)
      - [set_logging_active](#set_logging_active)
      - [get_logging_timing](#get_logging_timing)
      - [set_logging_timing](#set_logging_timing)
    - [Data Transfer](#data-transfer)
      - [collect_data](#collect_data)
    - [Device Info](#device-info)
      - [get_device_info](#get_device_info)
      - [get_manufacturer_name](#get_manufacturer_name)
      - [get_model](#get_model)
      - [get_serial_number](#get_serial_number)
      - [get_firmware_version](#get_firmware_version)
      - [get_hardware_version](#get_hardware_version)
      - [get_software_version](#get_software_version)
    - [Fan Control](#fan-control)
      - [get_fan_state](#get_fan_state)
      - [set_fan_duty_cycle](#set_fan_duty_cycle)
      - [set_fan_pause_time](#set_fan_pause_time)
      - [set_fan_darkness_threshold](#set_fan_darkness_threshold)
    - [Gateway Mode](#gateway-mode)
      - [get_gateway_mode_rate](#get_gateway_mode_rate)
      - [set_gateway_mode_rate](#set_gateway_mode_rate)
    - [LEDs](#leds)
      - [get_led_enabled](#get_led_enabled)
      - [set_led_enabled](#set_led_enabled)
    - [Live Data](#live-data)
      - [get_live_data](#get_live_data)
    - [Live Data Averaging](#live-data-averaging)
      - [get_live_data_averaging_time](#get_live_data_averaging_time)
      - [set_live_data_averaging_time](#set_live_data_averaging_time)
    - [Modbus Settings](#modbus-settings)
      - [get_modbus_settings](#get_modbus_settings)
      - [set_modbus_settings](#set_modbus_settings)
    - [Sensor ID](#sensor-id)
      - [get_sensor_id](#get_sensor_id)
      - [set_sensor_id](#set_sensor_id)
    - [Sensor Time](#sensor-time)
      - [get_sensor_time](#get_sensor_time)
      - [set_sensor_time](#set_sensor_time)
      - [set_sensor_time_to_current](#set_sensor_time_to_current)
    - [Time Till Full](#time-till-full)
      - [get_logging_full_time](#get_logging_full_time)
    - [Last Transferred Timestamp](#last-transferred-timestamp)
      - [get_last_transferred_timestamp](#get_last_transferred_timestamp)
      - [set_last_transferred_timestamp](#set_last_transferred_timestamp)
- [Logging Messages](#logging-messages)
- [Contact](#contact)

## Installation

#### _Install_

1. Install by running the following command in terminal within an activated virtual environment:

`pip install apogee-sdk`

#### _Update_

To update to the latest version, run the following command in terminal:

`pip install apogee-sdk --upgrade`

#### _Uninstall_

To uninstall, run the following command in terminal:

`pip uninstall apogee-sdk`

# Bluetooth

For more information about Apogee's bluetooth sensor's available characteristics, advertising strategy, and a complete guide to functionality, see:
https://www.apogeeinstruments.com/content/Apogee-Bluetooth-API-2.0.pdf

## BleScanner

Class used to discover advertising Apogee bluetooth sensors,

_Example_

```
from apogee.bluetooth import BleScanner

async def main():
    scanner = BleScanner()
    scanner.set_min_scan_time(
        min_time=2
        )

    discovered_devices = await scanner.scan(
        duration=10,
        end_early_if_stable=True
        )
```

_Functions_

#### _scan_

Scan for nearby Apogee sensors

:param duration: (optional) The duration of time in seconds to scan for Apogee sensors
:param end_early_if_stable: (optional) If determined that all nearby sensors are found and no more information is needed, end scan early.
This may still result in a false negative if the initial packet discovery of another sensor did not occur before the set minimum duration

:return: A dictionary mapping MAC addresses (str) to a dictionary containing advertising information.

        Advertising information includes:

            - sensor_id: The integer representation of the sensor's id number

            - alias: The assigned alias

            - serial_number: The serial number

            - type: The type of sensor

#### _set_min_scan_time_

Set minimum scan time before determining if all Apogee sensor packets have been found

Apogee sensor's advertise multiple packets of identifying information. The BleScanner class tries to automatically detect when all the packets of advertising information have been discovered from nearby Ble sensors. This function sets the minimum amount of time in seconds before the class starts trying to determine if all packets have been discovered. A higher minimum scan time can be used since this may still result in a false negative if the initial packet discovery of another sensor did not occur before the set minimum duration

:param time: The duration of time in seconds to set the minimum scan time.

## BleClient

Class used for all communication with Apogee bluetooth sensors.

### Alias

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.set_alias(
        alias = "Example Alias"
        )
    alias = await client.get_alias()
```

_Functions_

#### _get_alias_

    Get the alias of the connected sensor.

    :return: A str with the alias of the sensor.

#### _set_alias_

    Set the alias of the connected sensor.
    Max number of characters for alias is 20.

    :param alias: A str with the desired alias of the sensor.

### Battery Level

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    battery = await client.get_battery_level()
```

_Functions_

#### _get_battery_level_

    Get the battery level of the connected sensor.
    Not applicable to Guardian sensors.

    :return: An int indicating the current battery level percentage.

### Calibration Coefficients

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.set_coefficients(1.1, 2.2, 3.3, 4.4, 5.5, 6.6)
    coefficients = await client.get_coefficients()
```

_Functions_

#### _get_coefficients_

    Get all the calibration coefficients of the connected sensor.
    The number of calibration coefficients varies by sensor but will be between 1 and 6

    :return: A List containing 6 floats for the 6 possible calibration coefficients

#### _get_coefficients_1_

    Get the first 3 calibration coefficients of the connected sensor.

    :return: A List containing 3 floats for the first 3 calibration coefficients

#### _get_coefficients_2_

    Get the last 3 calibration coefficients of the connected sensor.

    :return: A List containing 3 floats for the last 3 calibration coefficients

#### _set_coefficients_

    Set all calibration coefficients of the connected sensor.
    If the desired sensor uses less than 6 calibration coefficients, set the remaining values to 0

    :param coefficients: A list of 6 floats containing the calibration coefficients.

#### _set_coefficients_1_

    Set the first 3 calibration coefficients of the connected sensor.
    If the desired sensor uses less than the first 3 calibration coefficients, set the remaining values to 0

    :param coefficients: A list of 3 floats containing the first 3 calibration coefficients.

#### _set_coefficients_2_

    Set the last 3 calibration coefficients of the connected sensor.
    If the desired sensor uses less than the last 3 calibration coefficients, set the remaining values to 0

    :param coefficients: A list of 3 floats containing the last 3 calibration coefficients.

### Connecting

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect(
        retries=3,
        retry_delay=1
    )
    connected = client.is_connected
    await client.disconnect()
```

_Functions_

#### _connect_

    Attempt to connect to BLE device

    :param retries: (optional) An int representing the number of tries to retry in the event of a failed connection. Default is 2
    :param retry_delay: (optional) A float representing the number of seconds to wait between retries. Default is 0.5

#### _disconnect_

    Attempt to disconnect from BLE device

#### _is_connected_

    Return connected state of Ble device

    :return: A boolean indicating the current connected state of a Ble device

### Dark Offset

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.start_dark_offset_calibration()
    dark_offset_enabled = await client.get_dark_offset_calibration_enabled()
    aait client.reset_dark_offset_calibration()
```

_Functions_

#### _start_dark_offset_calibration_

    Start the dark offset calibration process.
    This process takes about 30 seconds.
    The light detector on the sensor should be covered throughout the process

    :param timeout: Number of seconds to wait before aborting if still haven't received a response from the device

    :return bool: Returns a boolean indicating whether the calibration was successful

#### _get_dark_offset_calibration_enabled_

    Check if dark offset calibration is currently in use.

    :return: A boolean indicating whether the dark offset calibration is being used.

#### _reset_dark_offset_calibration_

    Stop using the dark offset calibration

### Data Logging

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.start_data_logging(
        sampling_interval=15,
        logging_interval=300,
        start_time=1724942711,
        end_time=None,
        gateway_mode_rate=1
    )
```

_Functions_

#### _start_data_logging_

    Turn on data logging, set logging parameters, and optionally turn on gateway mode in a single function call.

    :param sampling_interval (int): (optional) The number of seconds a data sample is taken. Default is 15.
    :param logging_interval (int): (optional) The number of seconds a data sample is logged. Default is 300.
    :param start_time (int): (optional) The time using epoch time in seconds at which the sensor did/will start logging. Is None if not logging and not set or not available on firmware version. Default is to start immediately
    :param end_tme (int): (optional) (firmware version restriction) The time using epoch time in seconds at which the sensor will end logging. Is None if not logging and not set or not available on firmware version. Default is to never stop.
    :param gateway_mode_rate (int)s: An int indicating how often the sensor will advertise when data is logged. Default is 0.
            i.e., it advertises once every n data logs, where n correlates with the rate variable
            0 indicates that the sensor will not automatically advertise and requires a manual button press.

#### _get_logging_active_

    Get the logging state of the connected sensor.

    :return: A boolean indicating whether the sensor is currently logging.

#### _set_logging_active_

    Set the logging state of the connected sensor.

    :param active: A boolean with the desired logging state.

#### _get_logging_timing_

    Get the logging timing of the connected sensor.
    Firmware version restriction: End time is only available on uCache firmware version ≥ 9 or Guardian firmware version ≥ 3

    :return: A tuple containing:
        - sampling_interval (int): The number of seconds a data sample is taken.
        - logging_interval (int): The number of seconds a data sample is logged.
        - start_time (int): (optional) The time using epoch time in seconds at which the sensor did/will start logging. Is None if not logging and not set or not available on firmware version.
        - end_tme (int): (optional) (firmware version restriction) The time using epoch time in seconds at which the sensor will end logging. Is None if not logging and not set or not available on firmware version.

#### _set_logging_timing_

    Set the logging timing of the connected sensor.

    Firmware version restriction: End time is only available on uCache firmware version ≥ 9 or Guardian firmware version ≥ 3

    :param sampling_interval: An int representing the number of seconds a data sample should be taken. MUST be less than AND an interval of the logging interval variable.
    :param logging_interval: An int representing the number of seconds a data sample should be logged. MUST be greater than AND divisible by the sampling interval variable.
    :param start_time: (optional) An int representing the desired start time in epoch time for data logging. Default is to start immediately.
    :param end_tme: (optional) (firmware version restriction) An int representing the desired end time in epoch time for data logging. Default is to never end.

### Data Transfer

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    collected_data = await client.collect_data(
        start_time=1724942711,
        end_time=1748455754,
        timeout=60
    )
```

_Functions_

#### _collect_data_

    Collect logged data from the sensor

    :param start_time: (optional) The time, using epoch time in seconds, of the earliest logged data to collect.
                        A value of None will start from the last log transferred. (See get_last_timestamp_transferred)
    :param end_time: (optional) The time, using epoch time in seconds, of the latest logged data to collect.
                        A value of None will end at last log on device.
    :param timeout: (optional) The maximum number of seconds to collect data before aborting.
                        A value of None will never timeout.

    :return List: Returns a list of dicts that include the timestamp and the datapoints

### Device Info

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    fw_version = await client.get_firmware_version()
    serial_no = await client.get_serial_number()
```

_Functions_

#### _get_device_info_

    Get the basic device info of the connected sensor.

    :return: A dict containing the device information, including:
            - address: MAC address
            - manufacturer: Manufacturer Name
            - model: Model Number
            - serial number: Serial Number
            - firmware version: Firmware Version
            - hardware version: Hardware Version
            - software version: Software Version
            - alias: Device Alias
            - sensor id: Sensor ID number

#### _get_manufacturer_name_

    Get the manufacturer name of the connected sensor

    :return: A str with the name of the sensor manufacturer.

#### _get_model_

    Get the model number of the connected sensor

    :return: A str with the model number of the sensor.

#### _get_serial_number_

    Get the serial number of the connected sensor

    :return: An int with the serial number of the sensor.

#### _get_firmware_version_

    Get the firmware version of the connected sensor

    :return: An int with the firmware version of the sensor.

#### _get_hardware_version_

    Get the hardware version of the connected sensor

    :return: An int with the hardware version of the sensor.

#### _get_software_version_

    Get the software version of the connected sensor.
    A string with a single space (" ") denotes a release version.

    :return: A str with the software version of the sensor.

#### _get_sensor_id_

    Get the sensor id of the connected sensor.

    :return: An int with the sensor id number.

#### _set_sensor_id_

    Change the sensor id of the connected sensor.
    This will also result in a change in the model of the sensor and the data recorded and returned from the sensor

    :param id: An int with the sensor id number.

### Fan Control

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.set_fan_duty_cycle(
        duty_cycle=50
        )
```

_Functions_

#### _get_fan_state_

    Get the fan state of the connected sensor.
    Only applies to Guardian sensors.

    :return: A tuple containing:
        - duty_cycle (int): The fan's duty cycle percentage.
        - fan_darkness_threshold (float): The darkness threshold value at which fan's duty cycle will be throttled. 0 indicates that the fan will never be throttled.
        - fan_pause_time (int): Time in minutes the fan is paused.
        - rpm (int): Fan rotations per minute.

#### _set_fan_duty_cycle_

    Set the duty cycle for the fan of the connected sensor.
    Only applies to Guardian sensors.

    :param duty_cycle: A float representing the desired duty cycle percentage of the fan.
                    duty_cycle must be between 40 and 100, inclusive

#### _set_fan_pause_time_

    Set the number of minutes to pause the fan of the connected sensor.
    Only applies to Guardian sensors.

    :param pause_time: An int representing the number of minutes to pause the fan.
                    pause_time must be between 0 and 250 minutes, inclusive

#### _set_fan_darkness_threshold_

    Set the darkness threshold for the fan of the connected sensor.
    When PAR values fall below this threshold, the fan's duty cycle will be throttled to 40%.
    Only applies to Guardian sensors.

    :param darkness_threshold: A float representing the PAR value threshold at which to throttle the fan.
                        darkness_threshold must be between 0 and 250 minutes, inclusive

### Gateway Mode

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.set_gateway_mode_rate(
        rate=3
        )
    rate = await client.get_gateway_mode_rate()
```

_Functions_

#### _get_gateway_mode_rate_

    Get the gateway mode rate of the connected sensor.
    Not applicable to Guardian sensors.

    Gateway mode provides the functionality for the sensor to advertise periodically, synchronized with data logging.
    The sensor will advertise for up to 10 seconds or until connected.

    :return: An int indicating how often the sensor will advertise when data is logged.
            i.e., it advertises once every n data logs.
            0 indicates that the sensor will not automatically advertise and requires a manual button press.

#### _set_gateway_mode_rate_

    Set the gateway mode rate of the connected sensor.
    Not applicable to Guardian sensors.

    Gateway mode provides the functionality for the sensor to advertise periodically, synchronized with data logging.
    The sensor will advertise for up to 10 seconds or until connected.

    :param rate: An int indicating how often the sensor will advertise when data is logged.
            i.e., it advertises once every n data logs, where n correlates with the rate variable
            0 indicates that the sensor will not automatically advertise and requires a manual button press.

### LEDs

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.set_led_enabled(False)
    led_enabled = await client.get_led_enabled()
```

_Functions_

#### _get_led_enabled_

    Get the led state of the connected sensor.
    Only applies to Guardian sensors.

    :return: A boolean indicating whether the LEDs are currently enabled.

#### _set_led_enabled_

    Set the led state of the connected sensor.

    :param enabled: A boolean with the desired led state.

### Live Data

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    live_data = await client.get_live_data()
```

_Functions_

#### _get_live_data_

    Retrieve the live data from the sensor

    :param timeout: Number of seconds to wait before aborting if still haven't received a response from the device

    :return Dict: Returns a dict that include the datapoints with the keys being the name of the datapoints

### Live Data Averaging

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.set_live_data_averaging_time(average=5)
    averaging_time = await client.get_live_data_averaging_time()
```

_Functions_

#### _get_live_data_averaging_time_

    Get the rolling live data average time in seconds of the connected sensor.

    :return: A float with the live data averaging time.

#### _set_live_data_averaging_time_

    Set the rolling live data average time in seconds of the connected sensor.

    :param average: A float with the number of seconds for the desired averaging time.
                    Averaging time must be between 0 and 30 seconds, inclusive

### Modbus Settings

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.set_modbus_settings(
        address=1,
        baudrate=19200,
        parity="N",
        stop_bits=1
        )
```

_Functions_

#### _get_modbus_settings_

    Get the modbus settings of the connected sensor.
    Only applies to Guardian sensors.

    :return: A tuple containing:
        - address (int): An int representing the modbus address of the sensor. 1 - 247
        - baudrate (int): An int representing the baudrate of the sensor. 115200, 57600, 38400, 19200, 9600, or 1200
        - parity (str): A string containing a single character representing the parity of the sensor. 'N'one or 'E'ven.
        - stop_bits (int): An int representing the stop bits of the sensor. 1 or 2

#### _set_modbus_settings_

    Set the modbus settings of the connected sensor.
    Only applies to Guardian sensors.

    :param address: An int representing the modbus address of the sensor. Valid values are 1 - 247, inclusive.
    :param baudrate: An int representing the baudrate of the sensor. 115200, 57600, 38400, 19200, 9600, or 1200
    :param parity: A string containing a single character representing the parity of the sensor. 'N'one or 'E'ven.
    :param stop_bits: An int representing the stop bits of the sensor. 1 or 2

### Sensor Time

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    await client.set_sensor_time_to_current()
    sensor_time = await client.get_sensor_time()
```

_Functions_

#### _get_sensor_time_

    Get the current time of the sensor in epoch time.

    :return: An int representing epoch time in seconds

#### _set_sensor_time_

    Set the time of the sensor to desired time in epoch time.

    :param time: An int representing epoch time in seconds.

#### _set_sensor_time_to_current_

    Set the time of the sensor to the current time.

#### Time Till Full

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    logging_full_time = await client.get_logging_full_time()
```

_Functions_

#### _get_logging_full_time_

    Get the time at which logging will be full in epoch time.
    When full, the sensor will start overwriting the oldest logs in memory.

    :return: An int representing epoch time in seconds at which logging will be full

### Last Transferred Timestamp

_Example_

```
from apogee.bluetooth import BleClient

async def main():
    client = BleClient()
    await client.connect()
    last_collected_log = await client.get_last_transferred_timestamp()
```

_Functions_

#### _get_last_transferred_timestamp_

    Get the time in epoch time of the last datalog collected using the data transfer characteristic.
    When transferring data using the collect_data function (Data Transfer Characteristic) the sensor's internal memory will record the timestamp of the last log that was sent.

    :return: An int representing epoch time in seconds of the last log collected

#### _set_last_transferred_timestamp_

    Set the time in epoch time of the last datalog collected.
    This will cause the sensor to start sending data from this timestamp next time logs are collected as it changes the sensor's internal memory of the timestamp of the last log sent.

    :param time: An int representing epoch time in seconds of the last log collected

# Logging Messages

Use python's logging to show logging messages in the terminal window.

Available logging levels:

- Critical
- Error
- Warning (Default)
- Info
- Debug

_Example_

```
from apogee.tools.MessageHandler import LoggingMessages
from apogee.bluetooth import BleClient

async def main():
    LoggingMessages.set_level("INFO")

    client = BleClient()
    await client.connect()
```

## Contact

For more information or additional help, contact Apogee Instruments at: [techsupport@apogeeinstruments.com](mailto:techsupport@apogeeinstruments.com) or [+1(435)245-8012](tel:+14352458012)
