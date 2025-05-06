from workers.worker_factory import MatchWorkerFactory
from workers.abstract_worker import AbstractMatchWorker

CONFIG_PATH = "./config.json"

class MatchAutomationController:
    def __init__(self, ui):
        """
        ui: UI 元件集合（需包含 logTextBrowser 等）
        selected_mode: 字串模式，如 '王朝模式' 或 '5v5 模式'
        """
        self.ui = ui
        
        self.start = False

    def _connect_worker_signals(self):
        self.worker.isStart.connect(self._on_start)
        self.worker.isFinish.connect(self._on_finish)
        self.worker.isError.connect(self._on_error)
        self.worker.emitLog.connect(self.ui.logTextBrowser.append)

    def start_or_stop(self):
        self.start = not self.start
        if self.start:
            self._start_worker()
        else:
            self._stop_worker()

    def _start_worker(self):
        try:
            port = self.ui.connectPort.text()
            times = int(self.ui.matchTimes.text()) if self.ui.matchTimes.text().isdigit() else 0
            random_time = self.ui.randomTimeCheckButton.isChecked()
            random_click = self.ui.randomClickCheckButton.isChecked()
            self.worker: AbstractMatchWorker = MatchWorkerFactory.get_worker(self.ui.modeSelector.currentText())
            self.worker.setVariable(port, times, random_time, random_click)
            self._connect_worker_signals()
            try:
                self.worker.TriggerMumuADB()
            except Exception as e:
                self.ui.logTextBrowser.append(f"Mumu ADB 錯誤：{str(e)}")

            self.worker.start()

        except Exception as e:
            self.ui.logTextBrowser.append(f"啟動錯誤：{str(e)}")
            self._stop_worker()
            self._reset_ui_state()

    def _stop_worker(self):
        self.worker.ChangeTerminateStatus()
        self.ui.logTextBrowser.append("[使用者手動停止]")
        self._update_ui_state(disabled=False)

    def _on_start(self):
        self.ui.logTextBrowser.setText("")
        self._update_ui_state(disabled=True)

    def _on_finish(self):
        self._reset_ui_state()

    def _on_error(self):
        self._reset_ui_state()

    def _update_ui_state(self, disabled: bool):
        print(f"_update_ui_state: ",disabled)
        self.ui.startButton.setText("停止" if disabled else "開始")
        self.ui.connectPort.setDisabled(disabled)
        self.ui.randomTimeCheckButton.setDisabled(disabled)
        self.ui.randomClickCheckButton.setDisabled(disabled)
        self.ui.matchTimes.setDisabled(disabled)

    def _reset_ui_state(self):
        try:
            self.start = False
            self.worker.export_report()
            self._update_ui_state(disabled=self.start)
        except Exception as e:
            self.ui.logTextBrowser.append(f"啟動錯誤：{str(e)}")