# workers/fvf_worker.py

from .abstract_worker import AbstractMatchWorker
from adbutils import adb
import aircv, random, os, json
import numpy as np
from PyQt6.QtCore import QThread
import time

CONFIG_PATH = "./config.json"
BASE_FOLDER = os.path.dirname(os.path.dirname(__file__))
IMAGE_FOLDER = os.path.join(BASE_FOLDER, "assets", "imgs")

class FvfWorker(AbstractMatchWorker):
    def __init__(self):
        super().__init__()
        self.config = self.LoadConfig()
        self.randomClick = False
        self.randomTime = False
        self.connectPort = ""
        self.startTimes = 0
        self.device = None
        self.isTerminate = False
        self.numOfProcessMatches = 0
        self.mode = "FVF"

    def LoadConfig(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as fp:
                return json.load(fp)
        return {}
    

    def setVariable(self, connectPort: str, startTimes: int, randomTime: bool, randomClick: bool):
        self.connectPort = connectPort
        self.startTimes = startTimes
        self.randomTime = randomTime
        self.randomClick = randomClick

    def ChangeTerminateStatus(self):
        self.isTerminate = True

    def export_report(self):
        self.emitLog.emit("===== 結束掛機 (5v5 模式) =====")
        self.emitLog.emit(f"共進行了 {self.numOfProcessMatches} 場比賽")

    def run(self):
        self.isStart.emit()
        self.emitLog.emit("[初始化 5v5 模式]")
        QThread.sleep(1)
        try:
            self.isTerminate = False
            adb.device(serial=self.connectPort).info
            self.device = adb.device(serial=self.connectPort)
            self.emitLog.emit("adb連接成功")
        except Exception as e:
            self.emitLog.emit("adb連接失敗")
            self.isError.emit()
            return
        
        def load_img(name):
            pic = None
            images_loc = os.path.join(IMAGE_FOLDER, self.mode)
            if os.path.exists(images_loc):
                pic = aircv.cv2.cvtColor(aircv.imread(os.path.join(images_loc, f"{name}.png")), aircv.cv2.COLOR_BGR2RGB)
            if pic is None:
                self.emitLog.emit(f"無法讀取 {os.path.join(images_loc, name+'.png')}")
                self.isTerminate = True
            return pic
                
        startMatch = load_img("fvfstart")
        readyButton = load_img("fvfready")
        backToLobby = load_img("fvfback")

        matchDefaultTime = 180

        while self.startTimes > 0 and not self.isTerminate:
            self.emitLog.emit(f"> 第{self.numOfProcessMatches + 1}場比賽開始 <")

            while not self.__click_image(startMatch):
                self.__sleep(4)

            self.emitLog.emit("開始配對")
            self.startTimes -= 1
            self.numOfProcessMatches += 1
            self.__sleep(5)

            self.__sleep(matchDefaultTime, 10)

            if self.__click_image(readyButton):
                self.__sleep(matchDefaultTime, 10)

            while not self.__click_image(backToLobby):
                self.__sleep(30)

        self.isFinish.emit()

    def __sleep(self, sec, random_sec=None):
        base = sec * 1000
        if self.randomTime:
            drift = random.randint(-int(random_sec or sec)*1000//3, int(random_sec or sec)*1000//3)
            QThread.msleep(base + drift)
        else:
            QThread.sleep(sec)

    def __find_image(self, img, thres=0.9):
        screenshot = np.asarray(self.device.screenshot())
        return aircv.find_template(screenshot, img, thres)

    def __click_image(self, img):
        result = self.__find_image(img)
        if result:
            x, y = result["result"]
            if self.randomClick:
                x += random.randint(-10, 10)
                y += random.randint(-10, 10)
            self.device.click(x, y)
            return True
        return False
