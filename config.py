"""Config file containing the configuration of the LabJack
"""
import dataConversions
from packet_spec import TelemetryPacketSubType as SensorTypeID

class Sensor:
    def __init__(self, name: str, sensor_type_id: SensorTypeID, sensor_id: int, convertClass: dataConversions.genericAmplifier):
        self.name = name
        self.sensor_type_id = sensor_type_id
        self.sensor_id = sensor_id
        self.convertClass = convertClass

channelToSensor: dict[str, Sensor] = {
    "AIN0": Sensor("T5", SensorTypeID.TEMPERATURE, 5, dataConversions.genericAmplifier((0, 1300*1000), (0, 10))), # Placeholder (mdegC, V)
    "AIN1": Sensor("THRUST", SensorTypeID.THRUST, 0, dataConversions.genericAmplifier((0, 10000), (0, 5))),  # Placeholder (N, V)
    "AIN3": Sensor("MASS", SensorTypeID.MASS, 0, dataConversions.genericAmplifier((0, 100*1000), (0, 5))), # (g, V)
    "AIN2": Sensor("P1", SensorTypeID.PRESSURE, 1, dataConversions.genericAmplifier((0, 1000*1000), (0, 5))), # (mPSI, V)
    "AIN4": Sensor("P2", SensorTypeID.PRESSURE, 2, dataConversions.genericAmplifier((0, 1000*1000), (0, 5))), # (mPSI, V)
    "AIN13": Sensor("P3", SensorTypeID.PRESSURE, 3, dataConversions.genericAmplifier((0, 1000*1000), (1, 5))), # (mPSI, V)
    "AIN6": Sensor("P4", SensorTypeID.PRESSURE, 4, dataConversions.genericAmplifier((0, 1000*1000), (0, 5))), # (mPSI, V)
    "AIN7": Sensor("P5", SensorTypeID.PRESSURE, 5, dataConversions.genericAmplifier((0, 1000*1000), (0, 5))), # (mPSI, V)
    "AIN8": Sensor("P6", SensorTypeID.PRESSURE, 6, dataConversions.genericAmplifier((0, 1000*1000), (0, 5))), # (mPSI, V)
    "AIN9": Sensor("P7", SensorTypeID.PRESSURE, 7, dataConversions.genericAmplifier((0, 1000*1000), (0, 5))), # (mPSI, V)
    "AIN10": Sensor("T1", SensorTypeID.TEMPERATURE, 0, dataConversions.genericAmplifier((0, 1300*1000), (0, 10))), # (mC, V)
    "AIN11": Sensor("T2", SensorTypeID.TEMPERATURE, 1, dataConversions.genericAmplifier((0, 1300*1000), (0, 10))), # (mC, V)
    "AIN12": Sensor("T3", SensorTypeID.TEMPERATURE, 3, dataConversions.genericAmplifier((0, 1300*1000), (0, 10))), # Placeholder (mC, V)
    "AIN5": Sensor("T4", SensorTypeID.TEMPERATURE, 4, dataConversions.genericAmplifier((0, 1300*1000), (0, 10))) # Placeholder (mC, V)
    }

scanRate = 8000 # Scan rate in Hz

networkScanFraction = 200 # Fraction of scans to send over network (e.g., 10 means 1 out of every 10 scans)

logFilePath = ""#"\\logs\\labjack-collector"

dataLog = "data.csv"

dataSaveDir = "/mnt/labjack/{date}"

mc_addr = "239.100.110.210"
port = 50002