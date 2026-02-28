# Salesforce — Frappe Sales Activity Module

A custom [Frappe](https://frappeframework.com/) application that helps field sales teams **plan, execute, and track customer visits** through structured activity logging and an automated coverage planning engine.

---

## What This Module Does

### 🗓️ Master Coverage Plan (MCP)
The **Master Coverage Plan** is the heart of the scheduling system. Managers define a list of customers assigned to a sales person, along with each customer's preferred visit days (Monday–Sunday) and visit frequency:

| Code | Meaning |
|---|---|
| `D1` | Every day |
| `M1` | Once a month (Week 1) |
| `M2` | Twice a month (Weeks 1 & 3) |
| `M4` | Four times a month (Weeks 1–4) |
| `Q1` | Once a quarter (first week of first month) |
| `Q2` | Twice a quarter (first week of months 1 & 2) |

Every day, a **scheduled job** (`generate_planned_calls`) runs automatically and creates `Salesforce Activity` records of type **"Planned Call"** for each customer whose visit is due that day. Key guard-rails built in:
- A cap of **20 planned calls per salesperson per day** — overflow is rescheduled to the next available matching day within a 60-day window.
- Duplicate prevention — a planned call is never created if one already exists for the same customer and day.
- Managers can also trigger generation on-demand for a specific MCP via `generate_planned_calls_on_demand`.

### 📋 Salesforce Activity
Tracks every customer interaction performed by a sales representative. Key behaviours:
- **Auto-assignment** — on save, the logged-in user's linked `Sales Person` record is automatically populated in the `sales_person` field.
- **Image enforcement** — at least one photo must be attached to the activity before it can be submitted (validated in `before_submit`).
- Activity types include **Planned Call**, **Actual Visit**, and more.

### 📸 Salesforce Activity Image
A child DocType that holds one or more images (with optional captions/GPS metadata) attached to a `Salesforce Activity`.

### 📊 Reports & Number Cards
- **Daily Activities Summary** — overview of what activities were completed on a given day.
- **Planned Calls Status** — tracks which planned calls were fulfilled, missed, or rescheduled.
- **Number Cards** — quick metrics for *My Completed Activities Today* and *My Planned Calls Today*, surfaced in the Salesforce Workspace dashboard.

---

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app salesforce
```

---

## Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/salesforce
pre-commit install
```

Pre-commit is configured with the following tools:

- **ruff** — Python linting & formatting
- **eslint** — JavaScript linting
- **prettier** — Code formatting
- **pyupgrade** — Modernises Python syntax

---

## License

MIT
