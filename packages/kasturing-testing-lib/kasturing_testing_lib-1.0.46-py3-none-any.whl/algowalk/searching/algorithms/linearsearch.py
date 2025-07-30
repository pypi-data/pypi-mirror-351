from algowalk.searching.search_strategy import SearchStrategy
from algowalk.utils.tracker import StepTracker


class LinearSearchStrategy(SearchStrategy):
    def search(self, data, target, tracker: StepTracker):
        pseudo = tracker.pseudocode_builder
        if pseudo:
            pseudo.add_line("for i in range(0, len(data)):")
            pseudo.indent()
            pseudo.add_line("if data[i] == target:")
            pseudo.indent()
            pseudo.add_line("return i")
            pseudo.dedent()
            pseudo.add_line("# continue loop")
            pseudo.dedent()
            pseudo.add_line("return -1")
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
