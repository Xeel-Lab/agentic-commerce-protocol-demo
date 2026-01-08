
# ACP-style Merchant API — Render + ChatGPT GPT Actions

This package exposes an **ACP-like checkout API** you can deploy on **Render.com**
and hook into **ChatGPT via GPT Actions** (schema = `/openapi.json`).

## Features
- FastAPI with **OpenAPI** (public, read-only) at `/openapi.json`
- **API Key** auth via `X-API-Key` (required on commerce endpoints)
- **CORS** enabled
- Endpoints (spec-ish):
  - `POST /checkout/sessions` (create) — *idempotent*
  - `POST /checkout/sessions/{id}` (update)
  - `POST /checkout/sessions/{id}/complete` (complete) — *idempotent*
  - `GET /products` (public catalog preview)
- Multi-item cart + totals (subtotal, discount WELCOME10, tax 22%, shipping 5€ < 50)
- **MotherDuck/DuckDB** persistence (auto init + seed)
- **Stripe (test)** via PaymentIntents (SPT mocked)

## Deploy on Render
1. Push this folder to a GitHub repo.
2. In Render → *New* → *Blueprint* → select repo (uses `render.yaml`).
3. Set env vars:
   - `API_KEY` (choose a strong secret; used by GPT Actions)
   - `STRIPE_SECRET_KEY` (test key, `sk_test_...`)
   - `STRIPE_WEBHOOK_SECRET` (optional unless you configure Stripe webhooks)
   - `MOTHERDUCK_TOKEN` (optional; if missing, uses local DuckDB)
   - `MOTHERDUCK_DATABASE` (optional; default `acp_demo`)
   - `PUBLIC_BASE_URL` (your Render service URL, e.g. `https://agentic-commerce-protocol-demo.onrender.com` - required for OpenAPI schema and product links)
4. Deploy. After boot, note your base URL, e.g.: `https://agentic-commerce-protocol-demo.onrender.com`

## Connect to ChatGPT via GPT Actions
1. In ChatGPT → *Explore GPTs* → *Create* → *Actions* → *Add action*.
2. **Schema URL**: paste your Render URL + `/openapi.json`, e.g.  
   `https://agentic-commerce-protocol-demo.onrender.com/openapi.json`
3. **Auth**: select **API Key** and set header **`X-API-Key`** to your `API_KEY` value.
4. Save the GPT (private or workspace).

Now in chat you can ask your GPT, e.g. “Trova 2 articoli e completa l’ordine”:
- The GPT will call: `/products` → `/checkout/sessions` → `/checkout/sessions/{id}` → `/checkout/sessions/{id}/complete`

> Note: this is **not** Instant Checkout. Payments are test-only and SPT is mocked.
