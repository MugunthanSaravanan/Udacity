# Rubric audit

Status definitions: **PASS** means the specified local check succeeded; **PARTIAL** means source or offline behavior is present but a runtime integration remains unverified; **BLOCKED** means an external service, package, or authorized lab check is required; **NOT RUN** means not attempted.

| Requirement | Implementation | Verification and status |
| --- | --- | --- |
| ADK root agent with name, description and prompt | `agent.py`, `agent-prompt.txt` | Source reviewed; ADK imports unavailable in venv. **PARTIAL** |
| Suitable Gemini model configuration | `agent.py`, `.env.example` | Defaults to user-reported `gemini-3.5-flash-lite`; user-reported Vocareum success not independently verified. **PARTIAL** |
| Short-term session history and reusable runner helpers | `agent.py`, `agents.py` | Source reviewed and syntax compiled; ADK session API not runtime-tested. **PARTIAL** |
| Three sources available to root agent | `agent.py` | Static test checks all three function/tool references; ADK tool registration not runtime-tested. **PARTIAL** |
| Store question retrieval uses configured Search data store | `datastore.py` | Offline mock tests cover env routing, empty/missing config, snippets, and safe errors. Google client unavailable; no live query. **PARTIAL** |
| Product lookup via Toolbox/MySQL | `product_tool.py`, `tools.yaml` | Offline fake-client tests cover success, partial name, empty query, and sanitized failures. Toolbox/database not installed or connected. **PARTIAL** |
| SQL matches supplied schema and parameterizes wildcard lookup | `tools.yaml`, `docs/betty_db.sql` | Offline schema assertion passed. Schema contains only id, product name, price. **PASS** |
| Google Search specialist is isolated and returns grounding metadata | `search_agent.py` | Static test checks `google_search`, `AgentTool`, metadata propagation, and prompt boundaries. No ADK runtime or live search test. **PARTIAL** |
| Prompt guardrails and source-use instructions | `agent-prompt.txt`, `search-prompt.txt` | Offline content assertions passed; model behavior not observed. **PARTIAL** |
| README, setup guide, GCP checklist, safe config template and evidence checklist | Project docs | Files reviewed; cloud details remain user-reported or unverified. **PASS** for local documentation presence |
| Python syntax | Project Python files | `.venv\Scripts\python.exe -m compileall -q .` succeeded. **PASS** |
| Offline unit tests | `tests/` | `.venv\Scripts\python.exe -m unittest discover -s tests -v`: 18 passed. **PASS** |
| Application dependency install/import | `requirements.txt` | Only pip is present; pip install previously failed with `ConnectionAbortedError(10053)`. No packages installed during this work. **BLOCKED** |
| Lint/type checking | Project config | No Ruff, mypy, or pytest config/tool was present in the venv. Dedicated static tools not run. **NOT RUN** |
| Live Gemini, Search, Google Search grounding, Toolbox/MySQL | External services | No external API calls or GCP access made. Vocareum result is user-reported only. **BLOCKED** |
| Submission evidence screenshots | `evidence/README.md` | Checklist exists; live captures must be collected in authorized lab. **NOT RUN** |

## Remaining verification

Use the course-approved package repository/network route to install dependencies in `.venv`, after confirming Python version support. Then run the installed ADK version against the authorized lab and capture truthful evidence. Confirm actual data store ID/location/serving configuration and live database availability before claiming those integrations work. Do not create resources or use another project to work around missing access.
