import time
import sys


class StepTracker:
    def __init__(self, visualizer=None):
        self.steps = []
        self.total_comparison = 0
        self.visualizer = visualizer
        self.start_time = None
        self.end_time = None
        self.total_memory = 0

    def start(self, data):
        self.start_time = time.perf_counter()
        self.total_memory += sys.getsizeof(data)

    def log(self, index, value, target, match, active=True):
        self.steps.append({
            'index': index,
            'value': value,
            'target': target,
            'match': match
        })
        if active:
            self.total_comparison += 1
            self.total_memory += sys.getsizeof(index) + sys.getsizeof(value) + sys.getsizeof(match)

    def end(self):
        self.end_time = time.perf_counter()

    def print_steps(self):
        print("\n\033[1;34m>>> Step-by-Step Execution <<<\033[0m")
        print("\033[1;33mBreadcrumbs: Search → Trace → Evaluation\033[0m\n")
        for i, step in enumerate(self.steps, 1):
            print(f"\033[1;36mStep {i}:\033[0m Checked index {step['index']} → "
                  f"Value = {step['value']} | "
                  f"Target = {step['target']} | "
                  f"{'✅ MATCH' if step['match'] else '❌ NO MATCH'}")

    def print_summary(self):
        total_time = self.end_time - self.start_time if self.end_time else 0
        print("\n\033[1;34m>>> Benchmark Summary <<<\033[0m")
        print("\033[1;33mBreadcrumbs: Search → Execution → Metrics\033[0m\n")
        print(f"\033[1;32m✓ Total comparisons:\033[0m {self.total_comparison}")
        print(f"\033[1;32m✓ Estimated space used:\033[0m {self.total_memory} bytes")
        print(f"\033[1;32m✓ Execution time:\033[0m {total_time:.6f} seconds")
        print(f"\033[1;35m⌛ Static Time Complexity:\033[0m O(n)")
        print(f"\033[1;35m🧠 Static Space Complexity:\033[0m O(1)\n")

    def visualize(self):
        if self.visualizer:
            self.visualizer.visualize(self.steps)
