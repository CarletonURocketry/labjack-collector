import datetime
import config
import daq
import argparse
import time

import pickle

parser = argparse.ArgumentParser(description="LabJack Data Collector")
parser.add_argument("-d", "--debug", help="Enable simulated labjack data", action="store_true")

args = parser.parse_args()

ch_list = list(config.channelToSensor.keys())
labjack = daq.labjackClass(ch_list, 8000, args)

dataList: list[dict[str, datetime.datetime | float | int]] = []
i = 0
while i < 80000:
    scanData = labjack.read_data()
    if type(scanData) == int:
        time.sleep(1)
        print("Error reading data from labjack")
    else:
        timestamp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=i * 1 / 8000)
        dataConverted: list[int] = []
        data = labjack.read_data()[0]  # type: ignore
        for j in range(len(ch_list)):
            sensor = config.channelToSensor[ch_list[j]]
            convertedValue = sensor.convertClass.volt_to_output(data[j]) # type: ignore
            dataConverted.append(convertedValue)
        dataDict: dict[str, float | int | datetime.datetime] = {"Timestamp": timestamp}
        for j in range(len(ch_list)):
            dataDict[f"{ch_list[j]}_Raw"] = round(data[j], 4) # type: ignore
        for j in range(len(ch_list)):
            dataDict[f"{ch_list[j]}_Converted"] = dataConverted[j]
        dataList.append(dataDict)
        i += 1

pickle.dump(dataList, open("fakeData.pkl", "wb"))
print("Fake data generated and saved to fakeData.pkl")