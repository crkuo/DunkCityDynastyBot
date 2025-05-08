# workers/fvf_worker.py

from .abstract_worker import AbstractMatchWorker
from adbutils import adb
import aircv, random, os, json
import numpy as np
from PyQt6.QtCore import QThread
import sys
def resource_path(relative_path: str) -> str:
    """取得資源的正確路徑，支援 PyInstaller 與開發環境"""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller 打包後的執行環境
        base_path = sys._MEIPASS
    else:
        # 開發階段：__file__ 指的是目前的 Python 檔案位置
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 使用方式：取得圖片資料夾路徑
IMAGE_FOLDER = resource_path(os.path.join("assets", "imgs"))
CONFIG_PATH = resource_path("config.json")
class FvfWorker(AbstractMatchWorker):
    def __init__(self):
        super().__init__()
        self.config = self.LoadConfig()
        self.randomClick = False
        self.randomTime = False
        self.connectPort = ""
        self.startTimes = 0
        self.device = None
        self.numOfProcessMatches = 0
        self.numOfLoseMatches = 0
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
        self.isTerminate = not self.isTerminate

    def export_report(self):
        if self.numOfProcessMatches > 0:
            wins = self.numOfProcessMatches - self.numOfLoseMatches
            self.emitLog.emit(f"共進行了{self.numOfProcessMatches}場，共贏了{wins}場，勝率為 {wins/self.numOfProcessMatches*100:.2f}%")

    def run(self):
        def load_img(name):
            pic = None
            images_loc = os.path.join(IMAGE_FOLDER, self.mode)
            if os.path.exists(images_loc):
                pic = aircv.cv2.cvtColor(aircv.imread(os.path.join(images_loc, f"{name}.png")), aircv.cv2.COLOR_BGR2RGB)
            if pic is None:
                self.emitLog.emit(f"無法讀取 {os.path.join(images_loc, name+'.png')}")
                self.isTerminate = True
            return pic
                
        def access_match_workflow():
            assert startMatch is not None, "載入圖片失敗: fvfstart"
            assert readyButton is not None, "載入圖片失敗: fvfready"
            assert backToLobby is not None, "載入圖片失敗: fvfback"
            assert reachLimit is not None, "載入圖片失敗: reachLimit"
            assert modeCheck is not None, "載入圖片失敗: modeCheck"
            assert matchFinish is not None, "載入圖片失敗: matchFinish"
            assert matchLose is not None, "載入圖片失敗: matchLose"
            if not self.__find_image(modeCheck):
                self.emitLog.emit("非【五對五全場爭霸】畫面")
                self.emitError.emit()
                return
            while self.startTimes > 0 and not self.isTerminate:
                try:
                    if self.__click_image(reachLimit):
                        self.emitLog.emit("配對次數已達上限")
                        break

                    self.emitLog.emit(f"> 第{self.numOfProcessMatches + 1}場比賽開始 <")
                    self.emitLog.emit("開始配對")
                    while not self.__click_image(startMatch):
                        self.emitLog.emit("未找到配對按鈕")
                        self.__sleep(1)
                        print("Cannot find match button.")
                    self.startTimes -= 1
                    self.numOfProcessMatches += 1
                    self.__sleep(5)

                    self.__sleep(matchDefaultTime, 10)
                    self.__click_image(readyButton)
                    self.__sleep(matchDefaultTime, 10)
                        
                    while not self.__click_image(matchFinish):
                        self.__sleep(5)
                    self.__sleep(2)
                    if self.__find_image(matchLose):
                        self.numOfLoseMatches += 1
                        self.emitLog.emit("失敗")
                    else:
                        self.emitLog.emit("獲勝")
                    while not self.__click_image(backToLobby):
                        self.__sleep(5)
                except Exception as exc:
                    self.isTerminate = True
                    self.emitError.emit()
                    return
            self.emitFinish.emit()


        self.emitStart.emit()
        self.emitLog.emit("[初始化 5v5 模式]")
        QThread.sleep(1)
        self.isTerminate = False
        try:
            self.TriggerMumuADB()
            self.connectAdb()
            self.emitLog.emit("adb連接成功")
        except Exception as e:            
            self.isTerminate = True
            self.emitLog.emit("adb連接失敗")
            self.emitError.emit()
            return
        
        startMatch = load_img("fvfstart")
        readyButton = load_img("fvfready")
        backToLobby = load_img("fvfback")
        reachLimit = load_img("reachLimit")
        modeCheck = load_img("modeCheck")
        matchFinish = load_img("matchFinish")
        matchLose = load_img("matchLose")
        matchDefaultTime = 180
        access_match_workflow()

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
