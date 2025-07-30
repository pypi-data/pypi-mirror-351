from algowalk.searching.search_strategy import SearchStrategy
from algowalk.searching.tracker.search_algo_tracker import StepTracker


class LinearSearchStrategy(SearchStrategy):

    def search(self, data, target, tracker: StepTracker):
        found_index = -1  # Default to -1 if target is not found
        tracker.start(data)
        for index, value in enumerate(data):
            match = (value == target)
            tracker.log(index, value, target, match)
            if match:
                tracker.end()
                for i in range(index + 1, len(data)):
                    tracker.log(i, data[i], target, False, active=False)
                found_index = index
                return found_index
        tracker.end()
        return found_index

    def pseudocode(self, tracker: StepTracker):
        pseudo = tracker.pseudocode_builder
        if pseudo:
            pseudo.bundle_generation(self.search)
