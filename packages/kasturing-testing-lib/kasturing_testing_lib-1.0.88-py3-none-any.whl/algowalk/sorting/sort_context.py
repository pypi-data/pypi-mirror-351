from algowalk.sorting.tracker.sort_algorithm_tracker import StepTracker


class SortContext:
    def __init__(self, strategy, visualizer=None,pseudocode_builder=None):
        self.strategy = strategy
        self.visualizer = visualizer
        self.pseudocode_builder = pseudocode_builder

    def execute_sort(self, data: list):
        tracker = StepTracker(visualizer=self.visualizer, pseudocode_builder=self.pseudocode_builder)
        sorted_data = self.strategy.sort(data, tracker)
        self.strategy.pseudocode(tracker)

        tracker.print_steps()
        tracker.print_summary()
        tracker.print_pseudocode()
        tracker.visualize()

        print(f"\n✅ Final Sorted Output: {sorted_data}")
        return sorted_data
