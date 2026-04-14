# 1071 MultiRepo RELE Tools

Orchestrierungs-Repository fuer ein zentrales Streamlit-Dashboard.
Die Fachlogik bleibt in den drei Einzelrepos und wird hier ueber Submodule eingebunden.

## Zielbild

- Ein gemeinsamer Einstiegspunkt fuer Anwender
- Drei Tool-Seiten in einer App:
  - 1049 PDF-Extraktor LBV
  - 1067 RELElisten-Extraktor
  - 1052 Buchungsimporteur SAP LBV
- Hohe Wartbarkeit durch klare Trennung: UI/Orchestrierung hier, Business-Logik in den Tool-Repos

## Lokaler Start

```bash
uv sync
uv run streamlit run streamlit_app.py
```

## Struktur

```text
streamlit_app.py
app_pages/
src/dashboard/
src/dashboard/integrations/
tools/
```

- `app_pages/`: Streamlit-Unterseiten je Tool
- `src/dashboard/integrations/`: Adapter-Schicht zu den Tool-Submodulen
- `tools/`: Submodule der Einzelanwendungen

## Submodul-Runbook

### Grundprinzip

Dieses Repo (`1071`) nutzt Tool-Repositories als Git-Submodule.
Jedes Submodul ist auf einen festen Commit fixiert.

Das bedeutet:

- Tool-Aenderungen sind nicht automatisch im Dashboard sichtbar.
- Das Dashboard sieht neue Aenderungen erst, wenn der Submodul-Pointer in `1071` aktualisiert und committed wurde.

### Einmaliges Setup

```bash
git clone --recurse-submodules <1071-repo-url>
cd 1071_MultiRepo_Rele-Tools
git submodule update --init --recursive
uv sync
```

### Tool weiterentwickeln und in 1071 uebernehmen

1. Im Tool-Repo entwickeln, testen, committen.
2. In `1071` den Submodulstand auf den gewuenschten Commit aktualisieren.
3. In `1071` den geaenderten Submodul-Pointer committen.

Beispiel:

```bash
git -C "tools/<submodule-pfad>" fetch origin
git -C "tools/<submodule-pfad>" checkout <commit-oder-tag>
git add "tools/<submodule-pfad>"
git commit -m "Update <tool-name> submodule to <commit/tag>"
```

### Nach Pull auf neuem Rechner

```bash
git submodule update --init --recursive
```

## Qualitaetschecks

```bash
uv run ruff check .
uv run ruff format .
uv run mypy .
uv run pytest
```
