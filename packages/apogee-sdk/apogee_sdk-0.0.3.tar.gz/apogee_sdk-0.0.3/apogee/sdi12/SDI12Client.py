from apogee.SerialClient import SerialClient

class SDI12Client(SerialClient):
    
    #region CONSTRUCTOR
    def __init__(self,
                 port: str,
                 baudrate: int = 1200,
                 timeout: int = 2,
                 auto_caps_cmd: bool = True
                 ):
        """
        :param port: comport name of connected serial device
        :param baudrate: (optional) 115200, 57600, 38400, 1920, 9600, 1200
        :param timeout: (optional) No response timeout in seconds
        :param auto_caps_cmd: (optional) Automatically capitalize command (excluding device address)
        """

        self._auto_capitalize_cmd = auto_caps_cmd

        super().__init__(port, baudrate, timeout)
    #endregion
    
    def _send_cmd(self, cmd):
        if self._auto_capitalize_cmd:
            cmd = cmd[0] + cmd[1:].upper()

        if cmd[-1] != '!':
            cmd += '!'

        print(cmd)
        command = (cmd).encode()
        print(command)
        super()._send_cmd(command)