from abc import ABC, abstractmethod
from algowalk.utils.tracker import StepTracker

class SearchStrategy(ABC):
    @abstractmethod
    def search(self, data, target, tracker: StepTracker):
        pass