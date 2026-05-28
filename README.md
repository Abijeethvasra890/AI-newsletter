# The Vasra's AI Digest

An autonomous AI agent pipeline that collects, ranks, extracts, and writes a daily AI newsletter — then delivers it to subscribers every morning via email.

Built by [Abijeeth Vasra](https://github.com/abijeeth-vasra). Runs entirely on GitHub Actions, no server required.

---

## How it works

```
RSS Feeds + Web Sources
        ↓
  Collector Agent        — fetches last 24hrs of AI news across 30+ global feeds
        ↓
   Ranker Agent          — scores articles 1–10 for builder relevance (via LLM)
        ↓
  Extractor Agent        — generates summaries, impact notes, key points (via LLM)
        ↓
   Writer Agent          — composes the newsletter in Agent Vasra's voice (via LLM)
        ↓
  Email Service          — sends personalized HTML emails to all active subscribers
        ↓
  Supabase               — subscriber list with active/inactive management
```

Each agent is independent, retries on failure, and logs structured output via `loguru`.

---

## Stack

| Layer | Technology |
|---|---|
| Orchestration | GitHub Actions (cron, daily 12:00 UTC) |
| LLM | Groq — `llama-3.3-70b-versatile` |
| Agent framework | Custom pipeline with Pydantic state |
| Subscriber store | Supabase (Postgres) |
| Email delivery | Gmail SMTP |
| Feeds | feedparser + 30+ global RSS sources |
| Retries | tenacity |
| Logging | loguru |

---

## Project structure

```
.
├── agents/
│   ├── collector_agent.py     # Fetches and filters last 24h of articles
│   ├── ranker_agent.py        # Scores articles for global builder relevance
│   ├── extractor_agent.py     # Extracts summaries and key points via LLM
│   └── writer_agent.py        # Writes the newsletter in Agent Vasra's voice
│
├── core/
│   ├── state.py               # Pydantic NewsletterState and Article models
│   └── constants.py           # RSS feed list, limits, timeouts
│
├── services/
│   ├── llm_router.py          # Provider abstraction (Groq / Gemini fallback)
│   ├── rss_service.py         # Feed fetching, deduplication, 24h filtering
│   ├── email_service.py       # HTML email composition and SMTP delivery
│   └── subscriber_repository.py  # Supabase subscriber CRUD
│
├── schemas/
│   ├── extraction_schema.py   # Pydantic schema for extractor LLM output
│   └── ranking_schema.py      # Pydantic schema for ranker LLM output
│
├── .github/
│   └── workflows/
│       └── newsletter.yml     # GitHub Actions daily trigger
│
├── main.py                    # Pipeline entry point
└── requirements.txt
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Abijeethvasra890/AI-newsletter.git
cd AI-newsletter
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root:

```env
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-gmail-app-password
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key        # optional fallback
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

> For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your account password. 2FA must be enabled on your Google account.

### 4. Set up Supabase

Create a `subscribers` table in your Supabase project:

```sql
create table subscribers (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  interests text[] default '{}',
  is_active boolean default true,
  created_at timestamptz default now()
);
```

Add your first subscriber:

```sql
insert into subscribers (email) values ('you@example.com');
```

### 5. Add GitHub Actions secrets

In your repo → Settings → Secrets and variables → Actions, add:

```
SENDER_EMAIL
SENDER_PASSWORD
GROQ_API_KEY
GEMINI_API_KEY
SUPABASE_URL
SUPABASE_KEY
```

### 6. Run locally

```bash
python main.py
```

---

## Scheduling

The pipeline runs automatically via GitHub Actions at **12:00 UTC daily** (5:30 AM IST). You can also trigger it manually from the Actions tab using `workflow_dispatch`.

To change the schedule, edit `.github/workflows/newsletter.yml`:

```yaml
on:
  schedule:
    - cron: "0 12 * * *"   # 12:00 UTC = 5:30 AM IST
  workflow_dispatch:
```

---

## Subscriber management

Subscribers are managed in Supabase. The pipeline reads all rows where `is_active = true`.

```sql
-- Add a subscriber
insert into subscribers (email) values ('reader@example.com');

-- Deactivate a subscriber
update subscribers set is_active = false where email = 'reader@example.com';
```

You can also use the `SubscriberRepository` class directly:

```python
from services.subscriber_repository import SubscriberRepository

repo = SubscriberRepository()
repo.add_subscriber("reader@example.com", interests=["llm", "startups"])
repo.deactivate_subscriber("reader@example.com")
```

---

## Adding or removing RSS feeds

Edit `core/constants.py`:

```python
AI_RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    # add your feeds here
]
```

The collector automatically filters for articles published in the last 24 hours, deduplicates by title and URL, and applies a keyword relevance filter before ranking.

---

## The Agent Vasra voice

The newsletter is written by **Agent Vasra** — an editorial persona with a specific set of constraints:

- Filters signal from noise, no hype
- Speaks to builders and practitioners, not executives
- Dry wit, never cringe
- Never uses "game-changing", "revolutionary", or "unprecedented"
- Ends every edition with a clean, memorable sign-off

The writer prompt lives in `agents/writer_agent.py` and is the highest-leverage place to tune output quality.

---

## License

MIT
