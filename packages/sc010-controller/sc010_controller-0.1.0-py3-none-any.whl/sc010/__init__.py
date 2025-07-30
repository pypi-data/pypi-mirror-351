"""Python Wrapper for SC010 using Telnet"""

from telnetlib import Telnet
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from . import aspeed

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SC010Error(Exception):
    """Base exception for SC010 errors"""

    pass


class ConnectionError(SC010Error):
    """Raised when connection to SC010 fails"""

    pass


class CommandError(SC010Error):
    """Raised when a command fails"""

    pass


class ParseError(SC010Error):
    """Raised when parsing response fails"""

    pass


class DeviceMode(Enum):
    """Device operation modes"""

    RECEIVER = "RECEIVER"
    TRANSMITTER = "TRANSMITTER"
    TRANSCEIVER = "TRANSCEIVER"


@dataclass
class ConnectionConfig:
    """Configuration for SC010 connection"""

    ip: str
    port: int = 23
    timeout: float = 1.0
    max_retries: int = 3
    retry_delay: float = 1.0
    gather_info: bool = True  # Whether to gather device info on connection


# Helpers
def string_to_dict(message: str) -> Dict[str, str]:
    """
    Convert a string response to a dictionary.

    Args:
        message: String response from SC010

    Returns:
        Dictionary of key-value pairs

    Raises:
        ParseError: If string cannot be parsed
    """
    try:
        data_lines = message.strip().split("\n")
        data_dict = {}
        for line in data_lines:
            key, value = line.split(": ")
            data_dict[key.strip()] = value.strip()
        return data_dict
    except Exception as e:
        logger.error(f"Error converting string to dictionary: {e}")
        raise ParseError(f"Failed to parse response: {e}")


def strip_to_dict(message: str) -> Dict[str, Any]:
    """
    Convert a JSON string response to a dictionary.

    Args:
        message: JSON string response from SC010

    Returns:
        Dictionary parsed from JSON

    Raises:
        ParseError: If JSON cannot be parsed
    """
    try:
        brace_position = message.find("{")
        if brace_position != -1:
            stripped_string = message[brace_position:]
        else:
            stripped_string = message
        return json.loads(stripped_string)
    except Exception as e:
        logger.error(f"Error converting string to dictionary: {e}")
        raise ParseError(f"Failed to parse JSON response: {e}")


class Controller:
    def __init__(self, ip: str, config: Optional[ConnectionConfig] = None) -> None:
        """
        Initialize SC010 controller.

        Args:
            ip: IP address of SC010 controller
            config: Optional connection configuration
        """
        self.config = config or ConnectionConfig(ip=ip)
        self.tn: Optional[Telnet] = None
        self.info: Dict[str, Any] = {
            "mac_av": "",
            "mac_ctl": "",
            "serialNumber": "",
            "api_version": "",
            "system_version": "",
            "hostname_av": "",
            "hostname_ctl": "",
        }
        self.connect()

    def _gather_controller_info(self) -> None:
        """
        Gathers controller information and stores it in self.info.
        This includes MAC addresses, serial number, and version information.
        """
        try:
            # Get controller info
            response = self.send("config get controller info")
            if response:
                try:
                    # Find the JSON part of the response
                    start = response.find("[")
                    end = response.rfind("]") + 1
                    if start != -1 and end != -1:
                        json_str = response[start:end]
                        controller_info = json.loads(json_str)[
                            0
                        ]  # Get first item from array

                        # Extract model from hostname (everything before the first hyphen)
                        hostname = controller_info.get("hostname_av", "")
                        model = hostname.split("-")[0] if hostname else ""

                        # Update self.info with controller information
                        self.info = {
                            "serial_number": controller_info.get("serialNumber", ""),
                            "mac_av": controller_info.get("mac_av", ""),
                            "mac_ctl": controller_info.get("mac_ctl", ""),
                            "api_version": "",
                            "system_version": "",
                            "model": model,
                        }
                except (json.JSONDecodeError, IndexError) as e:
                    logger.error(f"Error parsing controller info: {e}")

            # Get version info
            version_info = self.get_version()
            if version_info:
                self.info.update(
                    {
                        "api_version": version_info.get("API version", ""),
                        "system_version": version_info.get("System version", ""),
                    }
                )

            logger.info(
                f"Gathered controller information: {json.dumps(self.info, indent=2)}"
            )

        except Exception as e:
            logger.error(f"Error gathering controller information: {e}")

    def connect(self) -> bool:
        """
        Attempts to connect to the device with retries.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            ConnectionError: If connection fails after max retries
        """
        if self.tn is None:
            self.tn = Telnet()  # Initialize without connecting

        for attempt in range(self.config.max_retries):
            try:
                self.tn.open(
                    self.config.ip, self.config.port, timeout=self.config.timeout
                )

                # Read welcome message with timeout
                try:
                    welcome = self.tn.read_until(
                        b"welcome to use hdip system.", timeout=self.config.timeout
                    )
                    if not welcome:
                        raise ConnectionError("No welcome message received")
                except Exception as e:
                    logger.warning(f"Error reading welcome message: {e}")
                    # Continue anyway as some devices might not send welcome message

                # Send carriage return and read response with timeout
                try:
                    self.tn.write(b"\r\n")
                    response = self.tn.read_until(b"\r\n", timeout=self.config.timeout)
                    if not response:
                        logger.warning("No response to carriage return")
                except Exception as e:
                    logger.warning(f"Error reading response: {e}")
                    # Continue anyway as we're already connected

                logger.info(f"Connected to SC010 at {self.config.ip}")

                # Gather controller information if configured to do so
                if self.config.gather_info:
                    self._gather_controller_info()

                return True
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    import time

                    time.sleep(self.config.retry_delay)
                else:
                    self.tn = None
                    raise ConnectionError(
                        f"Failed to connect to SC010 at {self.config.ip} after {self.config.max_retries} attempts"
                    )
        return False

    def ensure_connection(func):
        """
        Decorator to ensure there's a connection before executing a command.
        Will attempt to reconnect if connection is lost.
        """

        def wrapper(self, *args, **kwargs):
            if not self.tn:
                logger.info("Reconnecting...")
                if not self.connect():
                    raise ConnectionError("Failed to reconnect")
            return func(self, *args, **kwargs)

        return wrapper

    def flush(self) -> None:
        """Flushes any pending responses from the buffer."""
        if self.tn:
            try:
                self.tn.read_very_eager()
            except Exception as e:
                logger.warning(f"Error flushing buffer: {e}")
                self.tn = None

    @ensure_connection
    def send(self, command: str) -> Optional[str]:
        """
        Sends a command to the device.

        Args:
            command: Command to send

        Returns:
            Optional[str]: Response from device or None if command failed

        Raises:
            CommandError: If command fails
        """
        try:
            self.flush()
            self.tn.write(command.encode("ascii") + b"\n")
            response = self.tn.read_until(b"\r\n\r\n")
            return response.decode()
        except Exception as e:
            logger.error(f"Error sending command '{command}': {e}")
            self.tn = None
            raise CommandError(f"Failed to send command: {e}")

    def disconnect(self) -> None:
        """
        Safely closes the Telnet connection if it exists.
        """
        if self.tn is not None:
            try:
                self.tn.close()
                logger.info("Disconnected from SC010")
            except Exception as e:
                logger.error(f"Error closing Telnet connection: {e}")
            finally:
                self.tn = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def send_serial(self, command: str, *true_names: str):
        self.send(
            f'serial -b 115200-8n1 -r on -n on "{command}" {" ".join(true_names)}'
        )

    def _strip_prefix(self, response):
        """Strips everything before the first [ or { character."""
        start_bracket = response.find("[")
        start_brace = response.find("{")
        start = min(
            start_bracket if start_bracket != -1 else float("inf"),
            start_brace if start_brace != -1 else float("inf"),
        )
        if start != float("inf"):
            return response[start:]
        return response

    def get_version(self) -> dict:
        response = self.send("config get version")
        dict = string_to_dict(response)
        self.info["api_version"] = dict.get("API version")
        self.info["system_version"] = dict.get("System version")
        return dict

    def get_system_info(self) -> dict:
        response = self.send("config get system info")
        dict = strip_to_dict(response)
        return dict

    def __str__(self):
        return (
            f"Controller@{self.config.ip} "
            f"System Version:{self.info['system_version']} "
            f"API Version:{self.info['api_version']} "
            f"Serial:{self.info['serialNumber']}"
        )

    # Config Commands
    def set_ip4addr(self, ipaddr=None, netmask=None, gateway=None):
        """
        Configures network settings in LAN(AV) port for communicating with devices
        Note:
        This command is used to set IP address, subnet mask and gateway in LAN(AV) port. You can set two or three of them at the same time or only one each time.
        LAN(AV) port only supports Static IP mode. After network settings are configured, it automatically reboots for the settings to take effect.
        """
        command = "config set "
        if ipaddr is not None:
            command += f"ip4addr {ipaddr}"
        if netmask is not None:
            command += f"netmask {netmask}"
        if gateway is not None:
            command += f"gateway {gateway}"

        return self.send(command)

    def set_ipaddr2(self, ipaddr=None, netmask=None, gateway=None):
        """Configures network settings in LAN(C) port for communicating with devices
        Note:
        This command is used to set IP address, subnet mask and gateway in LAN(AV) port. You can set two or three of them at the same time or only one each time.
        LAN(C) port only supports Static IP mode. After network settings are configured, it automatically reboots for the settings to take effect.
        """
        command = "config set "
        if ipaddr is not None:
            command += f"ip4addr {ipaddr}"
        if netmask is not None:
            command += f"netmask {netmask}"
        if gateway is not None:
            command += f"gateway {gateway}"

        return self.send(command)

    def set_webloginpasswd(self, password):
        """Sets WebUI login password"""
        command = f"config set webloginpasswd {password}"
        return self.send(command)

    def set_telnetpasswd(self, password):
        """Sets Telnet configuration page login password"""
        command = f"config set telnetpasswd {password}"
        return self.send(command)

    def set_telnetpasswd_delete(self):
        """Delete Telnet configuration page login password"""
        command = "config set delete telnetpasswd"
        return self.send(command)

    def set_device_alias(self, hostname, alias):
        """Set's an alias for device and alias can be used in other commands
        instead of hostname"""
        command = f"config set device alias {hostname} {alias}"
        return self.send(command)

    def set_device_remove(self, *hostnames):
        """Remove devices from Controller record. Can remove one or multiple
        devices at once.
        Args:
        Hostname1
        Hostname2
        ..."""
        command = "config set device remove "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def set_device_ip(self, hostname, type, ipaddr=None, netmask=None, gateway=None):
        """Set device network configuration
        Args:
        hostname = ex: IPD5100-341B22800BCD
        type = (autoip, dhcp, static)
                autoip = set the device to a self assigned 169.254.xxx.xxx address
                dhcp = get IP address from DHCP server
                static = need to also provide ipaddr, netmask, gateway
                    ex: IPD5100-341B22800BCD static 192.168.1.20 255.255.255.0 192.168.1.1
        """
        if type.lower() == "static":
            command = (
                f"config set device ip {hostname} {type} {ipaddr} {netmask} {gateway}"
            )
        else:
            command = f"config set device ip {hostname} {type}"
        return self.send(command)

    def set_device_info(self, command, *hostnames):
        """
        Changes a device's one or multiple working parameters in key=value format.
        You can change parameters for multiple devices at one time.

        ex: set_device_info(
            "IPD5100-341B22800BCD",
            "IPD5100-341B22800BCC",
            command="sinkpower.mode=4004"
        )

        Note:
        hostname1 and hostname2 are device names.
        command is a string in key=value format.
        """
        full_command = f"config set device info {command} {' '.join(hostnames)}"
        return self.send(full_command)

    def set_device_audio(self, type, *hostnames):
        """This command is only used for IPE5000,
        configure device hostname1, hostname2's audio input type such as auto, hdmi, analog.
        """
        command = f"config set device audio input type {type} "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def set_device_notify_status(self, on_off, *hostnames):
        """Wakes up device status notify or makes it enter its standby mode. hostname is the device alias;
        Hostname also can be KEY words: ALL_DEV, ALL_TX, ALL_RX, ALL_MRX, ALL_WP, ALL_GW, when hostname is one of the KEY word,
        this command will not include other KEY word and device name.
        Note:
        •	This command is available for IPX2000.
        •	When the system work mode is set as 1, this command will be not available.
        """
        command = f"config set device status notify {on_off} "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def set_device_notify_cec(self, on_off, *hostnames):
        """Wakes up device cec notify system or makes it enter its standby mode. hostname is the device alias;
        Hostname also can be KEY words: ALL_DEV, ALL_TX, ALL_RX,
        when hostname is one of the KEY word, this command will not include other KEY word and device name.
        """
        command = f"config set device cec notify {on_off} "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def set_device_audio_volume(self, action, type, *hostnames):
        """Control device audio volume, the meanings of parameters as follow:
        {mute|unmute|up|down}: up is volume increased; down is volume decreased; mute means mute mode, unmute means mute mode cancelled;
        {hdmi[:n]|analog[:n]|all}: hdmi means that all the HDMI audio outputs, hdmi[:n] means that the number of hdmi audio output is n; analog means that all the analog audio outputs, analog[:n]means that the number of analog audio output is n; all is all of the hdmi and analog audio outputs.
        Note: IPX5000 supports "up" and "down" setting for analog audio only.
        """
        command = f"config set device audio volume {action} {type} "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def set_device_video_source(self, type, hostname):
        """Configure input video signal type for TX; the signal type supports three modes: auto, hdmi and dp.
        Note: This command is available for IPX6000 only.
        """
        command = f"config set device videosource {hostname} {type}"
        return self.send(command)

    def set_device_audio_source(self, type, hostname):
        """Configure HDMI audio source type for RX; the source type supports three modes: hdmi (digital audio, corresponds to audio from DP input or HDMI input), analog and dmix.
        Note: This command is available for IPX6000 only.
        """
        command = f"config set device audiosource {hostname} {type}"
        return self.send(command)

    def set_device_audio_source2(self, type, hostname):
        """Configure audio source type for RX's analog output port; the source type supports two modes: analog and dmix.
        Note: This command is available for IPX6000 only.
        """
        command = f"config set device audio2source {hostname} {type}"
        return self.send(command)

    def set_device_mode(self, mode, hostname):
        """Set device mode
        mode: RECEIVER, TRANSMITTER or TRANSCEIVER"""
        command = (
            f"config set device info device_mode={mode.upper()} {hostname.upper()}"
        )
        return self.send(command)

    def set_session_alias(self, on_off):
        """Open or close the alias mode on the current session, if the value set to be on, then all API command next to it will get alias information feedback, while the feedback got alias. If the value set to be off, then all
        API command next to it will get true name information feedback."""
        command = f"config set session alias {on_off}"
        return self.send(command)

    def set_session_telnet_alias(self, on_off):
        """Configure the Telnet session default alias mode, it will not affect the telnet session that has been linked, only affect the telnet session which is linked later. When the value is on, the API response will describe the device with alias. When the value is off, the API response will describe the device with true name.
        Note: on is by default.
        """
        command = f"config set telnet alias {on_off}"
        return self.send(command)

    def set_session_rs232_alias(self, on_off):
        """Configure uart session alias mode. When it is on, the API response will describe the device with alias, when is off, API response will describe the device with true name.
        Note: on is by default.
        """
        command = f"config set rs-232 alias {on_off}"
        return self.send(command)

    def set_system_ssh(self, on_off):
        """Open or close the system SSH service, off is by default."""
        command = f"config set systemsshservice {on_off}"
        return self.send(command)

    def set_system_workmode(self, status):
        """Set the working mode for the system. By default, it is set as mode 1.
        0: In this mode, all the IP series units except IPX6000 are available for API control.
        1: In this mode, IPX6000 is available for API control, while the other IP series units will be unavailable for API "Notify devices status".
        Note:
        Please reboot the unit for this command setting to take effect.
        status = 0 or 1
        """
        command = f"config set system workmode {status}"
        return self.send(command)

    def set_system_preview(self, fps):
        """Set the total preview framerate for the IP6000 series TX units in the system; the range is [0,30], and the type is integer.
        By default, the framerate is set as 0.
        •	0: The preview function is disabled.
        •	Other value: The preview function for IP6000 TX is enabled; the preview framerate for each TX is calculated by system (=total framerate/quantity of online TX), the minimum framerate is 0.5.
        """
        command = f"config set system preview fps {fps}"
        return self.send(command)

    def set_scene(self, scene):
        """Set scene"""
        return self.send(f"scene active {scene}")

    def get_devicelist(self) -> List[str]:
        """
        Get all device names and return as a sorted list of strings.

        Returns:
            List[str]: Sorted list of device names
        """
        command = "config get devicelist"
        response = self.send(command)
        if not response:
            return []

        # Remove "devicelist is " and split by spaces
        cleaned_str = response.replace("devicelist is ", "").strip()
        device_list = [device for device in cleaned_str.split(" ") if device]
        return sorted(device_list)

    def get_ipsettings(self, lan: int = 1) -> Dict[str, str]:
        """
        Get network settings for LAN(AV) or LAN(C) and return as a dictionary.

        Args:
            lan: 1 or 2
                1. LAN(AV)
                2. LAN(C)

        Returns:
            Dict[str, str]: Dictionary containing network settings
                - port: "LAN(AV)" or "LAN(C)"
                - ip4addr: IP address
                - netmask: Subnet mask
                - gateway: Gateway address
        """
        if lan == 1:
            command = "config get ipsetting"
            port = "LAN(AV)"
        else:
            command = "config get ipsetting2"
            port = "LAN(C)"

        response = self.send(command)
        if not response:
            return {"port": port, "ip4addr": "", "netmask": "", "gateway": ""}

        # Remove the "config get ipsetting" or "config get ipsetting2" part from the response
        if lan == 1:
            response = response.replace("ipsetting is:", "").strip()
        else:
            response = response.replace("ipsetting2 is:", "").strip()

        # Split the response into parts and parse into a dictionary
        settings_dict = {"port": port}
        parts = response.split(" ")
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                key = parts[i]
                value = parts[i + 1]
                settings_dict[key] = value

        return settings_dict

    def get_device_name(self, device: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get device names and their aliases.

        Args:
            device: Optional device name or alias to look up

        Returns:
            List[Dict[str, str]]: Sorted list of dictionaries containing device information
                Each dictionary contains:
                - trueName: Device's true name
                - alias: Device's alias
        """
        if device is None:
            command = "config get name"
        else:
            command = f"config get name {device}"

        response = self.send(command)
        if not response:
            return []

        # Parse the response into a list of dictionaries
        result = []
        lines = response.strip().split("\n")
        for line in lines:
            if "'s alias is " in line:
                true_name, alias = line.split("'s alias is ")
                result.append({"trueName": true_name.strip(), "alias": alias.strip()})

        # Sort the list by trueName
        return sorted(result, key=lambda x: x["trueName"])

    def get_device_info(self, *hostnames) -> dict:
        """Obtains device working parameters in real time.
        Note:
        hostname1 and hostname2 are device names.
        You can get one or multiple devices' working parameters at one time.
        Alias name feature is added from the API v1.7 version
        It may take some time for IP controller to get device information.
        The developer must consider this factor when programming the caller's code.
        Working parameters use Key:Value format. Key is a parameter name and value is its value. For more information, see 3.1 Device Info section.
        """
        command = "config get device info "
        for hostname in hostnames:
            command += hostname + " "
        response = self.send(command)
        logger.debug(f"Raw response for device info: {response}")
        response = self._strip_prefix(response)

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}, response: {response}")
            return {}

    def get_device_status(self, *hostnames) -> dict:
        """Obtains device status in real time.
        Note:
        hostname1 and hostname2 are device names.
        Device status information uses json format.
        Devices' status information is depend on device instead of IP controller, IP controller is only used for passing by.
        """
        command = "config get device status "
        for hostname in hostnames:
            command += hostname + " "

        response = self.send(command)
        logger.debug(f"Raw response for device status: {response}")

        response = self._strip_prefix(response)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}, response: {response}")
            return {}

    def get_device_json(self) -> list:
        """Obtains all device information and returns a list of dictionaries.
        Note:
        "aliasName" represents device alias name (If no alias name appears, it means that this device is not given an alias name).
        "deviceType" represents device type: TX represents transmitter, RX represents receiver, TRX represents transceiver.
        "group" represents a group. One RX unit can only be put in one group. "sequence" in "group" represents the position of this group, which starts with 1. If "sequence" is 0, it means that this group is not arranged in specific order. In this case, you can put this group in a position based on programming.
        "ip" represents device IP address such as 169.254.5.24.
        "online" represents device status, online or offline. "true" represents device is online. "false" represents device is offline.
        "sequence" in a device represents the position of this device in its group, which starts with 1. If "sequence" is 0, it means that this device is not arranged in specific order. In this case, you can put this device in a position based on programming.
        "trueName" represents device true name.
        """
        response = self.send("config get devicejsonstring")
        logger.debug(f"Raw response for device json: {response}")

        response = self._strip_prefix(response)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}, response: {response}")
            return []

    def get_scene_json(self) -> dict:
        """Obtains all scene information.
        Note:
        "group" represents a group. One scene can only be put in one group. "sequence" in" group" represents the position of this group, which starts with 1. If "sequence" is 0, it means that this group is not arranged in specific order. In this case, you can put this group in a position based on programming.
        "layoutseq" represents the position of this scene in video wall.
        "n" and "m" represent the number of rows and columns respectively in a scene.
        "name" represents scene name, such as s
        "rxArray" describes RX in a form of two-dimensional array in a scene.
        "sequence" in a scene represents the position of video wall which contains this scene , which starts with 1. If "sequence" is 0, it means that this video wall is not arranged in specific order. In this case, you can put it in a position based on programming.
        "txListArray" describesTX in a form of two-dimensional array in a scene.
        "vwConfigList" represents the configuration of combination screen in a scene. "name" represents combination screen name, which uses "scene name_ combination screen name" in IP controller (SC010)."pos_row" represents the start place of the first row."pos_col" represents the start place of the first column."row_count" represents the number of rows in combination screen."col_count"represents the number of columns in combination screen.
        """
        command = "config get scenejsonstring"
        response = self.send(command)
        logger.debug(f"Raw response for scene json: {response}")

        response = self._strip_prefix(response)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}, response: {response}")
            return {}

    def get_telnet_alias(self):
        """Get the rs-232 alias mode."""
        command = "config get rs-232 alias"
        return self.send(command)

    def get_system_ssh(self):
        """Get the system SSH service mode."""
        command = "config get system sshservice"
        return self.send(command)

    def remove_device(self, *hostnames):
        """Removes hostnames from controller"""
        command = "config set device remove "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def device_cec_standby(self, *hostnames):
        """Send CEC standy to each host devices"""
        command = "config set device cec standby "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def device_cec_onetouchplay(self, *hostnames):
        """Send CEC one touch play to host devices"""
        command = "config set device cec onetouchplay "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def device_sinkpower(self, on_off, *hostnames):
        """Set display to wake up or enter standby"""
        command = f"config set device sinkpower {on_off} "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def device_reboot(self, *hostnames):
        """Reboot device/s"""
        command = "config set device reboot "
        for hostname in hostnames:
            command += hostname + " "

        return self.send(command)

    def device_factory_restore(self, *hostnames):
        """Factory restore devices"""
        command = "config set device restorefactory "
        for hostname in hostnames:
            command += hostname + " "
        return self.send(command)

    def disconnect_all(self):
        return self.send("matrix set NULL ALL_RX")

    def system_factory_restore(self):
        """Resets Controller to factory settings
        IP address will change 169.254.1.1"""
        command = "config set restorefactory"
        return self.send(command)

    def system_reboot(self):
        """Reboot Controller"""
        command = "config set reboot"
        return self.send(command)

    # Matrix Commands
    def set_matrix(self, segments):
        """
        example: matrix_set("TX1 RX1 RX2","TX2 RX3 RX4")
        Controls the switching of RX to TX.
        Parameters are separated by commas such as segments TX1 RX1 RX2,TX2 RX3 RX4.
        Every segment starts with TX and is followed by some RX which are switched to this TX.
        If a segment starts with TX whose name is "NULL" the followed RX will not decode video. "NULL" is not case sensitive.
        For RX in video wall, this command is used to switch to another TX but will not clear video wall settings.
        If a RX in video wall displays a certain position of TX1's video, after this RX is switched to TX2,
        RX will still display the same position of TX2's video. Other RX in video wall functions in the same way.
        For RX supporting multi-view, this command is used to switch to another TX for full-screen displaying.
        """
        command = "matrix set"
        segments = segments.split(",")  # Split segments by comma
        for i, segment in enumerate(segments):
            command += " " + segment.strip()  # Add each segment to the command
            if (
                i < len(segments) - 1
            ):  # Add comma after each segment except the last one
                command += ","
        return self.send(command)

    def get_matrix(self) -> List[Dict[str, str]]:
        """
        Obtains TX played by RX in matrix.

        Returns:
            List[Dict[str, str]]: List of dictionaries containing matrix information
                Each dictionary contains:
                - tx: Transmitter name
                - rx: Receiver name
        """
        command = "matrix get"
        response = self.send(command)
        if not response:
            return []

        # Parse matrix response into structured format
        matrix_list = []
        lines = response.strip().split("\n")
        for line in lines:
            if "->" in line:
                tx, rx = line.split("->", 1)
                matrix_list.append({"tx": tx.strip(), "rx": rx.strip()})
        return matrix_list

    # CEC
    def cec(self, command, *hosts):
        """Send CEC Command to device"""
        command = f'cec "{command}" '
        for host in hosts:
            command += host + " "
        return self.send(command)

    def find_me(self, seconds, *hosts):
        """Blink LEDS for seconds on device"""
        command = f"config set device findme {seconds} "
        for host in hosts:
            command += host + " "
        return self.send(command)

    def set_vw_add(self, name, nrows, ncols, encoder):
        """Add video wall"""
        command = f"vw add {name} {nrows} {ncols} {encoder}"
        return self.send(command)

    def get_vw(self) -> List[Dict[str, Any]]:
        """
        Get video wall configuration.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing video wall information
                Each dictionary contains:
                - name: Video wall name
                - rows: Number of rows
                - cols: Number of columns
                - encoder: Encoder name
                - layout: Layout information (if available)
        """
        response = self.send("vw get")
        if not response:
            return []

        # Parse video wall response into structured format
        vw_list = []
        current_vw = None

        lines = response.strip().split("\n")
        for line in lines:
            if line.startswith("Video Wall"):
                if current_vw:
                    vw_list.append(current_vw)
                current_vw = {
                    "name": line.split(":", 1)[1].strip(),
                    "rows": 0,
                    "cols": 0,
                    "encoder": "",
                    "layout": {},
                }
            elif current_vw and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "rows":
                    current_vw["rows"] = int(value)
                elif key == "columns":
                    current_vw["cols"] = int(value)
                elif key == "encoder":
                    current_vw["encoder"] = value
                elif key == "layout":
                    current_vw["layout"] = value

        if current_vw:
            vw_list.append(current_vw)

        return vw_list

    def set_vw_change_source(self, vw_name, tx_name):
        """Change source of video wall"""
        command = f"vw change {vw_name} {tx_name}"
        return self.send(command)

    def set_vw_bezelgap(self, vw_name, ow, oh, vw, vh):
        """Set video wall bezel gap"""
        return self.send(f"vw bezelgap {vw_name} {ow} {oh} {vw} {vh}")

    def set_vw_stretch(self, vw_name, type):
        """Set video wall stretch

        type: fit, stretch, fill

        fit: The picture will scale in proportion; it will be displayed proportionally in maximized state; there may be blank space.
        stretch: The picture will scale out of proportion; it will be stretched and shown according to the screen resolution; there's no blank space.
        fill: The picture will scale in proportion to fill the screen; there's no blank space, while part of the picture may not be displayed.
        """
        return self.send(f"vw stretch {vw_name} {type}")

    def set_vw_remove(self, vw_name):
        """Remove video wall"""
        return self.send(f"vw rm {vw_name}")

    def set_vw_add_layout(self, vw_name, nrows, ncols, tx_hostname, *rx_hostnames):
        """Add layout to video wall"""
        command = f"vw add {vw_name} layout {nrows} {ncols} {tx_hostname}"
        for rx_hostname in rx_hostnames:
            command += f" {rx_hostname}"
        return self.send(command)

    def set_vw_change(self, rx_hostname, tx_hostname):
        """Remove RX from video and have it switch to TX in full picture"""
        return self.send(f"vw change {rx_hostname} {tx_hostname}")

    def help(self):
        """Prints out all functions available"""
        functions = [
            func
            for func in dir(self)
            if callable(getattr(self, func))
            and not func.startswith("__")
            and not func.startswith("_")
        ]
        num_functions = len(functions)
        print("Available functions:")
        for i in range(0, num_functions, 2):
            func_name_1 = functions[i]
            func_name_2 = functions[i + 1] if i + 1 < num_functions else ""
            print("{:<30}{:<30}".format(func_name_1, func_name_2))
        print("")

    def remove_offline_devices(self):
        """
        Removes all offline devices by calling controller.remove_device with their trueNames.

        :param controller: The controller instance that has get_device_json and remove_device methods.
        """
        # Get the device JSON from the controller
        device_json = self.get_device_json()

        # Filter for offline devices and extract their trueNames
        offline_device_names = [
            device["trueName"] for device in device_json if not device["online"]
        ]

        if offline_device_names:
            # Convert the list of names to a string if required by your controller.remove_device method
            # Assuming remove_device takes a list of hostnames; adjust if it takes a different format
            self.remove_device(*offline_device_names)
            print(f"Removed offline devices: {', '.join(offline_device_names)}")
        else:
            print("No offline devices found to remove.")

    def get_controller_info(self) -> Dict[str, Any]:
        """
        Get the stored controller information.

        Returns:
            Dict[str, Any]: Dictionary containing controller information
                - mac_av: MAC address of AV port
                - mac_ctl: MAC address of control port
                - serialNumber: Device serial number
                - api_version: API version
                - system_version: System version
                - hostname_av: Hostname of AV port
                - hostname_ctl: Hostname of control port
        """
        return self.info.copy()  # Return a copy to prevent modification

    @classmethod
    def find_controller(cls) -> Optional[Dict[str, str]]:
        """
        Find SC010 controller on the network.

        Returns:
            Optional[Dict[str, str]]: Dictionary with 'ip' and 'mac' keys if found, None otherwise
        """
        try:
            devices = aspeed.search_nodes()

            for device in devices:
                if device["HOSTNAME"].startswith("SC010"):
                    # Extract MAC address from hostname
                    mac = (
                        device["HOSTNAME"].split("-")[1]
                        if "-" in device["HOSTNAME"]
                        else ""
                    )
                    return {"ip": device["ADDRESS"], "mac": mac}

            return None
        except ImportError:
            logger.error("aspeed module not found")
            return None
        except Exception as e:
            logger.error(f"Error finding controller: {e}")
            return None


if __name__ == "__main__":
    # Example configuration
    config = ConnectionConfig(
        ip="192.168.50.200",
        timeout=2.0,
        max_retries=3,
        retry_delay=1.0,
        gather_info=True,  # Enable automatic info gathering on connection
    )

    try:
        # Using context manager for automatic connection/disconnection
        with Controller(config=config) as controller:
            # Get and display controller information
            info = controller.get_controller_info()
            logger.info("Controller Information:")
            for key, value in info.items():
                logger.info(f"  {key}: {value}")

            # Send CEC commands to TVs
            tv_devices = ["TV1-6000", "TV2-6000", "TV3-6000", "TV4-6000"]

            # Power on sequence
            controller.send('cec "1f 9d" ' + " ".join(tv_devices))
            controller.send('cec "4f 82 40 00" ' + " ".join(tv_devices))
            controller.send('cec "ff 36" ' + " ".join(tv_devices))

            # Power off sequence
            controller.send("config set device sinkpower off " + " ".join(tv_devices))

    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
    except CommandError as e:
        logger.error(f"Command failed: {e}")
    except ParseError as e:
        logger.error(f"Parse error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
