# Family Expense AI — MCP-Based Expense Assistant

A real, working family expense/income/budget assistant whose financial
capabilities are exposed as **MCP (Model Context Protocol) tools** through a
**FastMCP** server, backed by **PostgreSQL**. This is not a chatbot with a
database bolted on — MCP is the core of the architecture: any
MCP-compatible LLM client (Claude Desktop, or Claude via a remote
connector) discovers and invokes these tools directly.

## Architecture

```text
                    User
                     |
                AI / LLM (e.g. Claude)
                     |
              MCP Protocol
                     |
             FastMCP Server (main.py)
                     |
               MCP Tools (23 tools)
          +----------+----------+-----------+
          |          |          |           |
      Family     Expenses    Income   Reports/Budgets/Insights
          |          |          |           |
          +----------+----------+-----------+
                     |
                 PostgreSQL
```

Remote usage (Claude connecting to a deployed server):

```text
Claude -> MCP Connector -> HTTPS -> Remote MCP Server (Render)
                                       -> FastMCP -> MCP Tools -> PostgreSQL
```

The LLM only ever *understands the request*, *selects a tool*, and
*generates parameters*. Validation, business logic, calculations, and all
persistence happen in `app/services/*`, with **PostgreSQL as the single
source of truth**.

## Multi-user family usage (one shared database, many Claude accounts)

Each family member can run their **own** Claude account/client connected to
the **same** deployed MCP server (`https://<your-app>.onrender.com/mcp`).
When someone says "I spent ₹500 on lunch," their Claude calls `add_expense`
with `member_name` set to that person — the server resolves the name to a
`member_id` and writes it into the one shared Postgres database. So the
whole family's spending naturally converges into a single source of truth,
per person, without needing separate databases per user.

Tips for this setup:
- Register everyone once with `add_family_member` (e.g. Praneeth → Self,
  Rahul → Brother, Mom → Mother).
- Give each person's Claude a system/custom instruction like *"My name is
  Rahul — when using Family Expense tools, use member_name='Rahul' unless
  I say otherwise."* so they don't have to repeat their name every time.
- Every report/insight/budget tool accepts an optional `member_name` to
  scope results to one person, or omit it for the whole family.

## Project structure

```text
mcp-famil/
├── main.py                # FastMCP server: 23 MCP tools, thin wrappers
├── chatbot.py              # Local NL test harness (no MCP client needed)
├── tool_router.py          # Dispatches tool name + params -> service call
├── formatter.py             # Raw results -> clean, INR-formatted text
├── requirements.txt
├── .env.example
├── .gitignore
├── render.yaml              # One-file Render deployment config
│
├── app/
│   ├── db/
│   │   ├── connection.py    # psycopg2 pool + init_db()
│   │   └── schema.sql       # Table definitions
│   ├── services/            # Business logic + validation (DB access only here)
│   │   ├── errors.py
│   │   ├── validators.py
│   │   ├── date_utils.py
│   │   ├── family_service.py
│   │   ├── expense_service.py
│   │   ├── income_service.py
│   │   ├── summary_service.py
│   │   ├── report_service.py
│   │   ├── budget_service.py
│   │   └── insight_service.py
│   └── ai/
│       ├── schemas.py           # Anthropic tool-use schemas (mirrors main.py)
│       ├── intent_parser.py     # NL -> (tool, params) via Claude tool-use
│       ├── category_detector.py # Keyword-based expense category guesser
│       ├── reports.py           # Rule-based report phrase parsing
│       ├── budget.py            # Rule-based budget phrase parsing
│       └── insights.py          # Suggestion generation from real DB numbers
│
└── tests/
```

## Database schema

- **family_members**(id, name, relationship, created_at)
- **expenses**(id, member_id → family_members, amount, category, expense_date, description, created_at, updated_at)
- **income**(id, member_id → family_members, amount, source, income_date, notes, created_at, updated_at)
- **budgets**(id, category, amount, created_at, updated_at)

Applied automatically on startup via `init_db()` (idempotent
`CREATE TABLE IF NOT EXISTS`), so there's no separate migration step to run.

## MCP tools (23)

| Area | Tools |
|---|---|
| Family | `add_family_member`, `list_family_members` |
| Expenses | `add_expense`, `list_expenses`, `update_expense`, `delete_expense` |
| Income | `add_income`, `list_income`, `update_income`, `delete_income` |
| Summary | `total_income`, `total_expenses`, `current_balance`, `expenses_by_category`, `expenses_by_member` |
| Reports | `monthly_income`, `monthly_expenses`, `monthly_summary`, `compare_months` |
| Budgets | `set_budget`, `list_budgets`, `budget_status` |
| Insights | `financial_insights` |

Every tool is a thin wrapper: it calls `tool_router.route()` (which calls
into `app/services/*`) and formats the result with `formatter.py` before
returning it — so the response an LLM/user sees is already a clean,
₹-formatted message, not a raw JSON blob.

## Currency

Everything is INR (₹), formatted with Indian digit grouping
(e.g. `₹12,34,567.00`, not `₹1,234,567.00`). Amounts are stored as
`NUMERIC(12,2)` in Postgres and only formatted at the presentation layer.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # edit .env: set DATABASE_URL to your PostgreSQL connection string
   # (LLM_API_KEY is only needed for chatbot.py, not for the MCP server itself)
   ```

3. **Run the MCP server**
   ```bash
   python main.py
   # Tables are created automatically. MCP endpoint: http://localhost:8000/mcp
   ```

4. **(Optional) Try the local natural-language chatbot**
   ```bash
   python chatbot.py
   ```
   Example session:
   ```text
   You: Rahul spent ₹700 on petrol today.
   AI: ✅ Expense Added

       👤 Rahul
       💸 ₹700.00
       📂 Petrol
       📅 2026-09-06
   ```

## Local testing with an MCP client

With `python main.py` running, point any MCP-compatible client at
`http://localhost:8000/mcp` (Streamable HTTP transport) and confirm all 23
tools are discoverable. For example, using the FastMCP CLI:
```bash
fastmcp dev main.py
```

> Note: depending on your installed `fastmcp` version, the transport name
> passed to `mcp.run()` in `main.py` may need to be `"streamable-http"`
> instead of `"http"`. Check `fastmcp --version` / release notes if the
> server fails to start.

## Using Supabase as the database

Supabase's database is plain PostgreSQL, so **no code changes are
needed** — just point `DATABASE_URL` at it:

1. Create a project at [supabase.com](https://supabase.com).
2. Go to **Project Settings → Database → Connection string → URI**.
   Use the **Session pooler** (or **Transaction pooler**) connection
   string, not the direct connection — it's the one meant for
   long-running apps and works fine with this project's connection pool.
3. Copy it into `DATABASE_URL` in your `.env` (or your host's environment
   variables), replacing `[YOUR-PASSWORD]` with your actual DB password:
   ```text
   DATABASE_URL=postgresql://postgres.xxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-xx-xxxx-x.pooler.supabase.com:5432/postgres
   ```
4. Run `python main.py` (or redeploy your host) — `init_db()` creates the
   `family_members`, `expenses`, `income`, and `budgets` tables on Supabase
   automatically on first boot. `SUPABASE_URL`/`SUPABASE_KEY` are **not**
   needed for this — those are only for the Supabase client SDK, which
   this project doesn't use.

## Deployment

You need somewhere to run the always-on Python process — Supabase only
hosts the database, not the app. Any host that gives you a public
**HTTPS** URL works (Claude's remote connector requires HTTPS, not plain
HTTP). Whatever you choose, the server just needs:
- `DATABASE_URL` set to your Supabase connection string
- To listen on `0.0.0.0:$PORT` (already handled by `main.py`)
- The `/mcp` path reachable over HTTPS at the root of your public URL

`render.yaml` is included for a one-file Render deploy if you want it:
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `python main.py`
- **Environment variables:** `DATABASE_URL`, `LLM_API_KEY` (optional), `ANTHROPIC_MODEL` (optional)

If you're self-hosting on your own server/VPS instead, make sure a
reverse proxy (Caddy, nginx + certbot, etc.) terminates TLS in front of
`main.py` and forwards to it — Claude cannot connect to a bare `http://`
URL or a self-signed certificate.

### Verify the deployed server before adding it to Claude

```bash
curl -s -D - -o /dev/null -X POST https://<your-domain>/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```
You should get `HTTP/1.1 200` back with a `serverInfo` block naming
"Family Expense MCP". If this fails, fix it before adding the connector —
Claude will hit the same URL.

## Add it to Claude as a custom connector

1. On [claude.ai](https://claude.ai), go to **Settings → Connectors**.
2. Click **Add custom connector**.
3. Enter a name (e.g. "Family Expense AI") and the URL:
   `https://<your-domain>/mcp`
4. Save, then enable the connector in a chat (the tool/connector picker
   below the message box).
5. Test it: ask Claude something like *"Add a family member named
   Praneeth, relationship Self"* or *"I spent ₹500 on lunch today"* — Claude
   should call the corresponding MCP tool and show the formatted result.

Every family member can add the same URL as their own custom connector
from their own claude.ai account — they all talk to the same hosted
server and the same Supabase database, so everyone's expenses land in one
shared, per-person-tracked source of truth (see "Multi-user family usage"
above).

## Example natural-language flow

**User:** "Rahul spent ₹700 on petrol today."

1. LLM determines intent: `add_expense`, `member_name=Rahul`, `amount=700`, `category=Petrol`, `expense_date=today`
2. `add_expense` tool → `tool_router.route()` → `expense_service.add_expense()`
3. Resolves "Rahul" → `member_id`, validates the amount, inserts the row
4. Result formatted and returned:
   ```text
   ✅ Expense Added

   👤 Rahul
   💸 ₹700.00
   📂 Petrol
   ```

## Error handling

Every tool call is wrapped so it never crashes the server. Domain errors
(`ValidationError`, `NotFoundError`) are caught and returned as a friendly
`⚠️ ...` message — covering: unknown family member, invalid/negative
amount, missing required parameter, unparseable date, expense/income not
found, no budget set for a category, unknown tool, and any unexpected
exception (`❌ Unexpected error: ...`).

## Security

No credentials are hardcoded anywhere. `DATABASE_URL` and `LLM_API_KEY`
are read from the environment (`.env`, gitignored). `.env.example`
documents every variable without real values.

## Running tests

```bash
pytest
```

Unit tests (formatter, validators, date parsing, category detection,
rule-based NL parsing, tool routing) run with no external services.
`tests/test_integration.py` exercises real database round-trips and is
skipped automatically unless `DATABASE_URL` points at a database.
