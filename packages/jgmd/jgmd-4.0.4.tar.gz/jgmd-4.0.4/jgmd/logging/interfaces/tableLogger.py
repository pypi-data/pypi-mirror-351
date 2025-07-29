from ..loggingUtil import makeTable

# from collections.abc import Iterable
from .logger import Logger
from ..loggingConsts import LogLevel


class TableLogger(Logger):

    def __init__(
        self,
        logDirectory: str,
        fileName: str,
        logLevel: LogLevel,
        printToConsole: bool = True,
    ):
        super().__init__(logDirectory, fileName, logLevel, printToConsole)

    def getHeaders(self):
        raise NotImplementedError("getHeaders() must be implemented by subclass")

    def getRowData(self, data):
        raise NotImplementedError("getRowData() must be implemented by subclass")

    def clearLog(self):
        super().clearLog()
        self.writeHeaders()

    def writeHeaders(self):
        with open(self.filePath, "a") as file:
            headerStr = ",".join(self.getHeaders())
            file.write(headerStr + "\n")

    def logRowToFile(self, data):
        with open(self.filePath, "a") as file:
            data = self.getRowData(data)
            rowStr = ",".join([str(item) for item in data])
            file.write(rowStr + "\n")

    def getTableStr(self, datas: list, label: str = None):
        if len(datas) == 0:
            return ""
        # if not isinstance(datas[0], Iterable):
        #     datas = [[data] for data in datas]

        data = [self.getRowData(data) for data in datas]

        headers = self.getHeaders()
        return makeTable(data, headers, label=label)
