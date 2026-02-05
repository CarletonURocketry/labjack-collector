"""_summary_
"""
import argparse

import datetime
import sys
import time
import daq
import config
import sendData
import dataLogger
import logging
from labjack import ljm # type: ignore
from threading import Thread
from queue import Queue, Full

parser = argparse.ArgumentParser(description="LabJack Data Collector")
parser.add_argument("-d", "--debug", help="Enable simulated labjack data", action="store_true")
parser.add_argument("--dataFile", help="Path to save data file to", type=str, default=config.dataLog)
parser.add_argument("--logFilePath", help="Path to save log files to", type=str, default=config.logFilePath)
parser.add_argument("--scanRate", help="Scan rate in Hz", type=int, default=config.scanRate)
parser.add_argument("--networkScanFraction", help="Fraction of scans to send over network (e.g., 10 means 1 out of every 10 scans)", type=int, default=config.networkScanFraction)
parser.add_argument("--mc_addr", help="Multicast address to send data to", type=str, default=config.mc_addr)
parser.add_argument("--port", help="Port to send data to", type=int, default=config.port)
parser.add_argument("--channelList", help="Comma-separated list of channels to read from LabJack", type=str, default="")
args = parser.parse_args()

errorLog = logging.getLogger(__name__)
logging.basicConfig(filename=config.logFilePath + "\\" + "error.log", encoding='utf-8', level=logging.INFO)

log = True
dataLogFileName = args.dataFile
scanRate = args.scanRate

errorLog.info("Starting labjack-collector")

startTime = time.time()

# compute channel list from args (split comma-separated string) or default to config keys
ch_list = args.channelList.split(",") if args.channelList != "" else list(config.channelToSensor.keys())

labjack = daq.labjackClass(ch_list, scanRate, args)

sender = sendData.sendData(args.mc_addr, args.port, ch_list, config.channelToSensor)

dataLogFile = dataLogger.dataLogger(dataLogFileName, ch_list, config.channelToSensor)

scansSinceNetPacket = 0

dataList = []

writeQueue: Queue[list[dict[str, datetime.datetime | int | float]]] = Queue()
netQueue: Queue[dict[str, list[int]]] = Queue()

def labjackCollector():
    global scansSinceNetPacket
    try:
        dataList: list[dict[str, datetime.datetime | int | float]] = []
        netDict: dict[str, list[int]] = {"Timestamp": []}
        for ch in ch_list:
            sensor_name = config.channelToSensor[ch].name
            netDict[sensor_name] = []
            netDict[ch] = []
        i = 0
        while True:
            scanData = labjack.read_data()
            #print(f"Data read: {scanData}")
            if type(scanData) == int:
                time.sleep(1)
                print("Error reading data from labjack")
                errorLog.error("Error reading data from labjack")
            else:
                data, scansPendingLJ, scansPendingLJM = scanData # type: ignore
                dataDict: dict[str, datetime.datetime | int | float] = {}
                scansSinceNetPacket += 1
                timestamp = time.time() - startTime
                netDict["Timestamp"].append(int(timestamp * 1000))
                dataDict["Timestamp"] = datetime.datetime.now(datetime.timezone.utc)
                for i in range(len(ch_list)):
                    sensor = config.channelToSensor[ch_list[i]]
                    convertedValue = sensor.convertClass.volt_to_output(data[i]) # type: ignore
                    dataDict[f"{ch_list[i]}"] = data[i]
                    dataDict[f"{sensor.name}"] = convertedValue
                    netDict[f"{sensor.name}"].append(convertedValue)
                dataList.append(dataDict)
                if scansSinceNetPacket > config.networkScanFraction:
                    try:
                        netQueue.put(netDict, block = False)
                        scansSinceNetPacket = 0
                        print(f"P3 value sent: {netDict['P3'][-1]}")
                        print(f"AIN13 raw value sent: {dataDict['AIN13']}")
                        netDict = {"Timestamp": []}
                        for ch in ch_list:
                            sensor_name = config.channelToSensor[ch].name
                            netDict[sensor_name] = []
                    except Full:
                        pass
                    print(f"LJM Buffer {scansPendingLJM}")
                    #print("Sent network packet")
                if len(dataList) >= 800:
                    try:
                        writeQueue.put(dataList, block=False)
                        dataList = []
                    except Full:
                        pass
    except (Exception, KeyboardInterrupt):
        e = sys.exc_info()
        ljm.closeAll()
        print(f"Unhandled exception in main loop: {e}")
        errorLog.critical(f"Unhandled exception in main loop: {e}")

def dataWriter():
    while True:
        data = writeQueue.get(block=True)
        #print(f"writeQueue size: {writeQueue.qsize()}")
        dataLogFile.writeRows(data)

def sendPacket():
    while True:
        data = netQueue.get(block=True)
        #print(f"netQueue size: {netQueue.qsize()}")
        sender.send_packet(data)

if __name__ == "__main__":
    collectorProcess = Thread(target=labjackCollector, name="LabJackCollectorProcess")
    dataProcess = Thread(target=dataWriter, name="DataWriterProcess")
    netProcess = Thread(target=sendPacket, name="SendPacketProcess")
    netProcess.start()
    collectorProcess.start()
    dataProcess.start()
    collectorProcess.join()
    dataProcess.join()
    netProcess.join()