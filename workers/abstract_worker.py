# workers/abstract_worker.py

from PyQt6.QtCore import QThread, pyqtSignal
from adbutils import adb
import os

class AbstractMatchWorker(QThread):
    
    emitStart = pyqtSignal()
    emitProgress = pyqtSignal(str)
    emitFinish = pyqtSignal()
    emitError = pyqtSignal()

    emitLog = pyqtSignal(str)
    emitMoney = pyqtSignal(str)
    emitStone = pyqtSignal(str)
    emitMode = pyqtSignal(str)

    isTerminate = False
    config = None
    def setVariable(self, connectPort: str, startTimes: int, randomTime: bool, randomClick: bool):
        raise NotImplementedError("setVariable must be implemented in subclass")

    def ChangeTerminateStatus(self):
        raise NotImplementedError("ChangeTerminateStatus must be implemented in subclass")

    def export_report(self):
        raise NotImplementedError("export_report must be implemented in subclass")
    
    def TriggerMumuADB(self):
        try:
            if self.config:
                if os.path.exists(self.config["mumu_path"]):
                    import subprocess
                    adb_path = os.path.join(self.config["mumu_path"], "adb.exe")
                    subprocess.run([adb_path, "reconnect"])
                    subprocess.run([adb_path, "connect", self.config["adb_addr"]])
                else:
                    raise Exception("找不到Mumu路徑。")
            else:
                raise Exception("Config is not defined.")
        except Exception as exc:
            self.emitLog.emit(str(exc))
            self.emitError.emit()
    
    def connectAdb(self):
        adb.device(serial=self.connectPort).info
        self.device = adb.device(serial=self.connectPort)