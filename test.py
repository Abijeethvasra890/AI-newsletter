import uuid
from core.state import NewsletterState
from agents.collector_agent import CollectorAgent

state = NewsletterState(run_id=str(uuid.uuid4()))

collector = CollectorAgent()
state = collector.run(state)

print("Collected:", len(state.raw_articles))
