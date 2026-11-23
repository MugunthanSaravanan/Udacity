# GCP setup and verification checklist

This guide is specific to the Vocareum lab project supplied for Betty's Bird Boutique. It records local findings and the setup that would be needed for local agent testing. It does not authorize or perform GCP changes.

## Project and current verification status

Assigned project ID: `lab18633938-1795419661`.

| Item | Status | Finding |
| --- | --- | --- |
| Assigned project ID | Confirmed from user-provided lab details | `lab18633938-1795419661`; no other project should be selected. |
| Local Google Cloud CLI | Not available | `gcloud` is not on PATH and the usual SDK locations checked are absent. No CLI account or active project could be inspected. |
| Authentication / project access | Cannot be verified | No GCP login or API calls were attempted. The Vocareum browser session itself was not inspected. |
| Vertex AI API (`aiplatform.googleapis.com`) | Cannot be verified | No service-status query was possible. |
| Discovery Engine API (`discoveryengine.googleapis.com`) | Cannot be verified | No service-status query was possible. |
| Cloud SQL Admin API (`sqladmin.googleapis.com`) | Cannot be verified | Needed by the configured Cloud SQL Toolbox integration; status not queried. |
| Cloud Storage API (`storage.googleapis.com`) | Conditional / cannot be verified | Needed only if the chosen document ingestion workflow uses a GCS bucket. |
| Billing, lab credits, budgets, and quotas | Cannot be verified | Billing account and Vocareum lab budget are not visible from this local inspection. |
| Vertex AI Search data store and serving config | Cannot be verified | The code expects a data store ID, its actual location, and a serving config (default ID `default_config`); no resource listing was performed. |
| Cloud SQL instance and products table | Cannot be verified | The local SQL file defines an example schema and products; it does not prove a cloud instance exists. |
| Supplied documents | Confirmed locally | `bettys-history.pdf`, `bettys-hours.pdf`, and `bettys-staff.pdf` are in `docs/`; their cloud ingestion/indexing is not verified. |

“Cannot be verified” means no read-only cloud check was made. It does not mean the API or resource is disabled or absent.

## Authentication through Vocareum

1. Start the assigned lab in Vocareum and use only the credentials shown in that lab interface. Never copy the password into this repository, a terminal command, `.env`, or a screenshot.
2. Open Google Cloud Console using the lab-provided console link. Confirm the displayed signed-in identity is the temporary lab identity and the selected project is exactly `lab18633938-1795419661`.
3. If the lab provides Cloud Shell, use it only after confirming that same identity and project. Cloud Shell commonly includes `gcloud`; local `gcloud` is not installed on this machine.
4. If authentication or project access is denied, stop and ask the course/lab administrator. Do not switch to a corporate account or another project.

If an administrator later authorizes read-only CLI checks in the lab, these commands only display account/project context and enabled services; they do not enable services or modify resources:

```sh
gcloud auth list
gcloud config get-value project
gcloud projects describe lab18633938-1795419661 --format="value(projectId,lifecycleState)"
gcloud services list --enabled --project=lab18633938-1795419661 --format="value(config.name)"
```

Do not run them until using the Vocareum-provided identity. Do not run `gcloud auth login` with a corporate account. Billing visibility may require separate billing-account permissions and may still not show Vocareum's remaining lab budget.

## Minimum resources for local testing

The agent runs locally with `adk web`; it does not need a Compute Engine VM, Cloud Run, GKE, or another project. Local execution still sends requests to cloud APIs for Gemini and Vertex AI Search, and can incur usage charges.

| Capability | Minimum project-side prerequisite | Current code/configuration |
| --- | --- | --- |
| Gemini through Vertex AI | Assigned project, supported model/location, Vertex AI API, usable authentication and invocation permission | `agent.py` defaults to `gemini-3.5-flash-lite`; the user reports a successful call in Vocareum at `global`. That report has not been independently verified from this Windows environment. |
| Google Search grounding | Vertex AI Gemini access and the grounding feature allowed for the project/model; no separate custom search key is configured by this project | `search_agent.py` uses ADK `google_search`; organization policy and service terms still apply. |
| Store document Q&A | Existing Agent Search / Vertex AI Search data store and serving configuration, indexed documents, Discovery Engine API, search permission | `datastore.py` builds `.../collections/default_collection/dataStores/{VERTEX_AI_SEARCH_DATASTORE_ID}/servingConfigs/{VERTEX_AI_SEARCH_SERVING_CONFIG}`. Verify the actual ID, location, and config. |
| Document ingestion | The PDFs must be imported and indexed once in the chosen store. A GCS bucket and Cloud Storage API are needed only for a GCS-based ingestion path; a console/local upload workflow has its own requirements | The PDFs are supplied locally. No upload, import, or datastore creation has occurred. |
| Product price lookup | Existing reachable Cloud SQL for MySQL instance/database with the `products` table and sample/real rows, Toolbox server/configuration, database-level `SELECT` privilege | `tools.yaml` uses `cloud-sql-mysql`, env-based connection values, and a parameterized read-only `SELECT`. `docs/betty_db.sql` is only a local schema/sample-data reference. |

No additional GCP compute resource is required just to run the agent locally. If the assigned lab already has the search engine and database, reuse them; do not create replacements without instructor/lab authorization and a budget check.

## Required APIs

Check these in the assigned project before setup. None were checked or enabled during this task.

| API | Need | Status |
| --- | --- | --- |
| Vertex AI API — `aiplatform.googleapis.com` | Required for Gemini requests through Vertex AI and the configured grounding flow | Cannot be verified |
| Discovery Engine API — `discoveryengine.googleapis.com` | Required for the datastore search call in `datastore.py` | Cannot be verified |
| Cloud SQL Admin API — `sqladmin.googleapis.com` | Required by Cloud SQL connectivity through the Cloud SQL connector used by the Toolbox Cloud SQL integration | Cannot be verified |
| Cloud Storage API — `storage.googleapis.com` | Conditional: required if documents are ingested from a GCS bucket | Cannot be verified |
| Service Usage API — `serviceusage.googleapis.com` | Used for listing/enabling API services and checking service state; API inspection permissions are distinct from permission to enable services | Cannot be verified |

Do not enable an API as part of this checklist. Enabling services requires additional permission and can make billable products usable.

## IAM permissions to verify

Request only the narrow permissions needed for the assigned task. These are role candidates from Google Cloud documentation, not a statement that the lab user has them:

- **Gemini requests:** `roles/aiplatform.user` is the standard Agent Platform user role for generative AI use.
- **Search queries:** `roles/discoveryengine.viewer` includes `discoveryengine.servingConfigs.search`; a narrower custom role may be preferable if the lab administrator supports it.
- **Cloud SQL connector:** `roles/cloudsql.client` is needed for connector-based connectivity. `roles/cloudsql.instanceUser` is additionally relevant if the database connection uses IAM database authentication. Built-in MySQL authentication also needs a MySQL user with only the required database/table privileges.
- **Read-only API/resource inspection:** project metadata and service-list permissions may be needed. `serviceusage.services.enable` is separate and must not be granted or used for this inspection task.
- **Creating a search app/datastore or changing ingestion:** requires additional Discovery Engine administration/editor permissions. Ask the lab administrator to perform or explicitly authorize these actions; do not assume a search-only role permits setup.
- **GCS ingestion:** requires access to the chosen bucket and its objects; the precise role depends on whether the task only reads existing objects or also creates/uploads them.

Google documents the Discovery Engine search permission in [Agent Search access control](https://docs.cloud.google.com/generative-ai-app-builder/docs/access-control), Cloud SQL connector access in [Cloud SQL roles and permissions](https://docs.cloud.google.com/sql/docs/mysql/roles-and-permissions), and Cloud SQL Toolbox API/IAM prerequisites in [Use Cloud SQL for MySQL with MCP Toolbox](https://docs.cloud.google.com/sql/docs/mysql/pre-built-tools-with-mcp-toolbox).

## Local environment variables

Use a private `submission/.env` created from `.env.example`; never commit it. The current template uses placeholders, and no real `.env` or credential file was opened.

| Variable | Value to configure after verification |
| --- | --- |
| `GOOGLE_CLOUD_PROJECT` | `lab18633938-1795419661` only after confirming that the Vocareum lab session has selected this project |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI model location; user reports `global` for their successful Gemini call; verify at runtime |
| `GOOGLE_GENAI_USE_VERTEXAI` | `true` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Prefer Vocareum/Cloud Shell ADC where available. If a key path is specifically required, use only a lab-provided, private local file; never include the file in submission. |
| `VERTEX_AI_SEARCH_PROJECT_ID` | Project containing the Search data store; expected to be the assigned project if the data store is there |
| `VERTEX_AI_SEARCH_DATASTORE_ID` | Existing data store ID; verify it in the lab console |
| `VERTEX_AI_SEARCH_LOCATION` | Actual data store location; do not infer it from the Gemini model location |
| `VERTEX_AI_SEARCH_SERVING_CONFIG` | Existing serving configuration ID; code defaults to `default_config` |
| `CLOUD_SQL_MYSQL_PROJECT` | Project containing the existing MySQL instance; expected assigned project if hosted there |
| `CLOUD_SQL_MYSQL_REGION`, `CLOUD_SQL_MYSQL_INSTANCE` | Exact location and instance name from a verified existing instance |
| `CLOUD_SQL_MYSQL_DATABASE` | Database containing the `products` table; local SQL reference uses `betty` |
| `CLOUD_SQL_MYSQL_USER`, `CLOUD_SQL_MYSQL_PASSWORD` | Existing least-privilege MySQL account values, supplied privately; never paste into chat, logs, or screenshots |
| `TOOLBOX_URL` | Local Toolbox endpoint, normally `http://127.0.0.1:5000` |

## Cost and lab risk

No billing account, lab-credit balance, budget, quota, or existing-resource list was accessible in this inspection. Do not infer that a Vocareum lab has remaining credits or that a project is free to use.

Potential charges include Gemini input/output tokens, Google Search grounding requests, Agent Search query and index-storage usage, document processing/ingestion, Cloud SQL instance runtime/storage/backups, and GCS storage/requests if used. Local `adk web` avoids compute deployment but does not make API calls free. The [Agent Search pricing page](https://cloud.google.com/generative-ai-app-builder/pricing) and [Agent Platform pricing page](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing) describe usage-based charges; pricing and free allowances can change and may not apply to a lab account. Get the instructor's current budget guidance before creating resources or performing document ingestion.

## Recommended setup order

1. Start the Vocareum lab and verify its temporary identity and the exact assigned project ID in the lab-provided Console.
2. In read-only views, check project access, billing/lab-budget guidance, quotas, enabled APIs, IAM roles, and whether a search engine and Cloud SQL instance already exist.
3. Reuse existing resources where available. Confirm the search app ID, serving location/configuration, indexed PDFs, SQL instance/database, and product table.
4. If something is absent, stop and ask the instructor/lab administrator whether it may be created, who should create it, which API/role is authorized, and what cost limit applies.
5. Configure the local `.env` from verified values only. Keep credentials private; do not change the source code or create service-account keys just to work around missing lab access.
6. Start the local Toolbox process only after its endpoint and database connection are approved/configured. Then run the local ADK UI and test one tool at a time, watching lab usage.
7. Stop local processes after testing. For any cloud resource explicitly created later with authorization, follow the lab's cleanup process; only clean up resources you created and were authorized to remove. Never delete instructor- or lab-provided resources. Confirm whether search indexes, buckets, SQL storage/backups, or other billable resources remain before ending the lab.

## Reference links

- [Vertex AI access control](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/access-control)
- [Agent Search API setup and access control](https://docs.cloud.google.com/generative-ai-app-builder/docs/access-control)
- [Agent Search document ingestion](https://docs.cloud.google.com/generative-ai-app-builder/docs/prepare-data)
- [Grounding with Google Search](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/grounding-with-google-search)
- [MCP Toolbox for Cloud SQL MySQL](https://docs.cloud.google.com/sql/docs/mysql/pre-built-tools-with-mcp-toolbox)
- [Agent Search pricing](https://cloud.google.com/generative-ai-app-builder/pricing)
- [Vertex AI / Agent Platform pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)
