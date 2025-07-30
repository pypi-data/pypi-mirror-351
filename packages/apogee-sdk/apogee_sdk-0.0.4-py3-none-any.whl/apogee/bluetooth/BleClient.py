import datetime
import struct
import uuid
import asyncio
import bleak
from bleak.backends.characteristic import BleakGATTCharacteristic
from typing import List, Dict, Callable, Tuple, Awaitable

from apogee.bluetooth.uuids import *
from apogee.bluetooth.SensorClasses import SENSOR_REGISTRY, ApogeeSensor
from apogee.tools.MessageHandler import LoggingMessages as messenger


class BleClient:
    #region INIT
    def __init__(self, 
                 address: str):
        """
        :param address: The MAC address of the sensor. If unknown, use the BleScanner to scan for and obtain the address
        """
        self._validate_address(address)
        
        self._address: str = address
        self._bleak_client: bleak.BleakClient = None 
        
        # notification_handlers used for live data notifications
        self.__notification_handlers: Dict[str, Callable] = {}

        messenger.debug(f"BleClient created with address: {address}")
    #endregion
    
    #region VALIDATION
    def _validate_address(self, address):
        if not isinstance(address, str):
            raise TypeError(f"Invalid address {address}. Must be a string.")  
    #endregion

    #region CONNECTION               
    async def connect(
            self,
            retries: int = 2,
            retry_delay: float = 0.5
            ) -> bool:
        """
        Attempt to connect to BLE device

        :param retries: (optional) An int representing the number of tries to retry in the event of a failed connection
        :param retry_delay: (optional) A float representing the number of seconds to wait between retries
        """
        if not self._bleak_client:
            exception_msg = "" # Save error message in the event of failuree

            for attempt in range(retries):
                messenger.info("Connecting to sensor...")
                try:
                    self._bleak_client = bleak.BleakClient(self._address)
                    await self._bleak_client.connect()
                    connected = self._bleak_client.is_connected
                    messenger.debug(f"Sensor connected: {connected}")
                    return connected
                except Exception as e:
                    messenger.info(f"Connection attempt {attempt + 1} failed")
                    exception_msg = e
                
                # Let the device sleep momentarily before retrying, unless it's the last attempt
                if attempt < retries - 1:
                    messenger.debug(f"Delaying for {retry_delay} sec before next attempt")
                    await asyncio.sleep(retry_delay)


            messenger.error("Failed to connect to sensor")
            raise RuntimeError(f"Failed to connect to sensor {self._address}. {exception_msg}")  

    async def disconnect(self):
        """
        Attempt to disconnect from BLE device
        """
        if self._bleak_client:
            try:
                messenger.info("Disconnecting from sensor")
                await self._bleak_client.disconnect()
                self._bleak_client = None
            
            except bleak.BleakError as e:
                raise RuntimeError(f"Error when disconnecting from sensor {self._address}. {e}")
    
    @property
    def is_connected(self) -> bool:
        """
        Return connected state of Ble device

        :return: A boolean indicating the current connected state of a Ble device
        :rtype: bool
        """
        
        if not self._bleak_client:
            return False
        
        connected = self._bleak_client.is_connected
        messenger.debug(f"Sensor connection state: {connected}")
        return connected
    #endregion

    #region GATT CHARACTERISTIC COMMUNICATION
    async def read_characteristic(
            self, 
            uuid: uuid.UUID
            ) -> bytes:
        """
        Reads a Bluetooth GATT characteristic by UUID.

        :param uuid: The UUID of the characteristic to read.
        :return: The raw bytes returned from the characteristic.
        :raises RuntimeError: If not connected to a device or the read fails.
        """
        
        if not self._bleak_client or not self._bleak_client.is_connected:
            raise RuntimeError("No connected bluetooth device")
        
        try:
            messenger.debug(f"Reading from characteristic {str(uuid)}")
            data = await self._bleak_client.read_gatt_char(uuid)
            return bytes(data)
        except bleak.exc.BleakCharacteristicNotFoundError as e:
            raise RuntimeError(f"Characteristic doesn't exist for connected sensor. {e}")
        except bleak.BleakError as e:
            raise RuntimeError(f"Read Failed: {e}")
        except Exception as e:
            raise RuntimeError(e)
    
    async def write_characteristic(
            self, 
            uuid: uuid.UUID, 
            data: bytearray
            ):
        """
        Writes a bytearray to a Bluetooth GATT characteristic by UUID.

        :param uuid: The UUID of the characteristic to write.
        :param data: The data to write of type bytearray.
        :raises RuntimeError: If not connected to a device or the write fails.
        """
        if not self._bleak_client or not self._bleak_client.is_connected:
            raise RuntimeError("No connected bluetooth device")
        
        try:
            messenger.debug(f"Writing to characteristic {str(uuid)}")
            await self._bleak_client.write_gatt_char(uuid, data, True)
        except bleak.exc.BleakCharacteristicNotFoundError as e:
            raise RuntimeError(f"Characteristic doesn't exist for connected sensor. {e}")
        except bleak.BleakError as e:
            raise RuntimeError(f"Write Failed: {e}")
        except Exception as e:
            raise RuntimeError(e)
        
    async def start_notifications(
            self, 
            uuid: uuid.UUID, 
            notification_handler: Callable[
                [BleakGATTCharacteristic, bytearray], 
                None | Awaitable[None]
                ]
            ):
        """
        Starts notifications of a Bluetooth GATT characteristic by UUID.

        :param uuid: The UUID of the characteristic to write.
        :param notification_handler: The callback function to receive the notifications.
        :raises RuntimeError: If not connected to a device or the notification start fails.
        """
        if not self._bleak_client or not self._bleak_client.is_connected:
            raise RuntimeError("No connected bluetooth device")
        
        try:
            messenger.debug(f"Starting notification for characteristic {str(uuid)}")
            await self._bleak_client.start_notify(uuid, notification_handler)
        except bleak.exc.BleakCharacteristicNotFoundError as e:
            raise RuntimeError(f"Characteristic doesn't exist for connected sensor. {e}")
        except bleak.BleakError as e:
            raise RuntimeError(f"Notification start failed: {e}")
        except Exception as e:
            raise RuntimeError(e)
        
    async def stop_notifications(
            self, 
            uuid: uuid.UUID
            ):
        """
        Starts notifications of a Bluetooth GATT characteristic by UUID.

        :param uuid: The UUID of the characteristic to write.
        :raises RuntimeError: If not connected to a device or the notification stop fails.
        """
        if not self._bleak_client or not self._bleak_client.is_connected:
            raise RuntimeError("No connected bluetooth device")
        
        try:
            messenger.debug(f"Stopping notification for characteristic {str(uuid)}")
            await self._bleak_client.stop_notify(uuid)
        except bleak.exc.BleakCharacteristicNotFoundError as e:
            raise RuntimeError(f"Characteristic doesn't exist for connected sensor. {e}")
        except bleak.BleakError as e:
            raise RuntimeError(f"Notification stop failed: {e}")
        except Exception as e:
            raise RuntimeError(e)
    
    
    async def _notifications_handler(self, sender, data):
        uuid = sender.uuid

        messenger.debug(f"{str(uuid)} packet received: {data}")
        
        # Send the data packet to the callback handler
        if uuid in self.__notification_handlers:
            self.__notification_handlers[uuid](self._address, uuid, data)
    #endregion

    #region BATTERY LEVEL
    async def get_battery_level(self) -> int:
        """
        Get the battery level of the connected sensor.
        Not applicable to Guardian sensors.
        
        :return: An int indicating the current battery level percentage.
        """
        data = await self.read_characteristic(batteryLevelCharacteristicUUID)
        messenger.debug(f"Battery level data read: {data}")
        battery = int.from_bytes(data, byteorder='little', signed=False)
        messenger.info(f"Battery level read: {battery}")

        return battery
    #endregion

    #region DEVICE INFO
    async def get_device_info(self) -> Dict:
        """
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
        """
        messenger.info("Collecting device info...")

        manufacturer = await self.get_manufacturer()
        model = await self.get_model()
        serial_number = await self.get_serial_number()
        firmware = await self.get_firmware_version()
        hardware = await self.get_hardware_version()
        software = await self.get_software_version()
        alias = await self.get_alias()
        id = await self.get_sensor_id()

        return {
            "address": self._address,
            "manufacturer": manufacturer, 
            "model": model, 
            "serial number": serial_number, 
            "firmware version": firmware, 
            "hardware version": hardware, 
            "software version": software, 
            "alias": alias,
            "sensor id": id
            }
    #endregion

    #region MANUFACTURER NAME
    async def get_manufacturer(self) -> str:
        """
        Get the manufacturer name of the connected sensor
        
        :return: A str with the name of the sensor manufacturer.
        """
        data = await self.read_characteristic(manufacturerNameUUID)
        messenger.debug(f"Manufacturer name data read: {data}")

        manufacturer = data.decode('utf-8')
        messenger.info(f"Manufacturer name read: {manufacturer}")

        return manufacturer
    #endregion

    #region MODEL
    async def get_model(self) -> str:
        """
        Get the model number of the connected sensor
        
        :return: A str with the model number of the sensor.
        """
        data = await self.read_characteristic(modelNumberUUID)
        messenger.debug(f"Model number data read: {data}")

        model = data.decode('utf-8')
        messenger.info(f"Model number read: {model}")

        return model
    #endregion

    #region SERIAL NUMBER
    async def get_serial_number(self) -> int:
        """
        Get the serial number of the connected sensor
        
        :return: An int with the serial number of the sensor.
        """
        data = await self.read_characteristic(serialNumberUUID)
        messenger.debug(f"Serial number data read: {data}")

        serial_no = int(data.decode('utf-8'))
        messenger.info(f"Serial number read: {serial_no}")

        return serial_no
    #endregion

    #region FIRMWARE VERSION
    async def get_firmware_version(self) -> int:
        """
        Get the firmware version of the connected sensor
        
        :return: An int with the firmware version of the sensor.
        """
        data = await self.read_characteristic(firmwareVersionUUID)
        messenger.debug(f"Firmware version data read: {data}")

        fw = int(data.decode('utf-8'))
        messenger.info(f"Firmware version read: {fw}")

        return fw
    #endregion

    #region HARDWARE VERSION
    async def get_hardware_version(self) -> int:
        """
        Get the hardware version of the connected sensor
        
        :return: An int with the hardware version of the sensor.
        """
        data = await self.read_characteristic(hardwareVersionUUID)
        messenger.debug(f"Hardware version data read: {data}")

        hw = int(data.decode('utf-8'))
        messenger.info(f"Hardware version read: {hw}")

        return hw
    #endregion

    #region SOFTWARE VERSION
    async def get_software_version(self) -> str:
        """
        Get the software version of the connected sensor.
        A string with a single space (" ") denotes a release version.
        
        :return: A str with the software version of the sensor. 
        """
        data = await self.read_characteristic(softwareVersionUUID)
        messenger.debug(f"Software version data read: {data}")

        sw = data.decode('utf-8')
        messenger.info(f"Software version read: {sw}")

        return sw
    #endregion

    #region ALIAS
    async def get_alias(self) -> str:
        """
        Get the alias of the connected sensor.
        
        :return: A str with the alias of the sensor. 
        """
        data = await self.read_characteristic(aliasUUID)
        messenger.debug(f"Alias data read: {data}")

        alias = data.decode('utf-8')
        messenger.info(f"Alias read: {alias}")

        return alias
    
    async def set_alias(
            self, 
            alias: str):
        """
        Set the alias of the connected sensor.
        Max number of characters for alias is 20.
        
        :param alias: A str with the desired alias of the sensor. 
        """
        if not isinstance(alias, str):
            raise ValueError("Alias must be of type <str>")
        
        if len(alias) > 20:
            raise ValueError("Alias length has a maximum length of 20")
        
        messenger.info(f"Alias write: {alias}")

        data = bytearray(alias.encode('utf-8'))
        messenger.debug(f"Alias data write: {data}")

        await self.write_characteristic(aliasUUID, data)
    #endregion

    #region SENSOR ID
    async def get_sensor_id(self) -> int:
        """
        Get the sensor id of the connected sensor.
        
        :return: An int with the sensor id number. 
        """
        data = await self.read_characteristic(sensorIDUUID)
        messenger.debug(f"Sensor ID data read: {data}")

        id = int.from_bytes(data, byteorder='little', signed=False)
        messenger.info(f"Sensor ID read: {id}")

        return id
    
    async def set_sensor_id(
            self, 
            id: int):
        """
        Change the sensor id of the connected sensor.
        This will also result in a change in the model of the sensor and the data recorded and returned from the sensor
        
        :param id: An int with the sensor id number. 
        """
        if not isinstance(id, int):
            raise ValueError("Sensor ID must be of type <int>")
        
        messenger.info(f"Sensor ID write: {id}")

        data = bytearray(id.to_bytes(1, byteorder='little', signed=False))
        messenger.debug(f"Sensor ID data write: {data}")

        await self.write_characteristic(sensorIDUUID, data)
    #endregion   
    
    #region LIVE DATA
    async def get_live_data(
            self,
            timeout=5.0 # Number of seconds to wait before exiting if no response from device
            ) -> Dict:
        """
        Retrieve the live data from the sensor

        :param timeout: Number of seconds to wait before aborting if still haven't received a response from the device

        :return Dict: Returns a dict that include the datapoints with the keys being the name of the datapoints
        """

        # Info for calculating data from the raw values
        sensor_id = await self.get_sensor_id() 
        sensor_class = SENSOR_REGISTRY.get(sensor_id, ApogeeSensor)
        data_labels = sensor_class.data_labels
        data_calculation = sensor_class.calculate_data
        
        live_data = {}
        data_transfer_finished = asyncio.Event()

        def _interpret_live_data(address, uuid, raw_data):
            nonlocal live_data, sensor_class, data_labels, data_calculation

            # Callback for just compiling all the data before sending it to the user
            if uuid != str(liveDataUUID) or address != self._address:
                return
            
            data_packet = bytes(raw_data)

            # Check if data packet is incomplete
            if len(data_packet) < 4:
                messenger.debug(f"Incomplete live data packet. {data_packet}")
                data_transfer_finished.set()
                return

            # Get each datapoint within the current timestamp
            raw_data = []
            for i in range(0, len(data_packet), 4):
                raw = struct.unpack('<i', data_packet[i:(i + 4)])[0]

                # Divide by 10,000 to scale from ten-thousandths to ones
                value = raw / 10000.0

                raw_data.append(value)

            # Calculate data from raw data and add to dict
            live_data = {}
            calculated_data = data_calculation(raw_data)
            for i, value in enumerate(calculated_data):
                key = data_labels[i] if i < len(data_labels) else f"Data_{i}"
                live_data[key] = value

            # Only need to run once
            data_transfer_finished.set()
            return
        
        messenger.info(f"Retrieving live data.")

        await self._start_live_data_notifications(_interpret_live_data)
        await asyncio.wait_for(data_transfer_finished.wait(), timeout=timeout)
        await self._stop_live_data_notifications()

        return live_data
    
    async def _start_live_data_notifications(
            self, 
            notification_callback: Callable[[str, str, bytes], None]
            ):
        """
        Start live data notifications
        *Recommended to use the retrieve_live_data function which handles notifications and callbacks automatically.
        
        :param notification_handler: callable function that receives the live data. The callback should accept the device address, sending uuid, and bytes
        """
        if not callable(notification_callback):
            raise ValueError("The notification_callback must be a callable function.")
    
        messenger.debug(f"Starting live data notifications")

        uuid_str = str(liveDataUUID)
        self.__notification_handlers[uuid_str] = notification_callback

        await self.start_notifications(liveDataUUID, self._notifications_handler)

    async def _stop_live_data_notifications(self):    
        """
        Stop live data notifications
        *Recommended to use the retrieve_live_data function which handles notifications and callbacks automatically.
        """    
        uuid_str = str(liveDataUUID)
        if uuid_str in self.__notification_handlers:
            del self.__notification_handlers[uuid_str]

        messenger.debug(f"Stopping live data notifications")

        await self.stop_notifications(liveDataUUID)
    #endregion

    #region LIVE DATA AVERAGING
    async def get_live_data_averaging_time(self) -> float:
        """
        Get the rolling live data average time in seconds of the connected sensor.
        
        :return: The number of seconds over which live data is averaged. 
        """
        data = await self.read_characteristic(liveDataAverageUUID)
        messenger.debug(f"Live data average data read: {data}")

        raw = int.from_bytes(data, byteorder='little', signed=False)
        average = float(raw) / 4.0 # Comes in units of 0.25 seconds from sensor
        messenger.info(f"Live data average read: {average}")

        return average
    
    async def set_live_data_averaging_time(
            self, 
            average: float):
        """
        Set the rolling live data average time in seconds of the connected sensor.
        
        :param average: A float with the number of seconds for the desired averaging time.
                        Averaging time must be between 0 and 30 seconds, inclusive 
        """
        try:
            avg = float(average)
        except (TypeError, ValueError):
            raise ValueError("Averaging value must be a number")

        if not (0 <= avg <= 30):
            raise ValueError("Averaging value must be 0 - 30, inclusive")
        
        messenger.info(f"Live data average write: {average}")

        value = int(avg * 4) # Convert to int in units of 0.25 seconds for the sensor
        data = bytearray(value.to_bytes(1, byteorder='little', signed=False))
        messenger.debug(f"Live data average data write: {data}")

        await self.write_characteristic(liveDataAverageUUID, data)
    #endregion

    #region LED STATE
    async def get_led_enabled(self) -> bool:
        """
        Get the led state of the connected sensor.
        Only applies to Guardian sensors.
        
        :return: A boolean indicating whether the LEDs are currently enabled.
        """
        data = await self.read_characteristic(LEDStateUUID)
        messenger.debug(f"LED state data read: {data}")

        state = int.from_bytes(data, byteorder='little', signed=False)
        messenger.info(f"LED state read: {state}")

        return bool(state)
    
    async def set_led_enabled(
            self, 
            enabled: bool):
        """
        Set the led state of the connected sensor.
        
        :param enabled: A boolean with the desired led state.
        """
        if not isinstance(enabled, bool):
            raise ValueError("Enabled must be of type <bool>")
        
        messenger.info(f"LED enabled write: {enabled}")

        state = int(enabled)
        data = bytearray(state.to_bytes(1, byteorder='little', signed=False))
        messenger.debug(f"LED enabled data write: {data}")

        await self.write_characteristic(LEDStateUUID, data)
    #endregion

    #region FAN CONTROL
    async def get_fan_state(self) -> Tuple[int, float, int, int]:
        """
        Get the fan state of the connected sensor.
        Only applies to Guardian sensors.

        :return: A tuple containing:
            - duty_cycle (int): The fan's duty cycle percentage.
            - fan_darkness_threshold (float): The darkness threshold value at which fan's duty cycle will be throttled. 0 indicates that the fan will never be throttled.
            - fan_pause_time (int): Time in minutes the fan is paused.
            - rpm (int): Fan rotations per minute.
        """
        data = await self.read_characteristic(fanControlUUID)
        messenger.debug(f"Fan control state data read: {data}")

        duty_cycle = int(data[0])
        fan_darkness_threshold = float(int.from_bytes(data[1:3], byteorder='little', signed=False) / 10)  # Divide by 10 to convert to float
        fan_pause_time = int(data[3])
        rpm = int.from_bytes(data[4:6], byteorder='little', signed=False)
        messenger.info(f"Fan control state read: {(duty_cycle, fan_darkness_threshold, fan_pause_time, rpm)}")

        return (duty_cycle, fan_darkness_threshold, fan_pause_time, rpm)
    
    async def set_fan_duty_cycle(
            self, 
            duty_cycle: int):
        """
        Set the duty cycle for the fan of the connected sensor.
        Only applies to Guardian sensors.
        
        :param duty_cycle: A float representing the desired duty cycle percentage of the fan.
                        duty_cycle must be between 40 and 100, inclusive 
        """
        if not isinstance(duty_cycle, int):
            raise ValueError("Duty cycle must be of type <int>")
        
        if not (40 <= duty_cycle <= 100):
            raise ValueError("Duty cycle must be 40 - 100, inclusive")
        
        messenger.info(f"Fan duty cycle write: {duty_cycle}")
        
        header = 1 # "1" is the header for updating just fan duty cycle
        data = bytearray(header.to_bytes(1, byteorder='little', signed=False)) 
        data.extend(bytearray(duty_cycle.to_bytes(1, byteorder='little', signed=False)))
        messenger.debug(f"Fan duty cycle data write: {data}")

        await self.write_characteristic(fanControlUUID, data)

        
    async def set_fan_pause_time(self, pause_time: int):
        """
        Set the number of minutes to pause the fan of the connected sensor.
        Only applies to Guardian sensors.
        
        :param pause_time: An int representing the number of minutes to pause the fan.
                        pause_time must be between 0 and 250 minutes, inclusive 
        """
        if not isinstance(pause_time, int):
            raise ValueError("Pause time must be of type <int>")
        
        if not (0 <= pause_time <= 250):
            raise ValueError("Pause time must be 0 - 250, inclusive")
        
        messenger.info(f"Fan pause time write: {pause_time}")
        
        header = 4 # "4" is the header for updating just fan pause time
        data = bytearray(header.to_bytes(1, byteorder='little', signed=False)) 
        data.extend(bytearray(pause_time.to_bytes(1, byteorder='little', signed=False)))
        messenger.debug(f"Fan pause time data write: {data}")

        await self.write_characteristic(fanControlUUID, data)    

    async def set_fan_darkness_threshold(self, darkness_threshold: float):
        """
        Set the darkness threshold for the fan of the connected sensor.
        When PAR values fall below this threshold, the fan's duty cycle will be throttled to 40%.
        Only applies to Guardian sensors.
        
        :param darkness_threshold: A float representing the PAR value threshold at which to throttle the fan.
                            darkness_threshold must be between 0 and 250 minutes, inclusive 
        """
        try:
            threshold = float(darkness_threshold)
        except (TypeError, ValueError):
            raise ValueError("Darkness threshold must be a number")
        
        if not (0 <= threshold <= 6553.5):
            raise ValueError("Darkness threshold must be 0 - 6553.5, inclusive")
        
        messenger.info(f"Fan darkness threshold write: {darkness_threshold}")
        
        darkness_threshold_converted = int(threshold * 10)  # Multiply by 10 to convert to int for bluetooth characteristic write
        
        header = 2 # "2" is the header for updating power saving mode
        data = bytearray(header.to_bytes(1, byteorder='little', signed=False)) 
        data.extend(bytearray(darkness_threshold_converted.to_bytes(2, byteorder='little', signed=False)))
        messenger.debug(f"Fan darkness threshold data write: {data}")

        await self.write_characteristic(fanControlUUID, data)
    #endregion

    #region DATA LOGGING
    async def start_data_logging(
            self,
            sampling_interval = 15, # seconds
            logging_interval = 300, # seconds 
            start_time = None, 
            end_time = None, 
            gateway_mode_rate = 0):
        """
        Turn on data logging, set logging parameters, and optionally turn on gateway mode in a single function call.
        
        :param sampling_interval (int): The number of seconds a data sample is taken.
        :param logging_interval (int): The number of seconds a data sample is logged.
        :param start_time (int): (optional) The time using epoch time in seconds at which the sensor did/will start logging. Is None if not logging and not set or not available on firmware version.
        :param end_tme (int): (optional) (firmware version restriction) The time using epoch time in seconds at which the sensor will end logging. Is None if not logging and not set or not available on firmware version.
        :param gateway_mode_rate (int)s: An int indicating how often the sensor will advertise when data is logged. 
                i.e., it advertises once every n data logs, where n correlates with the rate variable
                0 indicates that the sensor will not automatically advertise and requires a manual button press.
        """
            
        await self.set_logging_timing(sampling_interval, logging_interval, start_time, end_time)
        await self.set_logging_active(True)
        await self.set_gateway_mode_rate(gateway_mode_rate)

    async def get_logging_active(self) -> bool:
        """
        Get the logging state of the connected sensor.
        
        :return: A boolean indicating whether the sensor is currently logging.
        """
        data = await self.read_characteristic(dataLoggingControlUUID)
        messenger.debug(f"Data logging control data read: {data}")

        state = int.from_bytes(data, byteorder='little', signed=False)
        messenger.info(f"Data logging control read: {state}")

        return bool(state)
    
    async def set_logging_active(
            self, 
            active: bool):
        """
        Set the logging state of the connected sensor.
        
        :param active: A boolean with the desired logging state.
        """
        if not isinstance(active, bool):
            raise ValueError("Enabled must be of type <bool>")
        
        messenger.info(f"Data logging control write: {active}")
        
        state = int(active)
        data = bytearray(state.to_bytes(1, byteorder='little', signed=False))
        messenger.debug(f"Data logging control data write: {data}")

        await self.write_characteristic(dataLoggingControlUUID, data)

    async def get_logging_timing(self) -> Tuple[int, int, int, int]:
        """
        Get the logging timing of the connected sensor.

        Firmware version restriction: End time is only available on uCache firmware version ≥ 9 or Guardian firmware version ≥ 3

        :return: A tuple containing:
            - sampling_interval (int): The number of seconds a data sample is taken.
            - logging_interval (int): The number of seconds a data sample is logged.
            - start_time (int): (optional) The time using epoch time in seconds at which the sensor did/will start logging. Is None if not logging and not set or not available on firmware version.
            - end_tme (int): (optional) (firmware version restriction) The time using epoch time in seconds at which the sensor will end logging. Is None if not logging and not set or not available on firmware version.
        """
        data = await self.read_characteristic(dataLoggingIntervalsUUID)
        messenger.debug(f"Data logging timing data read: {data}")

        sampling_interval = int.from_bytes(data[0:4], byteorder='little', signed=False)
        logging_interval = int.from_bytes(data[4:8], byteorder='little', signed=False)

        start_time = None
        end_time = None
        if len(data) >= 12:
            start_time = int.from_bytes(data[8:12], byteorder='little', signed=False)
        if len(data) >= 16:
            end_time = int.from_bytes(data[12:416], byteorder='little', signed=False)
        messenger.info(f"Data logging timing read: {(sampling_interval, logging_interval, start_time, end_time)}")

        return (sampling_interval, logging_interval, start_time, end_time)
    
    async def set_logging_timing(
            self, 
            sampling_interval: int, 
            logging_interval: int, 
            start_time: int = None, 
            end_time: int = None):
        """
        Set the logging timing of the connected sensor.

        Firmware version restriction: End time is only available on uCache firmware version ≥ 9 or Guardian firmware version ≥ 3

        :param sampling_interval: An int representing the number of seconds a data sample should be taken. MUST be less than AND an interval of the logging interval variable.
        :param logging_interval: An int representing the number of seconds a data sample should be logged. MUST be greater than AND divisible by the sampling interval variable.
        :param start_time: (optional) An int representing the desired start time in epoch time for data logging. Only available on firmware version...
        :param end_tme: (optional) (firmware version restriction) An int representing the desired end time in epoch time for data logging.  Only available on firmware version...
        """
        if not isinstance(sampling_interval, int):
            raise ValueError("Sampling interval must be of type <int>")
        if not isinstance(logging_interval, int):
            raise ValueError("Logging interval must be of type <int>")
        if not (isinstance(start_time, int) or start_time is None):
            raise ValueError("Start time must be of type <int> or None")
        if not (isinstance(end_time, int) or end_time is None):
            raise ValueError("End time must be of type <int> or None")
        if sampling_interval > logging_interval or logging_interval % sampling_interval != 0:
            raise ValueError("Sampling interval must be less than logging interval and be a factor of the logging interval")
        if (start_time != None and end_time != None and start_time >= end_time):
            raise ValueError("End time must be after start time")
        if (end_time != None and end_time < int(datetime.datetime.now().timestamp())):
            raise ValueError("End time must be after the current time")
        
        messenger.info(f"Data logging control write: {(sampling_interval, logging_interval, start_time, end_time)}")

        data = bytearray(sampling_interval.to_bytes(4, byteorder='little', signed=False))
        data.extend(bytearray(logging_interval.to_bytes(4, byteorder='little', signed=False)))

        if start_time and end_time: 
            data.extend(bytearray(start_time.to_bytes(4, byteorder='little', signed=False)))
            data.extend(bytearray(end_time.to_bytes(4, byteorder='little', signed=False)))
        elif end_time:
            no_start_time = 0 # Entering an end time requires something be entered for start time as well
            data.extend(bytearray(no_start_time.to_bytes(4, byteorder='little', signed=False)))
            data.extend(bytearray(end_time.to_bytes(4, byteorder='little', signed=False)))
        elif start_time:
            data.extend(bytearray(start_time.to_bytes(4, byteorder='little', signed=False)))
        messenger.debug(f"Data logging control data write: {data}")

        await self.write_characteristic(dataLoggingIntervalsUUID, data)
    #endregion
    
    #region GATEWAY MODE
    async def get_gateway_mode_rate(self) -> int:
        """
        Get the gateway mode rate of the connected sensor.
        Not applicable to Guardian sensors.

        Gateway mode provides the functionality for the sensor to advertise periodically, synchronized with data logging.
        The sensor will advertise for up to 10 seconds or until connected.
        
        :return: An int indicating how often the sensor will advertise when data is logged. 
                i.e., it advertises once every n data logs.
                0 indicates that the sensor will not automatically advertise and requires a manual button press.
        """
        data = await self.read_characteristic(dataLogCollectionRateUUID)
        messenger.debug(f"Gateway mode data read: {data}")

        rate = int.from_bytes(data, byteorder='little', signed=False)
        messenger.info(f"Gateway mode read: {rate}")

        return rate
    
    async def set_gateway_mode_rate(
            self, 
            rate: int):
        """
        Set the gateway mode rate of the connected sensor.
        Not applicable to Guardian sensors.

        Gateway mode provides the functionality for the sensor to advertise periodically, synchronized with data logging.
        The sensor will advertise for up to 10 seconds or until connected.
        
        :param rate: An int indicating how often the sensor will advertise when data is logged. 
                i.e., it advertises once every n data logs, where n correlates with the rate variable
                0 indicates that the sensor will not automatically advertise and requires a manual button press.
        """
        if not isinstance(rate, int):
            raise ValueError("Rate must be of type <int>")
        
        if rate < 0:
            raise ValueError("Rate may not be negative")
        
        messenger.info(f"Gateway mode write: {rate}")
        
        data = bytearray(rate.to_bytes(1, byteorder='little', signed=False))
        messenger.debug(f"Gateway mode data write: {data}")

        await self.write_characteristic(dataLogCollectionRateUUID, data)
    #endregion

    #region COEFFICIENTS
    async def get_coefficients(self) -> List[float]:
        """
        Get all the calibration coefficients of the connected sensor.
        The number of calibration coefficients varies by sensor but will be between 1 and 6
        
        :return: A List containing 6 floats for the 6 possible calibration coefficients
        """
        coefficients_1 = await self.get_coefficients_1()
        coefficients_2 = await self.get_coefficients_2()
        coefficients = coefficients_1 + coefficients_2
        return list(coefficients)

    async def get_coefficients_1(self) -> List[float]:
        """
        Get the first 3 calibration coefficients of the connected sensor.
        
        :return: A List containing 3 floats for the first 3 calibration coefficients
        """
        data = await self.read_characteristic(coefficient1UUID)
        messenger.debug(f"Coefficients 1-3 data read: {data}")

        coefficients = struct.unpack('<3f', bytes(data)) 
        messenger.info(f"Coefficients 1-3 read: {coefficients}")

        return list(coefficients)

    async def get_coefficients_2(self) -> List[float]:
        """
        Get the last 3 calibration coefficients of the connected sensor.
        
        :return: A List containing 3 floats for the last 3 calibration coefficients
        """
        data = await self.read_characteristic(coefficient2UUID)
        messenger.debug(f"Coefficients 4-6 data read: {data}")

        coefficients = struct.unpack('<3f', bytes(data)) 
        messenger.info(f"Coefficients 4-6 read: {coefficients}")

        return list(coefficients)
    
    async def set_coefficients(
            self, 
            coefficients: List[float]):
        """
        Set all calibration coefficients of the connected sensor.
        If the desired sensor uses less than 6 calibration coefficients, set the remaining values to 0
        
        :param coefficients: A list of 6 floats containing the calibration coefficients.
        """
        if len(coefficients) != 6:
            raise ValueError("Coefficients must contains exactly 6 values. Use set_coefficients_1 or set_coefficients_2 to set only one group of coefficients")

        coefficients_1 = coefficients[0:3]
        coefficients_2 = coefficients[3:6]

        await self.set_coefficients_1(coefficients_1)
        await self.set_coefficients_2(coefficients_2)

    async def set_coefficients_1(
            self, 
            coefficients: List[float]):
        """
        Set the first 3 calibration coefficients of the connected sensor.
        If the desired sensor uses less than the first 3 calibration coefficients, set the remaining values to 0
        
        :param coefficients: A list of 3 floats containing the first 3 calibration coefficients.
        """
        if len(coefficients) != 3:
            raise ValueError("Coefficients must contains exactly 3 values. Use set_coefficients to set all coefficients at once. Otherwise, fill unused elements with 0")
       
        messenger.info(f"Coefficients 1-3 write: {coefficients}")

        data = struct.pack('<3f', *coefficients) 
        messenger.debug(f"Coefficients 1-3 data write: {data}")

        await self.write_characteristic(coefficient1UUID, data)

    async def set_coefficients_2(
            self, 
            coefficients: List[float]):
        """
        Set the last 3 calibration coefficients of the connected sensor.
        If the desired sensor uses less than the last 3 calibration coefficients, set the remaining values to 0
        
        :param coefficients: A list of 3 floats containing the last 3 calibration coefficients.
        """
        if len(coefficients) != 3:
            raise ValueError("Coefficients must contains exactly 3 values. Use set_coefficients to set all coefficients at once. Otherwise, fill unused elements with 0")

        messenger.info(f"Coefficients 4-6 write: {coefficients}")

        data = struct.pack('<3f', *coefficients)
        messenger.debug(f"Coefficients 4-6 data write: {data}")

        await self.write_characteristic(coefficient2UUID, data)
    #endregion

    #region MODBUS SETTINGS
    async def get_modbus_settings(self) -> Tuple[int, int, str, int]:
        """
        Get the modbus settings of the connected sensor.
        Only applies to Guardian sensors.

        :return: A tuple containing:
            - address (int): An int representing the modbus address of the sensor. 1 - 247
            - baudrate (int): An int representing the baudrate of the sensor. 115200, 57600, 38400, 19200, 9600, or 1200
            - parity (str): A string containing a single character representing the parity of the sensor. 'N'one or 'E'ven.
            - stop_bits (int): An int representing the stop bits of the sensor. 1 or 2
        """
        data = await self.read_characteristic(modbusSettingsUUID)
        messenger.debug(f"Modbus settings data read: {data}")

        address = data[0]
        baudrate_int = data[1]
        parity = data[2]
        stop_bits = data[3]

        parity_mapping = {0: 'N', 2: 'E'}
        parity_str = parity_mapping[parity]

        baudrate_mapping = {0: 115200, 1: 57600, 2: 38400, 3: 19200, 4: 9600, 5: 1200}
        baudrate = baudrate_mapping[baudrate_int]

        messenger.info(f"Modbus settings read: {(address, baudrate, parity_str, stop_bits)}")

        return (address, baudrate, parity_str, stop_bits)
    
    async def set_modbus_settings(self, address: int, baudrate: int, parity: str, stop_bits: int):
        """
        Set the modbus settings of the connected sensor.
        Only applies to Guardian sensors.

        :param address: An int representing the modbus address of the sensor. Valid values are 1 - 247, inclusive.
        :param baudrate: An int representing the baudrate of the sensor. 115200, 57600, 38400, 19200, 9600, or 1200
        :param parity: A string containing a single character representing the parity of the sensor. 'N'one or 'E'ven.
        :param stop_bits: An int representing the stop bits of the sensor. 1 or 2
        """
        if not isinstance(address, int):
            raise ValueError("address must be of type <int>")
        
        if not (1 <= address <= 247):
            raise ValueError("address must be between 1 and 247, inclusive")
        
        messenger.info(f"Modbus settings write: {(address, baudrate, parity, stop_bits)}")
        
        valid_baudrates = {115200, 57600, 38400, 19200, 9600, 1200}
        if baudrate not in valid_baudrates:
            raise ValueError(f"Invalid baudrate {baudrate}. Must be one of {valid_baudrates}.")

        valid_parities = {'N', 'E'}
        if parity not in valid_parities:
            raise ValueError(f"Invalid parity '{parity}'. Must be one of {valid_parities}.")

        if stop_bits not in {1, 2}:
            raise ValueError(f"Invalid stopbits {stop_bits}. Must be 1 or 2.")

        baudrate_mapping = {115200: 0, 57600: 1, 38400: 2, 19200: 3, 9600: 4, 1200: 5}
        baudrate_int = baudrate_mapping[baudrate]

        parity_mapping = {'N': 0, 'E': 2}
        parity_int = parity_mapping[parity]

        data = bytearray(address.to_bytes(1, byteorder='little', signed=False))
        data.extend(bytearray(baudrate_int.to_bytes(1, byteorder='little', signed=False)))
        data.extend(bytearray(parity_int.to_bytes(1, byteorder='little', signed=False)))
        data.extend(bytearray(stop_bits.to_bytes(1, byteorder='little', signed=False)))
        messenger.debug(f"Modbus settings data write: {data}")

        await self.write_characteristic(modbusSettingsUUID, data)
    #endregion

    #region SENSOR TIME
    async def get_sensor_time(self) -> int:
        """
        Get the current time of the sensor in epoch time.

        :return: An int representing epoch time in seconds
        """
        data = await self.read_characteristic(currentTimeUUID)
        messenger.debug(f"Sensor time data read: {data}")

        time = int.from_bytes(data, byteorder='little', signed=False)
        messenger.info(f"Sensor time read: {time}")

        return time
    
    async def set_sensor_time(
            self, 
            time: int):
        """
        Set the time of the sensor to desired time in epoch time.

        :param time: An int representing epoch time in seconds.
        """
        if not isinstance(time, int):
            raise ValueError("Time must be of type <int>")
        
        if time < 0:
            raise ValueError("Time may not be negative")
        
        messenger.info(f"Sensor time write: {time}")
        
        data = bytearray(time.to_bytes(4, byteorder='little', signed=False))
        messenger.debug(f"Sensor time data write: {data}")

        await self.write_characteristic(currentTimeUUID, data)

    async def set_sensor_time_to_current(self):
        """
        Set the time of the sensor to the current time.
        """
        current_time = int(datetime.datetime.now().timestamp())

        data = bytearray(current_time.to_bytes(4, byteorder='little', signed=False))
        await self.write_characteristic(currentTimeUUID, data)
    #endregion

    #region TIME TILL FULL
    async def get_logging_full_time(self) -> int:
        """
        Get the time at which logging will be full in epoch time.
        When full, the sensor will start overwriting the oldest logs in memory.

        :return: An int representing epoch time in seconds at which logging will be full
        """
        data = await self.read_characteristic(timeTillFullUUID)
        messenger.debug(f"Time till full data read: {data}")

        time = int.from_bytes(data, byteorder='little', signed=False)
        messenger.info(f"Time till full read: {time}")

        return time
    #endregion

    #region LAST TRANSFERRED TIMESTAMP
    async def get_last_transferred_timestamp(self) -> int:
        """
        Get the time in epoch time of the last datalog collected using the data transfer characteristic.

        :return: An int representing epoch time in seconds of the last log collected
        """
        data = await self.read_characteristic(lastTransferredTimestampUUID)
        messenger.debug(f"Last timestamp transferred data read: {data}")

        time = int.from_bytes(data, byteorder='little', signed=False)
        messenger.info(f"Last timestamp transferred read: {time}")

        return time
    
    async def set_last_transferred_timestamp(self, 
                                             time: int):
        """
        Set the time in epoch time of the last datalog collected.
        This will cause the sensor to start sending data from this timestamp next time logs are collected.

        :param time: An int representing epoch time in seconds of the last log collected
        """
        if not isinstance(time, int):
            raise ValueError("Time must be of type <int>")
        
        if time < 0:
            raise ValueError("Time may not be negative")
        
        messenger.info(f"Last timestamp transferred write: {time}")
        
        data = bytearray(time.to_bytes(4, byteorder='little', signed=False))
        messenger.debug(f"Last timestamp transferred data write: {data}")
        
        await self.write_characteristic(lastTransferredTimestampUUID, data)
    #endregion

    #region DARK OFFSET
    async def get_dark_offset_calibration_enabled(self) -> bool:
        """
        Check if dark offset calibration is currently in use.
        
        :return: A boolean indicating whether the dark offset calibration is being used.
        """
        data = await self.read_characteristic(darkOffsetUUID)
        messenger.debug(f"Dark offset calibration state data read: {data}")

        state = int.from_bytes(data, byteorder='little', signed=False)
        messenger.info(f"Dark offset calibration state read: {state}")

        return bool(state)

    async def reset_dark_offset_calibration(self):
        """
        Stop using the dark offset calibration
        """
        messenger.info(f"Resetting dark offset calibration")

        data = bytearray([0x00]) # Packet to stop using dark offset calibration
        await self.write_characteristic(darkOffsetUUID, data)

    async def start_dark_offset_calibration(
            self, 
            timeout=45.0 # Number of seconds to wait before exiting if no response from device
            ):
        """
        Start the dark offset calibration process.
        This process takes about 30 seconds.
        The light detector on the sensor should be covered throughout the process

        :param timeout: Number of seconds to wait before aborting if still haven't received a response from the device

        :return bool: Returns a boolean indicating whether the calibration was successful
        """
        success = False
        dark_offset_finished = asyncio.Event()

        def _interpret_data(address, uuid, raw_data):
            nonlocal success

            if uuid != str(darkOffsetUUID) or address != self._address:
                return
            
            data_packet = bytes(raw_data)

            if len(data_packet) > 0 and data_packet[0] == 0x01:
                success = True
                dark_offset_finished.set()
                return
            
        messenger.info(f"Starting dark offset calibration. Light detector should be covered.")
        
        await self._start_dark_offset_notifications(_interpret_data)
        await self._initiate_dark_offset_calibration()
        await asyncio.wait_for(dark_offset_finished.wait(), timeout=timeout)
        await self._stop_dark_offset_notifications()

        return success

    async def _start_dark_offset_notifications(
            self, 
            notification_callback: Callable[[str, str, bytes], None]
            ):
        """
        Start live data notifications
        *Recommended to use the start_dark_offset_calibration function which handles notifications and callbacks automatically.
        
        :param notification_handler: callable function that receives the dark offset notifications. The callback should accept the device address, sending uuid, and bytes
        """
        if not callable(notification_callback):
            raise ValueError("The notification_callback must be a callable function.")
    
        messenger.debug(f"Starting dark offset notifications")

        uuid_str = str(darkOffsetUUID)
        self.__notification_handlers[uuid_str] = notification_callback

        await self.start_notifications(darkOffsetUUID, self._notifications_handler)

    async def _stop_dark_offset_notifications(self):  
        """
        Stop live data notifications
        *Recommended to use the start_dark_offset_calibration function which handles notifications and callbacks automatically.
        """           
        uuid_str = str(darkOffsetUUID)
        if uuid_str in self.__notification_handlers:
            del self.__notification_handlers[uuid_str]

        messenger.debug(f"Stopping dark offset notifications")

        await self.stop_notifications(darkOffsetUUID)

    async def _initiate_dark_offset_calibration(self):
        messenger.debug(f"Initiating dark offset calibration")

        data = bytearray([0x03]) # Packet to start dark offset calibration process
        await self.write_characteristic(darkOffsetUUID, data)
    #endregion

    #region DATA TRANSFER
    async def collect_data(self, 
                           start_time: int = None, 
                           end_time: int = None, 
                           timeout: int = None
                           ) -> List[Dict]:
    
        """
        Collect logged data from the sensor

        :param start_time: (optional) The time, using epoch time in seconds, of the earliest logged data to collect. 
                            A value of None will start from the last log transferred. (See get_last_timestamp_transferred)
        :param end_time: (optional) The time, using epoch time in seconds, of the latest logged data to collect.
                            A value of None will end at last log on device.
        :param timeout: (optional) The maximum number of seconds to collect data before aborting.
                            A value of None will never timeout.

        :return List: Returns a list of dicts that include the timestamp and the datapoints
        """

        if not (isinstance(start_time, int) or start_time is None):
            raise ValueError("Start time must be of type <int> or None")
        if not (isinstance(end_time, int) or end_time is None):
            raise ValueError("End time must be of type <int> or None")
        if not (isinstance(timeout, int) or timeout is None):
            raise ValueError("Timeout must be of type <int> or None")
        if (start_time != None and end_time != None and start_time >= end_time):
            raise ValueError("End time must be after start time")
        
        if start_time:
            await self.set_last_transferred_timestamp(start_time)

        # Info for calculating data from the raw values
        sensor_id = await self.get_sensor_id() 
        sensor_class = SENSOR_REGISTRY.get(sensor_id, ApogeeSensor)
        data_labels = sensor_class.data_labels
        data_calculation = sensor_class.calculate_data

        collected_data = []
        data_transfer_finished = asyncio.Event()
        data_transfer_end_timestamp = end_time if end_time is not None else 4294967295 # Highest number for a 32-bit unsigned int
        
        def _interpret_data_from_transfer(address, uuid, raw_data):
            nonlocal collected_data, sensor_class, data_labels, data_calculation

            # Callback for just compiling all the data before sending it to the user
            if uuid != str(dataLogTransferUUID) or address != self._address:
                return
            
            data_packet = bytes(raw_data)

            # Check if data packet is incomplete or if it is just all "FF" indicating end of data
            if len(data_packet) < 8 or data_packet == b'\xff' * 4:
                messenger.debug(f"End of data or incomplete packet. {data_packet}")
                data_transfer_finished.set()
                return
            
            # Get packet header information
            timestamp = struct.unpack('<I', data_packet[:4])[0]
            interval_between_timestamps = struct.unpack('<H', data_packet[4:6])[0]
            measurements_per_interval = struct.unpack('<B', data_packet[6:7])[0]

            # Separate packet into groups based on timestamp (e.g., groups of 5 datapoints for the Guardian, groups of 1 datapoint for microcache)
            for start_index in range(8, len(data_packet) - 1, 4 * measurements_per_interval):
                if timestamp > data_transfer_end_timestamp:
                    messenger.debug(f"Data timestamp {timestamp} after desired timestamp range. Ending collection.")
                    data_transfer_finished.set()
                    return

                end_index = min(start_index + (4 * measurements_per_interval), len(data_packet))
                grouped_array = data_packet[start_index:end_index]

                # Get each datapoint within the current timestamp
                raw_data = []
                for i in range(0, len(grouped_array), 4):
                    raw = struct.unpack('<i', grouped_array[i:(i + 4)])[0]

                    # Divide by 10,000 to scale from ten-thousandths to ones
                    value = raw / 10000.0

                    raw_data.append(value)

                # Calculate data from raw data and append to collected_data
                values_dict = {}
                calculated_data = data_calculation(raw_data)
                values_dict['Timestamp'] = timestamp
                for i, value in enumerate(calculated_data):
                    key = data_labels[i] if i < len(data_labels) else f"Data_{i}"
                    values_dict[key] = value
                collected_data.append(values_dict)

                # Increment timestamp in case there are multiple logs in a single packet
                timestamp += interval_between_timestamps
        
        messenger.info(f"Collecting data. Start time: {start_time}, End time: {end_time}, Timeout: {timeout}")

        await self._start_data_transfer_notifications(_interpret_data_from_transfer)
        await asyncio.wait_for(data_transfer_finished.wait(), timeout=timeout)
        await self._stop_data_transfer_notifications()

        return collected_data
    
    async def _start_data_transfer_notifications(
            self, 
            notification_callback: Callable[[str, str, bytes], None]
            ):
        """
        Starts data transfer notifications for connected sensor.
        *Recommended to use the collect_data function which handles notifications and callbacks automatically.

        :param notification_callback: The callback function to receive the notifications.
        """
        if not callable(notification_callback):
            raise ValueError("The notification_callback must be a callable function.")
    
        messenger.debug(f"Starting data transfer notifications")

        uuid_str = str(dataLogTransferUUID)
        self.__notification_handlers[uuid_str] = notification_callback

        await self.start_notifications(dataLogTransferUUID, self._notifications_handler)

    async def _stop_data_transfer_notifications(self):    
        """
        Stops data transfer notifications for connected sensor.
        *Recommended to use the collect_data function which handles notifications and callbacks automatically.
        """    
        uuid_str = str(dataLogTransferUUID)
        if uuid_str in self.__notification_handlers:
            del self.__notification_handlers[uuid_str]

        messenger.debug(f"Stopping data transfer notifications")

        await self.stop_notifications(dataLogTransferUUID)
    #endregion
    
