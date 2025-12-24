
import streamlit as st
import os
from core.database import get_db_session
from models import School, Subscription

# --- Stripe Configuration ---
# Make stripe import optional to avoid breaking the app if not installed
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    stripe = None
    STRIPE_AVAILABLE = False

# It's crucial to set these as environment variables in production
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...") # Replace with your test secret key
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "pk_test_...") # Replace with your test public key
if STRIPE_AVAILABLE:
    stripe.api_key = STRIPE_SECRET_KEY

# --- Product IDs from your Stripe Dashboard ---
# These IDs represent the "Pro Plan" and "Enterprise Plan" products in Stripe
PRO_PLAN_PRICE_ID = os.getenv("PRO_PLAN_PRICE_ID", "price_1...") # e.g., price_1Lq...
ENTERPRISE_PLAN_PRICE_ID = os.getenv("ENTERPRISE_PLAN_PRICE_ID", "price_2...")

class StripeManager:
    """
    Handles all interactions with the Stripe payment gateway.
    """
    def __init__(self, school_id: int):
        self.school_id = school_id
        self.db_session = get_db_session()
        self.school = self.db_session.query(School).get(self.school_id)

    def _get_or_create_customer(self):
        """
        Retrieves the Stripe customer ID for the school, or creates a new
        customer in Stripe if one doesn't exist.
        """
        if not STRIPE_AVAILABLE:
            st.warning("Stripe is not available. Payment features are disabled.")
            return None
            
        if self.school.stripe_customer_id:
            return self.school.stripe_customer_id

        # Create a new customer in Stripe
        customer = stripe.Customer.create(
            name=self.school.name,
            metadata={'school_id': self.school.id}
        )
        
        # Save the new customer ID to our database
        self.school.stripe_customer_id = customer.id
        self.db_session.commit()
        
        return customer.id

    def create_checkout_session(self, price_id: str, success_url: str, cancel_url: str) -> str:
        """
        Creates a Stripe Checkout session for a subscription.

        Args:
            price_id (str): The ID of the Stripe Price object.
            success_url (str): The URL to redirect to on successful payment.
            cancel_url (str): The URL to redirect to on canceled payment.

        Returns:
            str: The URL of the Stripe Checkout page.
        """
        customer_id = self._get_or_create_customer()
        
        try:
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{'price': price_id, 'quantity': 1}],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={'school_id': self.school.id}
            )
            return checkout_session.url
        except Exception as e:
            st.error(f"Error creating Stripe checkout session: {e}")
            return None

    def create_portal_session(self, return_url: str) -> str:
        """
        Creates a Stripe Customer Portal session to allow users to manage
        their subscription (e.g., update card, cancel).

        Args:
            return_url (str): The URL to return to after leaving the portal.

        Returns:
            str: The URL of the Stripe Customer Portal.
        """
        customer_id = self.school.stripe_customer_id
        if not customer_id:
            st.error("No customer ID found for this school.")
            return None
            
        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return portal_session.url
        except Exception as e:
            st.error(f"Error creating Stripe portal session: {e}")
            return None

# You would also need a webhook endpoint to listen for Stripe events
# (e.g., subscription.created, subscription.deleted) to update your database.
# This is a more advanced topic requiring a separate web server (e.g., Flask/FastAPI)
# to receive the webhooks from Stripe.
