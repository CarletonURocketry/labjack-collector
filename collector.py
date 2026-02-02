"""_summary_
"""
import sys
import time
import daq
import config
import sendData
import dataLogger
import logging
#import time
#import argparse



errorLog = logging.getLogger(__name__)
logging.basicConfig(filename=config.logFilePath + "\\" + "error.log", encoding='utf-8', level=logging.INFO)

ch_list = list(config.channelToSensor.keys())

labjack = daq.labjack(ch_list, config.scanRate)

sender = sendData.sendData(config.mc_addr, config.port, ch_list, config.channelToSensor)

dataLogger = dataLogger.dataLogger(config.dataLog, ch_list, config.channelToSensor)

scansSinceNetPacket = 0

try:
    while True:
        scanData = labjack.read_data()
        if type(scanData) == tuple[list[float], int, int]:
            data, scansPendingLJM, scansPendingLJ = scanData # type: ignore
            scansSinceNetPacket += 1
            timestamp = time.time_ns()
            dataConverted: list[int] = []
            for i in range(len(ch_list)):
                sensor = config.channelToSensor[ch_list[i]]
                convertedValue = sensor.convertClass.volt_to_output(data[i]) # type: ignore
                dataConverted.append(convertedValue)
            if scansSinceNetPacket > config.networkScanFraction:
                sender.send_packet(dataConverted, timestamp * 1000 * 1000) # type: ignore
                scansSinceNetPacket = 0
            dataLogger.writeRow(data, dataConverted, timestamp * 1000 * 1000) # type: ignore
        else:
            errorLog.error("Error reading data from labjack")
except Exception:
    e = sys.exc_info()
    errorLog.critical(f"Unhandled exception in main loop: {e}")