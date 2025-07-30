class PseudocodeBuilder:
    def __init__(self):
        self.lines = []
        self.indent_level = 0
        self.indent_str = "    "

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level = max(0, self.indent_level - 1)

    def add_line(self, line: str):
        indented_line = f"{self.indent_str * self.indent_level}{line}"
        self.lines.append(indented_line)

    def get_code(self) -> str:
        return "\n".join(self.lines)

    def print_code(self):
        print("\n\033[1;34m>>> Pseudocode <<<\033[0m\n")
        for line in self.lines:
            print(f"\033[1;36m{line}\033[0m")