import os
import yaml

from io import StringIO


def cls():
    print("\033c", end="")


def grammar_yaml() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "grammar.yaml")


class YamlReader:
    def __init__(self, filename: str | StringIO):
        if isinstance(filename, str):
            if not os.path.exists(filename):
                raise FileNotFoundError(f"File {filename} not found!")
            elif os.path.isdir(filename):
                raise IsADirectoryError(f"{filename} is a directory!")
            file_object = open(filename, "r", encoding="utf-8")
        else:
            file_object = filename
        self.yamlf = file_object
        self.data: list[dict] = self.read_yaml()

    def read_yaml(self) -> list[dict]:
        return yaml.load(self.yamlf, Loader=yaml.FullLoader)


class InstructionFetch:
    def __init__(self, instructions: list[dict], target: str, exact_match: bool = True):
        self.instructions = instructions
        self.target: str = target
        self.result: dict | list[dict] = (
            self.fetch() if exact_match else self.fetch_fuzzy()
        )

    def __str__(self):
        """
        Returns the result in a human-readable format.
        """
        if isinstance(self.result, dict):
            if not self.result:
                results = f"No instruction found for {self.target}!"
                return results
            results = f"Opcode: {self.result['opcode']}\n"
            results += f"Name: {self.result['name']}\n"
            results += f"Format: {self.result['format']}\n"
            results += f"Format ID: {self.result['format_id']}\n"
            results += f"Syntax: {self.result['syntax']}\n"
            results += f"Args: {self.result['args_info']}\n"
            results += f"Short Info: {self.result['short_desc']}\n"
            results += f"Detailed Info: {self.result['long_desc']}\n"
            results += (
                f"Note: {self.result['note']}\n" if self.result.get("note") else ""
            )
            results += (
                f"Example: {self.result['example']}\n"
                if self.result.get("example")
                else ""
            )
            results += (
                f"  Desc: {self.result['example_desc']}"
                if self.result.get("example_desc")
                else ""
            )
        elif isinstance(self.result, list):
            results = ""
            for ith, instruction in enumerate(self.result):
                results += f"Result {ith + 1}:\n"
                results += f"Opcode: {instruction['opcode']}\n"
                results += f"Name: {instruction['name']}\n"
                results += f"Format: {instruction['format']}\n"
                results += f"Format ID: {instruction['format_id']}\n"
                results += f"Syntax: {instruction['syntax']}\n"
                results += f"Args: {instruction['args_info']}\n"
                results += f"Short Info: {instruction['short_desc']}\n"
                results += f"Detailed Info: {instruction['long_desc']}\n"
                results += (
                    f"Note: {instruction['note']}\n" if instruction["note"] else ""
                )
                results += (
                    f"Example: {instruction['example']}\n"
                    if instruction["example"]
                    else ""
                )
                results += (
                    f"  Desc: {instruction['example_desc']}\n\n"
                    if instruction["example_desc"]
                    else ""
                )
        else:
            results = "No matching instructions found."
        return results

    def __repr__(self):
        """Return a string representation of the InstructionFetch object."""
        return (
            f"InstructionFetch(instructions={self.instructions}, "
            f"target={self.target}, name={self.name}, "
            f"opcode={self.opcode}, format={self.format}, "
            f"format_id={self.format_id}, syntax={self.syntax}, "
            f"args_info={self.args_info}, short_desc={self.short_desc}, "
            f"long_desc={self.long_desc}, note={self.note}, "
            f"example={self.example}, example_desc={self.example_desc})"
        )

    def fetch(self) -> dict:
        """Fetch the instruction from the instruction set."""
        for instruction in self.instructions:
            if instruction["opcode"] == self.target:
                return instruction
        for instruction in self.instructions:
            if instruction["name"] == self.target:
                return instruction
        return {}

    def fetch_fuzzy(self) -> list[dict]:
        """Fetch the instruction from the instruction set using fuzzy matching."""
        results = []
        for instruction in self.instructions:
            if self.target.lower() in instruction["name"].lower():
                results.append(instruction)
        return results

    def fetch_opcode(self) -> dict:
        """Fetch the instruction from the instruction set using the opcode."""
        for instruction in self.instructions:
            if instruction["opcode"] == self.target:
                return instruction
        return {}

    def fetch_inst(self) -> dict:
        """Fetch the instruction from the instruction set using the name."""
        for instruction in self.instructions:
            if instruction["name"] == self.target:
                return instruction
        return {}

    def replace(self, type: str = "ansi"):
        """
        Replace $ and ` symbols with given type.
        type: str = "ansi" -> "ansi" or "html" or "markdown" or "md" or "plain"
        """
        if type in ["html", "markdown", "md"]:
            result = self.__str__()
            while result.find("$") != -1:
                result = result.replace("$", "<span style='color: #ff0;'>", 1)
                result = result.replace("$", "</span>", 1)
            while result.find("`") != -1:
                result = result.replace("`", "<code>", 1)
                result = result.replace("`", "</code>", 1)
        elif type == "plain":
            result = self.__str__()
            while result.find("$") != -1:
                result = result.replace("$", "", 1)
            while result.find("`") != -1:
                result = result.replace("`", "", 1)
        else:
            NC = "\033[0m"  # No Color
            YELLOW = "\033[0;33m"
            BLUE = "\033[3;34m"
            result = self.__str__()
            while result.find("$") != -1:
                result = result.replace("$", YELLOW, 1)
                result = result.replace("$", NC, 1)
            while result.find("`") != -1:
                result = result.replace("`", BLUE, 1)
                result = result.replace("`", NC, 1)
        return result
