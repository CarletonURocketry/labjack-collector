"""_summary_
"""
import argparse

parser = argparse.ArgumentParser(description="LabJack Data Collector")
parser.add_argument("-d", "--debug", help="Enable simulated labjack data", action="store_true")
args = parser.parse_args()

print(args.debug)

import sys
import time
import daq
import config
import sendData
import dataLogger
import logging


errorLog = logging.getLogger(__name__)
logging.basicConfig(filename=config.logFilePath + "\\" + "error.log", encoding='utf-8', level=logging.INFO)

errorLog.info("Starting labjack-collector")

startTime = time.time()

ch_list = list(config.channelToSensor.keys())

labjack = daq.labjackClass(ch_list, config.scanRate, args)

sender = sendData.sendData(config.mc_addr, config.port, ch_list, config.channelToSensor)

dataLogger = dataLogger.dataLogger(config.dataLog, ch_list, config.channelToSensor)

scansSinceNetPacket = 0

try:
    while True:
        scanData = labjack.read_data()
        print(f"Data read: {scanData}")
        if type(scanData) == int:
            print("Error reading data from labjack")
            errorLog.error("Error reading data from labjack")
        else:
            data, scansPendingLJM, scansPendingLJ = scanData # type: ignore
            scansSinceNetPacket += 1
            timestamp = time.time() - startTime
            print(f"Timestamp: {timestamp}")
            dataConverted: list[int] = []
            for i in range(len(ch_list)):
                sensor = config.channelToSensor[ch_list[i]]
                convertedValue = sensor.convertClass.volt_to_output(data[i]) # type: ignore
                dataConverted.append(convertedValue)
            if scansSinceNetPacket > config.networkScanFraction:
                sender.send_packet(dataConverted, timestamp / 1000) # type: ignore
                scansSinceNetPacket = 0
                print("Sent network packet")
            dataLogger.writeRow(data, dataConverted, timestamp) # type: ignore
except Exception:
    e = sys.exc_info()
    print(f"Unhandled exception in main loop: {e}")
    errorLog.critical(f"Unhandled exception in main loop: {e}")