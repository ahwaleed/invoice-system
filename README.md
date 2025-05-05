# Invoice Reimbursement System – Backend

FastAPI · SQLAlchemy 2 (Async) · SQLite (dev) / PostgreSQL (prod) · JWT Auth  
A compact, production‑style service that lets **Employees** upload invoice CSVs and **Managers** review, approve/reject, and analyse spend.

---

## ✨ Feature Highlights
| Area | Details |
|------|---------|
| **Auth & RBAC** | JWT (HS256) login, roles = Employee · Manager, login rate‑limit 5/min/IP |
| **CSV ingestion** | 5 MB max, header validation, streaming parse, duplicate detection |
| **Invoice workflow** | Pending ➜ Approved / Rejected, manager comments, audit history |
| **add‑on** | `/reports/monthly?year=YYYY` – spend dashboard (totals per employee per month) |
| **Docs** | Auto‑generated OpenAPI & Swagger UI at `/docs` |
| **Async stack** | Uvicorn + uvloop, aiosqlite, non‑blocking endpoints |

---

## 🛠️ Requirements
* **Python 3.11** (pin tested)
* `pip install -r requirements.txt`
  * optional: `requests jq` for the demo script

---

## 🚀 Quick‑start (local SQLite)

```bash
# 1 Clone & env
git clone <repo-url> invoice-system
cd invoice-system
python3.11 -m venv venv && source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2 Run
uvicorn app.main:app --reload      # http://127.0.0.1:8000/docs

# 3 Seed demo users (password = secret)
python scripts/seed_users.py


## Usage:
```bash
# Login (Employee) – grab JWT
EMP=$(curl -s -X POST http://127.0.0.1:8000/login \
        -d "username=alice" -d "password=secret" | jq -r .access_token)

# Upload CSV
curl -X POST http://127.0.0.1:8000/invoices/upload \
     -H "Authorization: Bearer $EMP" \
     -F "file=@sample-data/sample_invoices.csv"

# Login (Manager)
MAN=$(curl -s -X POST http://127.0.0.1:8000/login \
        -d "username=bob" -d "password=secret" | jq -r .access_token)

# List invoices
curl -H "Authorization: Bearer $MAN" http://127.0.0.1:8000/invoices

# Approve first invoice
curl -X POST http://127.0.0.1:8000/invoices/1/approve \
     -H "Authorization: Bearer $MAN" \
     -H "Content-Type: application/json" \
     -d '{"comment":"Looks good"}'
