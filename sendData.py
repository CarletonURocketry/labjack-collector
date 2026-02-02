import socket
from packet_spec import PacketType, TelemetryPacketSubType as SensorTypeID
import config

class sendData:
    def __init__(self, ip: str, port: int, channels: list[str], config: dict[str, config.Sensor]):
        self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mc_addr = ip
        self.port = port
        self.config = config
        self.channels = channels

    def send_packet(self, dataConverted: list[float], timestamp: float) -> None:
        header = PacketType.TELEMETRY.value
        for i in range(len(self.channels)):
            sensor = self.config[self.channels[i]]
            byte_data = header.to_bytes(1, 'little', signed=False)
            byte_data += sensor.sensor_type_id.value.to_bytes(1, 'little', signed=False)
            byte_data += int(timestamp).to_bytes(4, 'little', signed=False)
            if sensor.sensor_type_id == SensorTypeID.THRUST:
                byte_data += int(dataConverted[i]).to_bytes(2, 'little', signed=False)
            else:
                byte_data += int(dataConverted[i]).to_bytes(2, 'little', signed=True)
            byte_data += sensor.sensor_id.to_bytes(1, 'little', signed=False)
            self.socket_udp.sendto(byte_data, (self.mc_addr, self.port))