import config

class logFile:
    def __init__(self, filepath: str, channels: list[str], config: dict[str, config.Sensor]) -> None:
        self.filepath = filepath
        self.channels = channels
        self.config = config
        with open(self.filepath, "a", newline="") as f:
            header = "Timestamp,"
            for channel in self.channels:
                sensor = self.config[channel]
                header += f"{sensor.name}_Raw,{sensor.name}_Converted,"
            header = header + "\n"
            f.write(header)

    def writeRow(self, dataRaw: list[float], dataConverted: list[float], timestamp: float) -> None:
        with open(self.filepath, "a", newline="") as f:
            row = f"{timestamp},"
            for i in range(len(self.channels)):
                row += f"{dataRaw[i]},{dataConverted[i]},"
            row = row + "\n"
            f.write(row)