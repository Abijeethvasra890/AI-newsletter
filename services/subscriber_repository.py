from supabase import create_client
import os
from dotenv import load_dotenv

class SubscriberRepository:

    def __init__(self):
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise RuntimeError("Supabase credentials not configured")

        self.client = create_client(url, key)

    def get_active_subscribers(self):
        response = (
            self.client
            .table("subscribers")
            .select("email, interests")
            .eq("is_active", True)
            .execute()
        )

        return response.data or []

    def add_subscriber(self, email: str, interests=None):
        if interests is None:
            interests = []

        self.client.table("subscribers").insert({
            "email": email,
            "interests": interests
        }).execute()

    def deactivate_subscriber(self, email: str):
        self.client.table("subscribers") \
            .update({"is_active": False}) \
            .eq("email", email) \
            .execute()