import uuid

from core.state import NewsletterState
from agents.collector_agent import CollectorAgent
from agents.ranker_agent import RankerAgent
from agents.extractor_agent import ExtractorAgent
from agents.writer_agent import WriterAgent
from services.email_service import EmailService


if __name__ == "__main__":

    state = NewsletterState(run_id=str(uuid.uuid4()))

    # Run pipeline
    state = CollectorAgent().run(state)
    state = RankerAgent().run(state)
    state = ExtractorAgent().run(state)
    state = WriterAgent().run(state)

    print("Newsletter generated successfully.")

    # Send email
    email_service = EmailService()

    email_service.send_email(
        to_email="vasraabijeeth@gmail.com",
        subject="🚀 The Backprop Bulletin — This Week in Indian AI",
        markdown_content=state.final_newsletter
    )

    print("Email sent successfully.")
