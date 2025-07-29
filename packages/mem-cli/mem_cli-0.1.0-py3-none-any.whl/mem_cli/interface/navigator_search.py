from textual.app import App, ComposeResult
from textual.widgets import Input, ListView, ListItem, Label, Header, Footer, Button
from textual.containers import Vertical
from mem_cli.commands import GROUPS
from mem_cli.interface.wizard_dynamic import launch_dynamic_wizard
from mem_cli.interface.doc_group import show_group_doc

class NavigatorSearchApp(App):
    CSS_PATH = "style.css"
    TITLE = "Navigation CLI interactive"

    def __init__(self):
        super().__init__()
        self.commands = []
        self.filtered = []
        for group, group_obj in GROUPS.items():
            for cmd_name, cmd in group_obj.commands.items():
                self.commands.append((group, cmd_name, cmd.help or ""))

    def compose(self) -> ComposeResult:
        yield Header()
        self.input = Input(placeholder="Rechercher une commande...", id="search")
        self.list_view = ListView(id="results")
        yield Vertical(self.input, self.list_view)
        yield Button("Documentation", id="doc")
        yield Footer()

    def on_mount(self):
        self.update_list()

    def update_list(self, query: str = ""):
        self.list_view.clear()
        self.filtered = [c for c in self.commands if query.lower() in f"{c[0]} {c[1]}".lower()]
        for group, cmd, helptext in self.filtered:
            self.list_view.append(ListItem(Label(f"{group} {cmd} : {helptext}")))

    async def on_input_changed(self, message):
        self.update_list(message.value)

    async def on_list_view_selected(self, event):
        group, cmd, _ = self.filtered[event.index]
        self.exit()
        launch_dynamic_wizard(group, cmd)

    async def on_button_pressed(self, event):
        if event.button.id == "doc" and self.filtered:
            group, *_ = self.filtered[0]
            self.exit()
            show_group_doc(group)

def launch_navigator_search():
    NavigatorSearchApp().run()
