# Setup and usage

## Environment status

The project `.venv` uses Python 3.15.2, but its required application packages were not available during local inspection. Earlier pip network requests failed with `ConnectionAbortedError(10053)`. Do not repeatedly retry installation or bypass network controls. Python 3.15 is very new relative to some dependencies; package wheel/support status must be confirmed from the approved package index before choosing a different Python version. Dependency versions are left as specified in `requirements.txt`.

When package access is available through the approved route, use the venv executable directly in PowerShell (activation is unnecessary):

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Do not install globally. If an install fails, retain the exact package/error and ask the course or corporate IT administrator which package repository and interpreter version are supported. Do not alter pip proxy, index, certificate, PATH, or execution policy settings as a workaround.

## Environment variables

Copy `.env.example` to `.env`, then replace placeholders using verified values. Never commit `.env`, database passwords, API tokens, or service-account keys. Prefer the Vocareum lab's provided authentication in the environment where the agent runs. Cloud Shell ADC is not automatically available to a separate Windows process. No service-account key is required by this source code.

| Setting | Purpose |
| --- | --- |
| `GOOGLE_CLOUD_PROJECT` | Project used for Vertex AI model requests. |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI model location, reported by the user as `global`; verify it in the actual runtime. |
| `GOOGLE_GENAI_USE_VERTEXAI` | Select Vertex AI for Google Gen AI. |
| `GEMINI_MODEL` | Model name; defaults to `gemini-3.5-flash-lite` as reported successful by the user in Vocareum. |
| `VERTEX_AI_SEARCH_PROJECT_ID` | Project that owns the Search data store; falls back to `GOOGLE_CLOUD_PROJECT`. |
| `VERTEX_AI_SEARCH_LOCATION` | Location of the Search data store. It is independent of the Gemini model location. |
| `VERTEX_AI_SEARCH_DATASTORE_ID` | Existing data store ID. |
| `VERTEX_AI_SEARCH_SERVING_CONFIG` | Existing serving config ID; defaults to `default_config`. |
| `TOOLBOX_URL` | MCP Toolbox endpoint; defaults to `http://127.0.0.1:5000`. |
| `CLOUD_SQL_MYSQL_*` | Toolbox source connection settings, provided to the Toolbox process securely. |

The exact Search resource is constructed as `projects/{project}/locations/{location}/collections/default_collection/dataStores/{datastore}/servingConfigs/{serving_config}`. Confirm the real data store ID, location and serving config before use. The user's report that Vertex AI and Discovery Engine are enabled and Gemini worked in Vocareum has not been independently checked here.

## Start the local components

1. Ensure approved dependencies are installed in `.venv`.
2. Configure `.env` from verified values.
3. Start MCP Toolbox using the version and launch method approved by the course environment, with the database values available to that process. The project has a `tools.yaml` source/tool declaration; this repository does not provision the SQL instance or start a managed Toolbox service.
4. Start the ADK development UI from the directory above `submission` with the project's venv, using the ADK command documented for the installed version. Select the `submission` agent.
5. Reuse the same user and session ID for follow-up turns. `agents.py` exposes `create_runner()`, `create_session(user_id)` and `send_message(...)` for scripted local use.

The runner uses `InMemorySessionService`, so sessions are process-local and lost when the process stops. ADK UI session behavior depends on the installed ADK version and runtime.

## Offline validation

Run dependency-free unit tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

If `pytest` or configured lint/type-check tools are installed, they can be run separately; no packages should be added just for those checks while package access is blocked. These unit tests use fakes and do not verify cloud connectivity or API permissions.

## Manual live checks (only in the authorized lab)

After course/lab authorization and configuration, test one store-hours question, one Betty history question, one product lookup, and one general bird question. Inspect tool call and result in the UI, confirm source attribution for grounded responses, and check a follow-up for session context. Live calls may consume lab quota/credits. Do not create resources, enable APIs, or upload/index files without separate authorization and a budget check. Record only results actually observed; use `evidence/README.md` as the capture checklist.

## Data limits and errors

The supplied SQL schema exposes product IDs, names and prices only. The agent must not invent descriptions or stock availability. Product-tool errors are returned as a generic temporary-unavailable response to avoid exposing connection details. Datastore search reports missing configuration separately and sanitizes API errors. Search results still depend on the existing index and its ingestion state.
