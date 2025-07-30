# Sentr

**High-performance, open-source middleware that blocks card-testing traffic _before_ it reaches Stripe.**

[![PyPI version](https://badge.fury.io/py/sentr.svg)](https://pypi.org/project/sentr/)
[![Python 3.8‒3.12](https://img.shields.io/badge/python-3.8--3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

Card-testing attacks burn fee budgets, pollute customer analytics and increase charge-back risk. **Sentr** stops these requests inside your application layer in < 1 ms, so only legitimate traffic reaches Stripe.

*Written in modern Python, built for developer velocity, shipped under the MIT license.*

---

## Key Capabilities

| Capability | Detail |
|------------|--------|
| **Sub-millisecond rules engine** | 95-th percentile evaluation ≈ **5 µs**; full request path (Redis + HTTP) ≈ **1 ms** |
| **Behavioural features** | Sliding-window counters in Redis (failure rate, BIN diversity, burst velocity) |
| **Transparent YAML rules** | Hot-reload, *audit → shadow-block → enforce* workflow; no black-box ML required |
| **Operational guard rails** | Panic flag, Prometheus metrics, `/healthz` readiness, circuit-breaker on Redis loss |
| **Drop-in middleware** | First-class FastAPI, Flask and Express examples; webhook-guard fallback for legacy stacks |

---

## Installation

```bash
# Alpha channel until v1.0
pip install --pre sentr

# Optional extras: Streamlit rule-simulator GUI
pip install --pre sentr[full]
```

---

## Quick Start (proxy-confirm mode)

```bash
# 1. Run Redis (or point to an existing instance)
docker run -d -p 6379:6379 redis:7-alpine

# 2. Create .env
echo "SENTR_REDIS_URL=redis://localhost:6379/0" > .env

# 3. Launch the guard
sentr run --env-file .env
```

### Add middleware to FastAPI

```python
from fastapi import FastAPI, Request
from sentr.integrations.fastapi_guard import SentrGuard

app = FastAPI()
app.add_middleware(SentrGuard)  # MUST be first

@app.post("/confirm")
async def confirm(req: Request):
    verdict = await req.state.sentr_verdict  # populated by middleware
    if verdict.decision == "block":
        return {"blocked": True, "reasons": verdict.reasons}, 402
    # proceed to stripe.PaymentIntent.confirm(...)
```

All rules ship in **audit** mode; no customer traffic is blocked until you promote rules to **shadow** or **enforce**.

---

## Performance Profile<sup>1</sup>

| Path | Median | P95 |
|------|--------|-----|
| Rule evaluation (10 rules) | 2 µs | 4 µs |
| Redis Lua feature lookup (local socket) | 110 µs | 260 µs |
| Full request → verdict (uvicorn + uvloop) | 0.9 ms | 1.4 ms |

<sup>1</sup> Apple M2, Python 3.12, Redis 7.0.

---

## Architecture

```text
┌─────────────── API / Checkout ───────────────┐
│                                               │
│  POST /confirmPaymentIntent                   │
│               │                               │
│               ▼                               │
│      ┌────────────────────┐   Redis (local)   │
│      │     Sentr Guard    │───▲ sliding win.  │
│      │  (FastAPI + rules) │   └───────────────┘
│      └─────────┬──────────┘
│                │ allow / block
│                ▼
│          Stripe API
└───────────────────────────────────────────────┘
```

*No card data leaves your infrastructure; Sentr only needs BIN + last‑4 and a hashed IP address.*

---

## Monitoring Endpoints

| Path | Purpose |
|------|---------|
| `/healthz` | JSON health report (Redis, rules count, revision hash) |
| `/metrics` | Prometheus exposition (`decision_latency_seconds`, `rules_hit_total`, `fees_saved_total`) |

A ready‑to‑use Grafana dashboard JSON lives in `docker/grafana/`.

---

## Rule Definition Example

```yaml
- id: burst_failures
  if: ip.fail_rate_60s > 0.8 and ip.attempts_60s >= 6
  action: block
  score: 0.92
  state: shadow  # audit | shadow | enforce

- id: geo_mismatch
  if: card.bin_country != ip.geo.country and timestamp.hour in 2..5
  action: challenge_3ds
  score: 0.65
  state: audit
```

Reload rules in‑place:

```bash
kill -HUP $(pgrep -f "uvicorn.*sentr")
```

---

## Deployment Notes

* **Colocate Redis** with the guard or connect via Unix socket to minimise RTT.
* Use the provided `docker-compose.yml` or the Helm chart under `deploy/` for Kubernetes.
* For webhook‑only flows, run `apps/webhook_guard` and point the Stripe Dashboard to its public URL.

---

## Development & Contribution

```bash
git clone https://github.com/sentr-dev/sentr-core.git
cd sentr-core
pip install -e .[dev]
pytest -q
pytest-benchmark
```

Pull requests are welcome for rule examples, feature ideas and integration guides.

---

## License

Sentr is released under the [MIT License](LICENSE).

---

> **Sentr – deterministic, open and fast fraud blocking for modern payment stacks.**
