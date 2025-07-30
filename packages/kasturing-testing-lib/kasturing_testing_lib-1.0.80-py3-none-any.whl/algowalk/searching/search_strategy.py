from abc import ABC, abstractmethod
from algowalk.utils.tracker.search_algo_tracker import StepTracker


class SearchStrategy(ABC):
    @abstractmethod
    def search(self, data, target, tracker: StepTracker):
        pass
