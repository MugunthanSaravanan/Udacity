# Betty's Bird Boutique customer service agent

This project is a Google ADK agent with three specialist capabilities:

- **Store facts:** Vertex AI Search / Discovery Engine, using the configured data store and serving configuration.
- **Product lookup:** MCP Toolbox connected to MySQL, querying product names and prices from the supplied schema.
- **General bird questions:** Google Search grounding through an ADK specialist agent.

The root agent also uses ADK's in-memory session service for short-term conversation history. The project does not place orders, change cloud resources, or provision services.

## Requirements and local checks

The project requires Python and the packages listed in `requirements.txt`. No package installation or live integration check is implied by this repository. From the project directory, run offline tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

If this environment cannot install packages, see `docs/setup-and-usage.md`; do not bypass corporate network or certificate controls.

## Configuration

Copy `.env.example` to `.env` and fill in values only after confirming the lab's actual project, model location, Search data store, and Toolbox/database endpoint. Keep `.env`, passwords, and credential files private. The model location and Search location are separate settings. Use the Vocareum-provided authenticated environment where available; Windows local processes do not automatically inherit Cloud Shell authentication.

See [setup and usage](docs/setup-and-usage.md) and the [GCP setup checklist](docs/gcp-setup-checklist.md). These documents distinguish user-reported lab information from independently verified state. No GCP resources were inspected or modified as part of the local project work.

## Project files

```text
submission/
├── agent.py
├── agents.py
├── datastore.py
├── product_tool.py
├── search_agent.py
├── agent-prompt.txt
├── search-prompt.txt
├── tools.yaml
├── requirements.txt
├── .env.example
├── docs/
├── tests/
└── evidence/
```

The local SQL definition is `docs/betty_db.sql`. Its products table has only `id`, `product_name`, and `price`; it contains no description, stock, or availability fields.
