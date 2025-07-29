from serial import Serial

class SerialClient():
    #region CONSTRUCTOR
    def __init__(self, port, baudrate, timeout):
        self._validate_port(port)
        self._validate_baudrate(baudrate)
        self._validate_timeout(timeout)

        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        
        self._encoding = 'latin-1'
        self._connected = False
        self._serial_device = None
        
        self.open()
    
    def __del__(self):
        self.close()
    #endregion
    
    #region VALIDATION
    def _validate_baudrate(self, baudrate):
        valid_baudrates = {115200, 57600, 38400, 19200, 9600, 1200}
        if baudrate not in valid_baudrates:
            raise ValueError(f"Invalid baudrate {baudrate}. Must be one of {valid_baudrates}.")
    
    def _validate_timeout(self, timeout):
        if not isinstance(timeout, int):
            raise TypeError(f"Invalid timeout {timeout}. Must be an integer.")
        if timeout < 0:
            raise ValueError(f"Invalid timeout {timeout}. Must be a non-negative integer.")

    def _validate_port(self, port):
        if not isinstance(port, str):
            raise TypeError(f"Invalid port {port}. Must be a string.")    
    #endregion

    #region PROPERTIES
    @property
    def connected(self):
        return self._connected
    
    @connected.setter
    def connected(self, value):
        if self._connected != value:
            self._connected = value
    #endregion

    #region CONNECTION MANAGEMENT
    def open(self):
        try:
            self._serial_device = Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout
                )
            self.connected = True     
        except Exception as e:
            raise IOError(e) 
    
    def close(self):
        try:
            self._serial_device.close()
            self.connected = False
            self._serial_device = None
        except Exception as e:
            raise IOError(e)
    #endregion

    #region COMMUNICATION
    def _send_cmd(self, cmd):
        try:
            if self.connected:
                self._serial_device.flush()
                self._serial_device.write(cmd)
        except Exception as e:
            raise IOError(e)
            
    def _read_response(self):
        try:
            response = self._serial_device.readline()
            return response
        except Exception as e:
            raise IOError(e)
    
    def _send_cmd_and_await_response(self, cmd, no_response_expected = False):
        try:
            if self.connected:
                self._serial_device.reset_input_buffer()
                self._send_cmd(cmd)

                if not no_response_expected:
                    response = self._serial_device.readline()
                    return response
                else:
                    return ""
        except Exception as e:
            raise IOError(e)
    #endregion