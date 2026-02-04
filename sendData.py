import socket
from packet_spec import PacketType, TelemetryPacketSubType as SensorTypeID
import config
import sys
from numpy import int32
from labjack import ljm # type: ignore

class sendData:
    def __init__(self, ip: str, port: int, channels: list[str], config: dict[str, config.Sensor]):
        self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket_udp.bind(("192.168.0.213", 50003))  # Bind to any available port
        self.mc_addr = ip
        self.port = port
        self.config = config
        self.channels = channels

    def send_packet(self, dataConverted: list[int32], timestamp: float) -> None:
        header = PacketType.TELEMETRY.value
        for i in range(len(self.channels)):
            try:
                sensor = self.config[self.channels[i]]
                byte_data = header.to_bytes(1, 'little', signed=False)
                byte_data += sensor.sensor_type_id.value.to_bytes(1, 'little', signed=False)
                byte_data += int(timestamp).to_bytes(4, 'little', signed=False)
                # clamp the sensor value to the 4-byte range (signed or unsigned) to avoid overflow
                raw_value = int(dataConverted[i])
                if sensor.sensor_type_id == SensorTypeID.THRUST:
                    signed_flag = False
                    min_v, max_v = 0, 0xFFFFFFFF
                else:
                    signed_flag = True
                    min_v, max_v = -(4**15), 4**15 - 1
                clamped = max(min_v, min(max_v, raw_value))
                byte_data += int(clamped).to_bytes(4, 'little', signed=signed_flag)
                byte_data += sensor.sensor_id.to_bytes(1, 'little', signed=False)
                self.socket_udp.sendto(byte_data, (self.mc_addr, self.port))
            except Exception:
                print(f"Error sending data for channel {self.channels[i]}")
                print(f"Data: {dataConverted[i]}")
                ljm.closeAll()
                print(sys.exc_info())