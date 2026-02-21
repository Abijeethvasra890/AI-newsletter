import uuid
from loguru import logger

from core.state import NewsletterState

from agents.collector_agent import CollectorAgent
from agents.ranker_agent import RankerAgent
from agents.extractor_agent import ExtractorAgent
from agents.writer_agent import WriterAgent
from services.email_service import EmailService


def run_newsletter_pipeline():

    logger.info("🚀 Starting The Backprop Bulletin pipeline")

    state = NewsletterState(run_id=str(uuid.uuid4()))

    try:
        # 1️⃣ Collect
        state = CollectorAgent().run(state)

        # 2️⃣ Rank
        state = RankerAgent().run(state)

        # 3️⃣ Extract
        state = ExtractorAgent().run(state)

        # 4️⃣ Write
        state = WriterAgent().run(state)

        logger.info("📝 Newsletter generated successfully")

        # 5️⃣ Send Email
        email_service = EmailService()

        email_service.send_email(
            to_email="vasraabijeeth@gmail.com",
            subject="🚀 The Backprop Bulletin — This Week in Indian AI",
            markdown_content=state.final_newsletter
        )

        logger.info("📧 Email sent successfully")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

    logger.info("✅ Newsletter pipeline completed successfully")


if __name__ == "__main__":
    run_newsletter_pipeline()