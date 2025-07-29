"""Stripe integration for PromptPack marketplace"""

import os
import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime


class StripeMarketplace:
    """Stripe integration for selling PromptPacks"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or os.getenv("STRIPE_SECRET_KEY")
        if self.secret_key:
            stripe.api_key = self.secret_key
    
    async def create_product(
        self,
        name: str,
        description: str,
        price: int,  # in cents
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a new product for a PromptPack"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            # Create product
            product = stripe.Product.create(
                name=name,
                description=description,
                metadata=metadata or {}
            )
            
            # Create price
            price_obj = stripe.Price.create(
                unit_amount=price,
                currency=currency,
                product=product.id
            )
            
            return {
                "success": True,
                "product_id": product.id,
                "price_id": price_obj.id,
                "price": price / 100,  # Convert back to dollars
                "currency": currency
            }
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    async def create_checkout_session(
        self,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create Stripe checkout session"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            session_data = {
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "mode": "payment",
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
            
            if customer_email:
                session_data["customer_email"] = customer_email
            
            if metadata:
                session_data["metadata"] = metadata
            
            session = stripe.checkout.Session.create(**session_data)
            
            return {
                "success": True,
                "session_id": session.id,
                "checkout_url": session.url
            }
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    async def create_subscription_product(
        self,
        name: str,
        description: str,
        monthly_price: int,  # in cents
        annual_price: Optional[int] = None,
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create subscription product for premium features"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            # Create product
            product = stripe.Product.create(
                name=name,
                description=description,
                metadata=metadata or {}
            )
            
            # Create monthly price
            monthly_price_obj = stripe.Price.create(
                unit_amount=monthly_price,
                currency=currency,
                recurring={"interval": "month"},
                product=product.id
            )
            
            result = {
                "success": True,
                "product_id": product.id,
                "monthly_price_id": monthly_price_obj.id,
                "monthly_price": monthly_price / 100
            }
            
            # Create annual price if provided
            if annual_price:
                annual_price_obj = stripe.Price.create(
                    unit_amount=annual_price,
                    currency=currency,
                    recurring={"interval": "year"},
                    product=product.id
                )
                result["annual_price_id"] = annual_price_obj.id
                result["annual_price"] = annual_price / 100
            
            return result
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    async def create_subscription_checkout(
        self,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        trial_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create subscription checkout session"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            session_data = {
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
            
            if customer_email:
                session_data["customer_email"] = customer_email
            
            if trial_days:
                session_data["subscription_data"] = {
                    "trial_period_days": trial_days
                }
            
            session = stripe.checkout.Session.create(**session_data)
            
            return {
                "success": True,
                "session_id": session.id,
                "checkout_url": session.url
            }
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    async def verify_payment(self, session_id: str) -> Dict[str, Any]:
        """Verify payment completion"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            return {
                "success": True,
                "payment_status": session.payment_status,
                "customer_id": session.customer,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "metadata": session.metadata
            }
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    async def create_customer_portal(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """Create customer portal for subscription management"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            
            return {
                "success": True,
                "portal_url": session.url
            }
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    async def get_customer_subscriptions(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """Get customer's active subscriptions"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status="active"
            )
            
            active_subs = []
            for sub in subscriptions.data:
                active_subs.append({
                    "id": sub.id,
                    "status": sub.status,
                    "current_period_end": sub.current_period_end,
                    "items": [
                        {
                            "price_id": item.price.id,
                            "product_id": item.price.product,
                            "quantity": item.quantity
                        }
                        for item in sub.items.data
                    ]
                })
            
            return {
                "success": True,
                "subscriptions": active_subs
            }
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    async def create_connect_account(
        self,
        email: str,
        country: str = "US",
        account_type: str = "express"
    ) -> Dict[str, Any]:
        """Create Stripe Connect account for sellers"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            account = stripe.Account.create(
                type=account_type,
                country=country,
                email=email,
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                }
            )
            
            return {
                "success": True,
                "account_id": account.id,
                "type": account.type,
                "email": email
            }
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    async def create_account_link(
        self,
        account_id: str,
        refresh_url: str,
        return_url: str
    ) -> Dict[str, Any]:
        """Create account link for onboarding"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type="account_onboarding",
            )
            
            return {
                "success": True,
                "onboarding_url": account_link.url,
                "expires_at": account_link.expires_at
            }
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    async def create_marketplace_payment(
        self,
        amount: int,
        currency: str,
        connected_account_id: str,
        application_fee: int,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create payment with marketplace fees"""
        if not self.secret_key:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                application_fee_amount=application_fee,
                transfer_data={
                    "destination": connected_account_id,
                },
                customer=customer_id
            )
            
            return {
                "success": True,
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}