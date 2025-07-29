from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Button, Footer, Header, Static, Select
from textual.containers import Vertical
import importlib
import click
import subprocess

class WizardDynamicApp(App):
    CSS_PATH = "style.css"
    TITLE = "Assistant CLI dynamique"

    def __init__(self, group_name: str, command_name: str):
        super().__init__()
        self.group_name = group_name
        self.command_name = command_name
        self.fields = {}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"Commande : {self.group_name} {self.command_name}", id="title")
        container = Vertical(id="form")

        module = importlib.import_module(f"mem_cli.commands.{self.group_name}")
        command = getattr(module, self.command_name.replace('-', '_'))

        for param in command.params:
            label = Label(param.name)
            default = str(param.default) if param.default is not None else ""
            if isinstance(param.type, click.Choice):
                input_widget = Select([(c, c) for c in param.type.choices], prompt=param.name)
            elif isinstance(param.type, click.BoolParamType):
                input_widget = Select([("yes", "True"), ("no", "False")], prompt=param.name)
            else:
                input_widget = Input(placeholder=default, id=param.name)
            self.fields[param.name] = input_widget
            container.mount(label)
            container.mount(input_widget)

        yield container
        yield Button("Exécuter", id="run")
        yield Footer()

    async def on_button_pressed(self, event):
        if event.button.id == "run":
            args = []
            for name, widget in self.fields.items():
                val = widget.value
                if val:
                    args += [f"--{name}", val]
            subprocess.run(["python", "-m", "mem_cli", self.group_name, self.command_name] + args)
            self.exit()

def launch_dynamic_wizard(group_name: str, command_name: str):
    app = WizardDynamicApp(group_name, command_name)
    app.run()
