from abc import ABC, abstractmethod
from algowalk.searching.tracker.search_algo_tracker import StepTracker


class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list, tracker: StepTracker) -> list:
        pass
