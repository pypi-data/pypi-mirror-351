from algowalk.sorting.sort_strategy import SortStrategy
from algowalk.searching.tracker.search_algo_tracker import StepTracker


class BubbleSortStrategy(SortStrategy):
    def sort(self, data: list, tracker: StepTracker) -> list:
        tracker.start(data)
        n = len(data)
        arr = data.copy()

        for i in range(n):
            for j in range(0, n - i - 1):
                match = arr[j] > arr[j + 1]
                tracker.log(index=j, value=arr[j], target=arr[j + 1], match=match)

                if match:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        tracker.end()
        return arr

    def pseudocode(self, tracker: StepTracker):
        pseudo = tracker.pseudocode_builder
        if pseudo:
            pseudo.bundle_generation(self.sort)
