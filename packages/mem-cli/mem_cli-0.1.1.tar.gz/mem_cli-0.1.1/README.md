# mem_cli

**mem_cli** est une interface CLI interactive extensible, construite avec [Click](https://click.palletsprojects.com/), [Textual](https://textual.textualize.io/) et [Rich](https://rich.readthedocs.io/).

## 🚀 Fonctionnalités

- 🎛 Navigation CLI interactive avec recherche en temps réel
- 🧙 Wizard dynamique de commandes basé sur les types Click
- 📘 Documentation CLI interactive par groupe (markdown stylisé)
- 🧩 Système modulaire basé sur l'auto-enregistrement des commandes
- 🛠 Commandes Click exposées à la racine du package pour usage simplifié

## 📦 Installation

```bash
pip install .
# ou en mode développement
pip install -e .
```

## 🛠 Utilisation

```bash
mem-cli --help
python -m mem_cli
```

## 🧪 Développement

```bash
make install
make build
make test
make clean
```

## 📤 Publication

```bash
make publish  # nécessite configuration .pypirc
```

## 📁 Arborescence

```
src/
└── mem_cli/
    ├── __init__.py  # exports Click decorators
    ├── __main__.py
    ├── interface/
    │   ├── wizard_dynamic.py
    │   ├── navigator_search.py
    │   ├── doc_group.py
    │   └── style.css
    └── commands/
        └── __init__.py
```

## 🧑‍💻 Auteur

Guillaume Lefebvre — guillaume@ldmail.fr
