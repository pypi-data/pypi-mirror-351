import bleak
import asyncio
import string
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict

from apogee.bluetooth.SensorClasses import SENSOR_REGISTRY, ApogeeSensor
from apogee.tools.MessageHandler import LoggingMessages

#region DATA STRUCTURES
@dataclass
class _AdvertisingInfo:
    sensor_id: str = ""
    alias: str = ""
    serial_number: str = ""
    type: str = ""
#endregion

class BleScanner:
    #region INIT
    def __init__(self):
        try:
            self._scanner = bleak.BleakScanner(detection_callback=self._did_receive_advertising_data)
            self._scanning = asyncio.Event()
            self._loop = asyncio.get_event_loop()
            
            self._discovered_sensors: Dict[str, Dict[str, str]] = {}

            self.min_duration: int = 3

        except Exception as e:
            raise IOError(e)
    #endregion

    #region GETTERS/SETTERS
    def set_min_scan_time(self, 
                          min_time: int):
        """
        Set minimum scan time before determining if all Apogee sensor packets have been found

        :param min_time: The duration of time in seconds to set the minimum scan time.
        """

        if not type(min_time) == int:
            raise ValueError("Minimum scan time must be of type <int>")
        
        self.min_duration = min_time
        LoggingMessages.info(f"Ble scanner min scan time set to: {min_time}")
    #endregion

    #region SCAN
    async def scan(self, 
                   duration: int = 10, 
                   end_early_if_stable: bool = False
                   ) -> Dict[str, Dict[str, str]]:
        """
        Scan for nearby Apogee sensors

        :param duration: (optional) The duration of time in seconds to scan for Apogee sensors
        :param end_early_if_stable: (optional) If determined that all nearby sensors are found and no more information is needed, end scan early.
                                                 This may still result in a false negative if the initial packet discovery of another sensor did not occur before the set minimum duration
        
        :return: A dictionary mapping MAC addresses (str) to a dictionary containing advertising information.
                The advertising information includes:
                    - sensor_id: The integer representation of the sensor's id number
                    - alias: The assigned alias
                    - serial_number: The serial number
                    - type: The type of sensor
        """

        try:
            # Start scanner
            await self._scanner.start()
            self._scanning.set()
            LoggingMessages.info(f"Starting Ble scan for {duration} seconds. End early if stable set to: {end_early_if_stable}")

            # Set the min and max time for scan duration
            min_time = self._loop.time() + self.min_duration
            max_time = self._loop.time() + duration
            
            # Check every second while scanner is still running
            while self._scanning.is_set():
                await asyncio.sleep(1.0) # Sleep for one second between checks

                # Ensure the min scan duraction has at least elapsed
                if (self._loop.time() > min_time):

                    # Check if scan can end early with no missing packets
                    if end_early_if_stable and self._no_missing_packets():
                        LoggingMessages.debug("Ble scan exiting early due to no new packets found")
                        self._scanning.clear()

                    # Check if scan has continued for max scan duration
                    if self._loop.time() > max_time:
                        LoggingMessages.debug("Ble scan max time elapsed")
                        self._scanning.clear()

        except bleak.exc.BleakDBusError as e:
            raise IOError(f"Error occurred during Ble Scan: {e}")
        
        except Exception as e:
            raise IOError(e)

        finally:
            await self._stop_scan()
            return {
                address: asdict(info) 
                for address, info in self._discovered_sensors.items()
            }

    async def _stop_scan(self):
        await self._scanner.stop()
        LoggingMessages.info("Ble scan stopped")
    #endregion

    #region HANDLE ADVERTISING DATA
    def _did_receive_advertising_data(self, device, advertisement_data):
        # Filter for Apogee's manufacturer ID: 1604 (0x0644)
        if 1604 in advertisement_data.manufacturer_data:
            self._did_discover_apogee_sensor(device, advertisement_data.manufacturer_data[1604])
        
    def _did_discover_apogee_sensor(self, sensor, manufacturer_data):
        LoggingMessages.debug(f"Ble scan - Apogee sensor discovered. {manufacturer_data}")
        address = sensor.address

        if address not in self._discovered_sensors:
            LoggingMessages.debug(f"Ble scan - Adding new sensor with address: {address}")
            self._discovered_sensors[address] = _AdvertisingInfo(address)

        self._interpret_manufacturer_data(address, manufacturer_data)

    def _interpret_manufacturer_data(self, address, manufacturer_data):
        sensor = self._discovered_sensors[address]
        
        # Check which manufacturer data packet was received
        packet_contains_alias_data = self._is_alias_data(manufacturer_data)
        if packet_contains_alias_data:
            self._populate_alias_info(sensor, manufacturer_data)
        else:
            self._populate_sensor_details(sensor, manufacturer_data)
    
    def _populate_alias_info(self, sensor: _AdvertisingInfo, manufacturer_data):
        LoggingMessages.debug(f"Ble scan - Packet contains alias data: {manufacturer_data}")

        sensor.alias = manufacturer_data.decode('utf-8')
    
    def _populate_sensor_details(self, sensor: _AdvertisingInfo, manufacturer_data):
        LoggingMessages.debug(f"Ble scan - Packet contains sensor details data: {manufacturer_data}")

        sensor_id = int(manufacturer_data[-1])
        serial_number = int.from_bytes(manufacturer_data[:2], byteorder='little')

        sensor.type = self._get_sensor_type_from_id(sensor_id)
        sensor.sensor_id = sensor_id
        sensor.serial_number = serial_number
    #endregion

    #region HELPERS
    def _is_alias_data(self, bytes):
        # TODO: Confirm this works on other platforms like Mac, RPi
        try:
            # Check if all characters are printable (either ASCII or Unicode printable)
            decoded_str = bytes.decode("utf-8")
            is_alias = all(c in string.printable or ord(c) > 127 for c in decoded_str)
            return is_alias
        except (UnicodeDecodeError, ValueError) as e:
            return False

    def _no_missing_packets(self):
        for sensor in self._discovered_sensors.values():
            # Determine a packet is missing if info from one of the packets missing
            if (sensor.alias == "") or (sensor.serial_number == "") or (sensor.type == ""):
                return False
        
        return True
    
    def _get_sensor_type_from_id(self, id):
        sensor_class = SENSOR_REGISTRY.get(id, ApogeeSensor)
        return sensor_class.type
    #endregion
