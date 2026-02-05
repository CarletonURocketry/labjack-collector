import pickle
import csv
import datetime
import os
import fastavro
import itertools

dataList = pickle.load(open("fakeData.pkl", "rb"))

class csvOpenEveryTime:
    def __init__(self):
        file = open("test.csv", "w", newline="\n")
        self.fieldnames = ["Timestamp", "AIN0_Raw", "AIN0_Converted", "AIN1_Raw", "AIN1_Converted", "AIN2_Raw", "AIN2_Converted", "AIN3_Raw", "AIN3_Converted", "AIN4_Raw", "AIN4_Converted", "AIN5_Raw", "AIN5_Converted", "AIN6_Raw", "AIN6_Converted", "AIN7_Raw", "AIN7_Converted", "AIN8_Raw", "AIN8_Converted", "AIN9_Raw", "AIN9_Converted", "AIN10_Raw", "AIN10_Converted", "AIN11_Raw", "AIN11_Converted", "AIN12_Raw", "AIN12_Converted", "AIN13_Raw", "AIN13_Converted"]
        self.writer = csv.DictWriter(file, fieldnames=self.fieldnames)
        self.writer.writeheader()
        file.close()
    def write(self, data: list[dict[str, float | int | datetime.datetime]]):
        for dict in data:
            with open("test.csv", "a", newline="\n") as file:
                self.writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                self.writer.writerow(dict)
                file.flush()
                os.fsync(file.fileno())

class csvKeepOpen:
    def __init__(self):
        self.file = open("test.csv", "w", newline="\n")
        self.fieldnames = ["Timestamp", "AIN0_Raw", "AIN0_Converted", "AIN1_Raw", "AIN1_Converted", "AIN2_Raw", "AIN2_Converted", "AIN3_Raw", "AIN3_Converted", "AIN4_Raw", "AIN4_Converted", "AIN5_Raw", "AIN5_Converted", "AIN6_Raw", "AIN6_Converted", "AIN7_Raw", "AIN7_Converted", "AIN8_Raw", "AIN8_Converted", "AIN9_Raw", "AIN9_Converted", "AIN10_Raw", "AIN10_Converted", "AIN11_Raw", "AIN11_Converted", "AIN12_Raw", "AIN12_Converted", "AIN13_Raw", "AIN13_Converted"]
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()
    def write(self, data: list[dict[str, float | int | datetime.datetime]]):
        self.writer.writerows(data)
        self.file.flush()
        os.fsync(self.file.fileno())
    def __del__(self):
        self.file.close()

class csvKeepOpenWriteRow:
    def __init__(self):
        self.file = open("test.csv", "w", newline="\n")
        self.fieldnames = ["Timestamp", "AIN0_Raw", "AIN0_Converted", "AIN1_Raw", "AIN1_Converted", "AIN2_Raw", "AIN2_Converted", "AIN3_Raw", "AIN3_Converted", "AIN4_Raw", "AIN4_Converted", "AIN5_Raw", "AIN5_Converted", "AIN6_Raw", "AIN6_Converted", "AIN7_Raw", "AIN7_Converted", "AIN8_Raw", "AIN8_Converted", "AIN9_Raw", "AIN9_Converted", "AIN10_Raw", "AIN10_Converted", "AIN11_Raw", "AIN11_Converted", "AIN12_Raw", "AIN12_Converted", "AIN13_Raw", "AIN13_Converted"]
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()
    def write(self, data: list[dict[str, float | int | datetime.datetime]]):
        for dict in data:
            self.writer.writerow(dict)
            self.file.flush()
            os.fsync(self.file.fileno())
    def __del__(self):
        self.file.close()

class avroOpenEveryTime:
    def __init__(self):
        self.schema = fastavro.schema.load_schema("testSchema.avsc") # type: ignore
        zeroRow: list[dict[str, datetime.datetime | float | int]] = [{"Timestamp": datetime.datetime.now(), "AIN0_Raw": 0.0, "AIN0_Converted": 0, "AIN1_Raw": 0.0, "AIN1_Converted": 0, "AIN2_Raw": 0.0, "AIN2_Converted": 0, "AIN3_Raw": 0.0, "AIN3_Converted": 0, "AIN4_Raw": 0.0, "AIN4_Converted": 0, "AIN5_Raw": 0.0, "AIN5_Converted": 0, "AIN6_Raw": 0.0, "AIN6_Converted": 0, "AIN7_Raw": 0.0, "AIN7_Converted": 0, "AIN8_Raw": 0.0, "AIN8_Converted": 0, "AIN9_Raw": 0.0, "AIN9_Converted": 0, "AIN10_Raw": 0.0, "AIN10_Converted": 0, "AIN11_Raw": 0.0, "AIN11_Converted": 0, "AIN12_Raw": 0.0, "AIN12_Converted": 0, "AIN13_Raw": 0.0, "AIN13_Converted": 0}]
        file = open("test.avro", "wb")
        fastavro.writer(file, self.schema, zeroRow) # type: ignore
        file.flush()
        os.fsync(file.fileno())
        file.close()
    def write(self, data: list[dict[str, float | int | datetime.datetime]]):
        for record in data:
            with open("test.avro", "a+b") as file:
                fastavro.writer(file, self.schema, [record]) # type: ignore
                file.flush()
                os.fsync(file.fileno())

class avroKeepOpenFlushEachRow:
    def __init__(self):
        zeroRow: list[dict[str, datetime.datetime | float | int]] = [{"Timestamp": datetime.datetime.now(), "AIN0_Raw": 0.0, "AIN0_Converted": 0, "AIN1_Raw": 0.0, "AIN1_Converted": 0, "AIN2_Raw": 0.0, "AIN2_Converted": 0, "AIN3_Raw": 0.0, "AIN3_Converted": 0, "AIN4_Raw": 0.0, "AIN4_Converted": 0, "AIN5_Raw": 0.0, "AIN5_Converted": 0, "AIN6_Raw": 0.0, "AIN6_Converted": 0, "AIN7_Raw": 0.0, "AIN7_Converted": 0, "AIN8_Raw": 0.0, "AIN8_Converted": 0, "AIN9_Raw": 0.0, "AIN9_Converted": 0, "AIN10_Raw": 0.0, "AIN10_Converted": 0, "AIN11_Raw": 0.0, "AIN11_Converted": 0, "AIN12_Raw": 0.0, "AIN12_Converted": 0, "AIN13_Raw": 0.0, "AIN13_Converted": 0}]
        self.schema = fastavro.schema.load_schema("testSchema.avsc") # type: ignore
        self.file = open("test.avro", "wb")
        fastavro.writer(self.file, self.schema, zeroRow) # type: ignore
        self.file.flush()
        os.fsync(self.file.fileno())
        self.file.close()
        self.file = open("test.avro", "a+b")
    def write(self, data: list[dict[str, float | int | datetime.datetime]]):
        for record in data:
            fastavro.writer(self.file, self.schema, [record]) # type: ignore
            self.file.flush()
            os.fsync(self.file.fileno())
    def __del__(self):
        self.file.close()
    
class avroKeepOpenFlushBatch:
    def __init__(self):
        zeroRow: list[dict[str, datetime.datetime | float | int]] = [{"Timestamp": datetime.datetime.now(), "AIN0_Raw": 0.0, "AIN0_Converted": 0, "AIN1_Raw": 0.0, "AIN1_Converted": 0, "AIN2_Raw": 0.0, "AIN2_Converted": 0, "AIN3_Raw": 0.0, "AIN3_Converted": 0, "AIN4_Raw": 0.0, "AIN4_Converted": 0, "AIN5_Raw": 0.0, "AIN5_Converted": 0, "AIN6_Raw": 0.0, "AIN6_Converted": 0, "AIN7_Raw": 0.0, "AIN7_Converted": 0, "AIN8_Raw": 0.0, "AIN8_Converted": 0, "AIN9_Raw": 0.0, "AIN9_Converted": 0, "AIN10_Raw": 0.0, "AIN10_Converted": 0, "AIN11_Raw": 0.0, "AIN11_Converted": 0, "AIN12_Raw": 0.0, "AIN12_Converted": 0, "AIN13_Raw": 0.0, "AIN13_Converted": 0}]
        self.schema = fastavro.schema.load_schema("testSchema.avsc") # type: ignore
        self.file = open("test.avro", "wb")
        fastavro.writer(self.file, self.schema, zeroRow) # type: ignore
        self.file.flush()
        os.fsync(self.file.fileno())
        self.file.close()
        self.file = open("test.avro", "a+b")
    def write(self, data: list[dict[str, float | int | datetime.datetime]]):
        fastavro.writer(self.file, self.schema, data) # type: ignore
        self.file.flush()
        os.fsync(self.file.fileno())
    def __del__(self):
        self.file.close()




if __name__ == "__main__":
    for i in [100, 800, 500, 1000, 80000]:
        for method in [csvKeepOpen, avroKeepOpenFlushBatch]: # type: ignore # Removed other options as they take forever to run.
            startInit = datetime.datetime.now()
            writer = method() # type: ignore
            start = datetime.datetime.now()
            #print(f"{method.__name__} init took {start - startInit} seconds to start") # type: ignore
            for batch in itertools.batched(dataList, i):
                writer.write(batch) # type: ignore
            end = datetime.datetime.now()
            print(f"{method.__name__} took {end - start} to write {len(dataList)} rows in batches of {i}") 

# Results (from one run):
#   csvOpenEveryTime init took 0:00:00.000999 seconds to start
#   csvOpenEveryTime took 0:00:57.033181 to write 80000 rows in batches of 100
#   csvKeepOpen init took 0:00:00.001517 seconds to start
#   csvKeepOpen took 0:00:01.640822 to write 80000 rows in batches of 100
#   csvKeepOpenWriteRow init took 0:00:00.001017 seconds to start
#   csvKeepOpenWriteRow took 0:00:37.880997 to write 80000 rows in batches of 100
#   avroOpenEveryTime init took 0:00:00.003012 seconds to start
#   
