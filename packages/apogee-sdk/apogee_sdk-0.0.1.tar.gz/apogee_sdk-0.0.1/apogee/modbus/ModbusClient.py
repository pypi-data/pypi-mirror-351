import struct
from numbers import Number

from apogee.SerialClient import SerialClient
from apogee.modbus.ModbusSensorRegisterDict import ModbusSensorModel, Sensor_Registers

class ModbusClient(SerialClient):
    
    #region CONSTRUCTOR
    def __init__(self,
                 port: str,
                 baudrate: int = 9600,
                 stopbits: int = 1,
                 parity: str = 'N',
                 bytesize: int = 8,
                 protocol: str = 'RS-485',
                 timeout: int = 1,
                 skip_AC422_setup: bool = False 
                 ):
        """
        :param port: comport name of connected serial device
        :param baudrate: (optional) 115200, 57600, 38400, 1920, 9600
        :param stopbits: (optional) 0, 1, 2
        :param parity: (optional) 'N'one, 'O'dd, or 'E'ven 
        :param bytesize: (optional) 7, 8
        :param protocol: (optional) RS-232, RS-485
        :param timeout: (optional) No response timeout in seconds
        :param skip_AC422_setup: (optional) If True, will not configure AC-422 during initialization. May be used when not using AC-422.
        """
        self._validate_stopbits(stopbits)
        self._validate_parity(parity)
        self._validate_bytesize(bytesize)
        self._validate_protocol(protocol)

        self._stopbits = stopbits
        self._parity = parity
        self._bytesize = bytesize
        self._protocol = protocol

        super().__init__(port, baudrate, timeout)
        if not skip_AC422_setup:
            self._configure_modbus_interface_type()
    #endregion

    #region VALIDATION
    def _validate_stopbits(self, stop_bits):
        if stop_bits not in {1, 2}:
            raise ValueError(f"Invalid stopbits {stop_bits}. Must be 1 or 2.")

    def _validate_parity(self, parity):
        valid_parities = {'N', 'O', 'E'}
        if parity not in valid_parities:
            raise ValueError(f"Invalid parity '{parity}'. Must be one of {valid_parities}.")

    def _validate_bytesize(self, bytesize):
        if bytesize not in {7, 8}:
            raise ValueError(f"Invalid bytesize {bytesize}. Must be one of 7 or 8.")

    def _validate_protocol(self, protocol):
        valid_protocols = {'RS-232', 'RS-485'}
        if protocol not in valid_protocols:
            raise ValueError(f"Invalid protocol '{protocol}'. Must be one of {valid_protocols}.")
    #endregion

    #region CONFIGURATION
    def _configure_modbus_interface_type(self):
         # Send command to AC-422 to configure it for proper modbus communication
        parity_map = {'N': 0, 'O': 1, 'E': 2}
        protocol_map = {'RS-232': 0, 'RS-485': 1}

        cmd = '\x00\xff'.encode(self._encoding)
        cmd += struct.pack('>I', self._baudrate)
        cmd += chr(self._stopbits).encode(self._encoding)
        cmd += chr(parity_map.get(self._parity, 2)).encode(self._encoding)
        cmd += chr(protocol_map.get(self._protocol, 1)).encode(self._encoding)

        self._serial_device.write(cmd)
        response = self._serial_device.read()
        success = int.from_bytes(response)

        if not success:
            raise IOError("Error setting configuration for AC-422")
    #endregion
    
    #region CMD
    def _build_modbus_command(self, device_address, function_code, start_address, num_registers, values = None):
        # Pack the Modbus request into a bytearray, calucate crc, append crc to end of command
        if values is not None:
            pass


        command = struct.pack('>B B H H', device_address, function_code, start_address, num_registers)
        crc = self._calculate_modbus_crc(command) 
        command += struct.pack('<H', crc)
        
        return command

    def _calculate_modbus_crc(self, msg):
        # Somehow calculates the crc for the modbus command
        # https://stackoverflow.com/questions/69369408/calculating-crc16-in-python-for-modbus
        crc = 0xFFFF
        for n in range(len(msg)):
            crc ^= msg[n]
            for i in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
    #endregion

    #region COMMANDS
    def write_to_registers(self,
            device_address: int, # Slave Address
            start_address: int,
            number_of_registers: int,
            values: list[Number],
            no_response_expected: bool = False
            ):
        """
        Write registers (code 0x16)

        :param device_address: Modbus slave ID
        :param start_address: Start address to write to
        :param number_of_registers: Number of registers to read
        :param values: List of values to write
        :param no_response_expected: (optional) The client will not expect a response to the request

        This function is used to write a block of contiguous registers.
        """
        if not type(device_address) == int:
            raise ValueError("device_address must be of type <int>")
        
        if not type(start_address) == int:
            raise ValueError("start_address must be of type <int>")
        
        if not type(number_of_registers) == int:
            raise ValueError("number_of_registers must be of type <int>")
        
        function_code = 16
        # TODO: Figure out writing
        cmd = self._build_modbus_command(device_address, function_code, start_address, values)
        self._send_cmd_and_await_response(cmd)
        
    def read_from_registers(self,
            device_address: int, # Slave Address
            start_address: int,
            number_of_registers: int,
            no_response_expected: bool = False
            ):
        """
        Read holding registers (code 0x03).

        :param device_address: Modbus slave ID 
        :param start_address: Start address to read from
        :param number_of_registers: Number of registers to read
        :param no_response_expected: (optional) The client will not expect a response to the request

        This function is used to read the contents of a contiguous block
        of holding registers in a remote device. The Request specifies the
        starting register address and the number of registers.
        """   
        if not type(device_address) == int:
            raise ValueError("device_address must be of type <int>")
        
        if not type(start_address) == int:
            raise ValueError("start_address must be of type <int>")
        
        if not type(number_of_registers) == int:
            raise ValueError("number_of_registers must be of type <int>")
        
        function_code = 3
        cmd = self._build_modbus_command(device_address, function_code, start_address, number_of_registers)
        self._send_cmd_and_await_response(cmd)

    def retrieve_sensor_value(self, 
            device_address: int, # Slave Address
            sensor_model: ModbusSensorModel, 
            register_name: str
            ):
        """
        :param device_address: Modbus slave ID
        :param sensor_model: First two letters of sensor model from the ModbusSensorModel enum 
        :param register_name: The name of the value. Must be in the Sensor_Register dictionary

        This function is used to retrieve the desired value without needing to
        know the holding register or how to convert the data to the proper format.
        """   
        if sensor_model not in Sensor_Registers:
            raise ValueError(f"Sensor model '{sensor_model.value}' not found.")

        sensor_data = self.register_dict[sensor_model]

        if register_name not in sensor_data:
            raise ValueError(f"Value '{register_name}' not found for sensor model '{sensor_model.value}'.")

        register = sensor_data[register_name]
        
        # TODO: Confirm endianness
        response = self.read_from_registers(device_address, register, 2, False)
        value = self.convert_bytes_to_float(response)

        return value
    #endregion 
    
    #region HELPERS
    def convert_bytes_to_float(self, bytestring, big_endian: bool = True):
        unpack_format = '>f' if big_endian else '<f'
        float_value = struct.unpack(unpack_format, bytestring)[0]
        return float_value
    #endregion