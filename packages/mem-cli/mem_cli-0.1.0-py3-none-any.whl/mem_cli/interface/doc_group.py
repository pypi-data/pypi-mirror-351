from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, MarkdownViewer
from textual.containers import Container
from mem_cli.commands import GROUPS
import click

class GroupDocApp(App):
    CSS_PATH = "style.css"
    TITLE = "Documentation CLI"

    def __init__(self, markdown: str):
        super().__init__()
        self.markdown = markdown

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(MarkdownViewer(self.markdown))
        yield Footer()

def show_group_doc(group_name: str):
    if group_name not in GROUPS:
        raise click.ClickException(f"Groupe '{group_name}' introuvable.")

    group = GROUPS[group_name]
    md = f"# Groupe `{group_name}`\n\n{group.help or ''}\n\n## Commandes disponibles :\n"
    for cmd_name, cmd in group.commands.items():
        md += f"### `{cmd_name}`\n{cmd.help or ''}\n\n"
        for param in cmd.params:
            md += f"- `--{param.name}` : {param.help or ''} (default={param.default})\n"
    GroupDocApp(md).run()
