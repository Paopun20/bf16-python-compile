from rich_argparse import RichHelpFormatter
from rich.console import Console

class CoolCustomRichFormatter(RichHelpFormatter):
    def __init__(self, *args, **kwargs):
        self.styles["argparse.text"] = "italic green"
        self.styles["argparse.args"] = "bold red"
        self.styles["argparse.groups"] = "bold underline blue"
        self.styles["argparse.metavar"] = "yellow"
        self.styles["argparse.prog"] = "bold magenta"
        self.styles["argparse.syntax"] = "bold cyan"
        self.styles["argparse.default"] = "green"
        super().__init__(*args, **kwargs)