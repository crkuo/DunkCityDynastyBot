# workers/worker_factory.py

from .dynasty_worker import DynastyWorker
from .fvf_worker import FvfWorker


class MatchWorkerFactory:
    @staticmethod
    def get_worker(mode: str):
        if mode == "王朝模式":
            return DynastyWorker()
        elif mode == "5v5 模式":
            return FvfWorker()
        else:
            raise ValueError(f"不支援的模式: {mode}")
