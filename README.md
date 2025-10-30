## Muti-Tenant SAS

# install uv (Windows)

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

```


# install uv (Linux/MacOS)

```
curl -LsSf https://astral.sh/uv/install.sh | sh

```


# Clone the repo

```
git clone https://github.com/emekadefirst/NoteApp-Saas.git SAASTEST

```

# Change Directory into SAASTEST

```
uv sync --frozen

```

# Activate the env


 .venv\Scripts\activate (windows CMD)

source .venv\Scripts\activate (windows GitBash)

source .venv\bin\activate  (Linux/MacOS terminal)


# Run Seed Data for Admin, Permission and Permission Groups

```
uv run seed

```


# run server

```
uv run dev

```