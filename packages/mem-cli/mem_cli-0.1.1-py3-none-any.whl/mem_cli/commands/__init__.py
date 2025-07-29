import importlib
import pkgutil
import click

GROUPS = {}

for _, group_name, _ in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{group_name}")
    if hasattr(module, "cli_group") and isinstance(module.cli_group, click.Group):
        GROUPS[group_name] = module.cli_group
