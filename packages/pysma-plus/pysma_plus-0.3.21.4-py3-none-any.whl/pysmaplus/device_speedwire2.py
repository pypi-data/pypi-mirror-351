import asyncio
import copy
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


from .const import Identifier, SMATagList
from .device import Device, DeviceInformation, DiscoveryInformation
from .exceptions import (
    SmaAuthenticationException,
    SmaConnectionException,
    SmaReadException,
    SmaWriteException,
)
from .helpers import isInteger, splitUrl
from .sensor import Sensor, Sensor_Range, Sensors
from .definitions_speedwire import (
    SpeedwireFrame,
    commands,
    responseDef,
    speedwireHeader,
    speedwireHeader6065,
)
_LOGGER = logging.getLogger(__name__)

class UDPClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, loop, on_response, _host, _password, _group):
        self.loop = loop
        self.on_response = on_response
        self.transport = None
        self.response_received = asyncio.Event()
        self.target_ip = _host
        self._password = _password
        self._group = _group
        self.target_port = 9255

    def connection_made(self, transport):
        self.transport = transport
   #     self.loop.create_task(self.send_message_loop())
        
    # async def send_message_loop(self):
    #     while True:
    #         print(f"Sending: {self.message}")
    #         self.transport.sendto(self.message.encode(), (self.target_ip, self.target_port))
    #         self.response_received.clear()
    #         try:
    #             await asyncio.wait_for(self.response_received.wait(), timeout=2)
    #         except asyncio.TimeoutError:
    #             print("No response received within timeout, resending...")
    #         await asyncio.sleep(10)  # Pause before sending the next message

    def datagram_received(self, data, addr):
        print(f"Received: {data.decode()} from {addr}")
        self.on_response(data.decode())
        self.response_received.set()  # Mark response as received

class SMAspeedwireINVV2(Device):
    """ """
    def __init__(self, host: str, group: str, password: Optional[str]):
        self._host = host
        self._group = group
        self._password = password
        self._transport = None
        self._protocol = None
        if group not in ["user", "installer"]:
            raise KeyError(f"Invalid user type: {group} (user or installer)")
    
    async def run(self):
        loop = asyncio.get_running_loop()
        on_response = lambda response: print(f"Processed response: {response}")
        message = "Hallo World"
        target_ip = "127.0.0.1"
        target_port = 9522
        self._connect = loop.create_datagram_endpoint(
            lambda: UDPClientProtocol(message, loop, on_response, target_ip, target_port),
            remote_addr=(target_ip, target_port)
        )
        self._transport, self._protocol = await connect

        # try:
        #     await asyncio.sleep(float('inf'))  # Run indefinitely
        # finally:
        #     transport.close()


        # destination = splitUrl(ip)
        # _LOGGER.debug(f"SHM {ip} => {destination}")
        # self._ip = destination["host"]
        # self._sensorValues: Dict[str, int] = {}
        # if password:
        #     if not isInteger(password):
        #         raise SmaConnectionException(
        #             "Password/Grid Guard Code must be a number."
        #         )
        #     self._ggc = int(password)
        # else:
        #     self._ggc = 0
        # self._device_list: Dict[str, DeviceInformation] = {}
        # self._client: AsyncModbusTcpClient

    async def get_sensors(self, deviceID: str | None = None) -> Sensors:
        """Returns a list of all supported sensors"""
        device_sensors = Sensors()
        # for s in modusbus2sensorList:
        #     device_sensors.add(copy.copy(s.sensor))
        return device_sensors


    # async def _read_sensor(self, sensorDef: modusbus2sensor):
    #     """Read a modbus register based on the sensorDefinition"""
    #     return await self.read_modbus(
    #         sensorDef.addr, sensorDef.slaveid, sensorDef.valueFormat
    #     )


    async def new_session(self) -> bool:
        """Starts a new session"""


        if self._transport:
            self._transport.close()

        loop = asyncio.get_running_loop()
        on_response = lambda response: print(f"Processed response: {response}")
        # message = "Hallo World"
        # target_ip = "127.0.0.1"

        target_port = 12456
        groupidx = ["user", "installer"].index(self._group) == 1
        self.speedwire = SpeedwireFrame()

#sw1  534d4100000402a000000001003a001060650ea0  ffffffffffff0001 ed0022 1902230001000000000180  0c04fdff070000008403000 03b7 bdd6700000000d0f7f5edb9bdc0b88888888800000000
#sw2  534d4100000402a000000001003a001060650ea0  ffffffffffff0001 ed0022 1902230001000000000180  0c04fdff070000008403000 0bc7 fdd6700000000d0f7f5edb9bdc0b88888888800000000
#this 534d4100000402a000000001003a001060650ea0--ffffffffffff0001 7d0023 1902230001000000000180--0c04fdff070000008403000 0a180dd6700000000d0f7f5edb9bdc0b88888888800000000
#this 534d4100000402a000000001003a001060650ea0ffffffffffff0001 7d0023 19022300010000000001800c04fdff070000008403000 06c7 fdd6700000000d0f7f5edb9bdc0b88888888800000000
        msg = self.speedwire.getLoginFrame(self._password, 0x23021923, groupidx)
#        print(msg.hex())

        self._connect = loop.create_datagram_endpoint(
            lambda: UDPClientProtocol(loop, on_response, self._host, self._password, self._group),
            remote_addr=(self._host, 9522)
        )
        self._transport, self._protocol = await self._connect


        # self._client = AsyncModbusTcpClient(str(self._ip))  # Create client object
        # connected = await self._client.connect()
        # if not connected:
        #     raise SmaConnectionException(f"Could not connect to {self._ip}:502")

        # device = await self.read_modbus(30053, 1, "u32")
        # if device != 9343:
        #     raise SmaConnectionException(f"No Sunny Home Manager 2 found. ({device})")

        # ggcStatus = await self.read_modbus(43090, 1, "u32")
        # _LOGGER.debug(f"GGC Code {ggcStatus}")
        # if ggcStatus == 0:
        #     await self._login()
        # ggcStatus = await self.read_modbus(43090, 1, "u32")
        # _LOGGER.debug(f"After Login -- GGC Code {ggcStatus}")
        # if ggcStatus == 0:
        #     raise SmaAuthenticationException("Grid Guard Code is not valid!")
        return True

    async def device_info(self) -> dict:
        """Read device info and return the results.

        Returns:
            dict: dict containing serial, name, type, manufacturer and sw_version
        """
        di = await self.device_list()
        return list(di.values())[0].asDict()

    async def device_list(self) -> dict[str, DeviceInformation]:
        """List of all devices"""
        self._device_list = {}
        # serial = str(await self.read_modbus(30005, 1, "u32"))
        # device = await self.read_modbus(30053, 1, "u32")
        # vendor = await self.read_modbus(30055, 1, "u32")
        # deviceName = SMATagList.get(device, f"Unknown Device {device}")
        # vendorName = SMATagList.get(vendor, f"Unknown Vendor {vendor}")
        # self._device_list[serial] = DeviceInformation(
        #     serial, serial, deviceName, deviceName, vendorName, ""
        # )
        return self._device_list

    async def read(self, sensors: Sensors, deviceID: str | None = None) -> bool:
        """Updates all sensors"""
        notfound = []
        # for sensor in sensors:
        #     #            print(sensor)
        #     if sensor.key not in modbusDict:
        #         notfound.append(sensor.key)
        #         continue
        #     sensorDef = modbusDict[sensor.key]
        #     value = None
        #     if not sensorDef.writeonly:
        #         value = await self._read_sensor(sensorDef)
        #         if sensor.factor and sensor.factor != 1:
        #             value = round(value / sensor.factor, 4)
        #         sensor.value = value
        #         if sensor.mapper:
        #             sensor.mapped_value = sensor.mapper.get(value, str(value))
        #     else:
        #         if sensor.key in self._sensorValues:
        #             sensor.value = self._sensorValues[sensor.key]
        #         else:
        #             sensor.value = None
        #     if sensorDef.range:
        #         sensor.range = sensorDef.range

        # if notfound:
        #     _LOGGER.info(
        #         "No values for sensors: %s",
        #         ",".join(notfound),
        #     )

        return True

    async def close_session(self) -> None:
        """Closes the session"""

    async def detect(self, ip: str) -> List[DiscoveryInformation]:
        """Try to detect SMA devices"""
        rets = []
        # try:
        #     di = DiscoveryInformation()
        #     rets.append(di)
        #     di.tested_endpoints = ip
        #     di.remark = "needs Installer Grid Guard Code. Usage not recommended."

        #     self._client = AsyncModbusTcpClient(str(self._ip))
        #     connected = await self._client.connect()
        #     if not connected:
        #         raise SmaConnectionException(f"Could not connect to {self._ip}:502")

        #     device = await self.read_modbus(30053, 1, "u32")
        #     if device != 9343:
        #         raise SmaConnectionException(
        #             f"No Sunny Home Manager 2 found. ({device})"
        #         )
        #     di.status = "found"
        #     di.exception = None
        # except Exception as e:  # pylint: disable=broad-exception-caught
        #     di.status = "failed"
        #     di.exception = e
        return rets

    async def get_debug(self) -> Dict[str, Any]:
        """Return a dict with all debug information."""
        return {}

    def set_options(self, options: Dict[str, Any]) -> None:
        """Set options"""

    async def set_parameter(
        self, sensor: Sensor, value: int, deviceID: str | None = None
    ) -> None:
        pass