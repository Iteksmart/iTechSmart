"""
iTechSmart Customer Success - Customer Success Management Engine
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4


class HealthScore(str, Enum):
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"  # 60-79
    AT_RISK = "at_risk"  # 40-59
    CRITICAL = "critical"  # 0-39


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Customer:
    def __init__(self, customer_id: str, name: str, email: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.health_score = 100
        self.last_login = datetime.utcnow()
        self.created_at = datetime.utcnow()
        self.tickets = []
        self.interactions = []


class Ticket:
    def __init__(self, ticket_id: str, customer_id: str, subject: str, priority: TicketPriority):
        self.ticket_id = ticket_id
        self.customer_id = customer_id
        self.subject = subject
        self.priority = priority
        self.status = "open"
        self.created_at = datetime.utcnow()
        self.resolved_at = None


class CustomerSuccessEngine:
    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.tickets: Dict[str, Ticket] = {}
        self.playbooks: Dict[str, Dict[str, Any]] = {}
    
    def add_customer(self, name: str, email: str) -> str:
        customer_id = str(uuid4())
        customer = Customer(customer_id, name, email)
        self.customers[customer_id] = customer
        return customer_id
    
    def calculate_health_score(self, customer_id: str) -> int:
        customer = self.customers.get(customer_id)
        if not customer:
            return 0
        
        score = 100
        
        # Reduce score based on inactivity
        days_inactive = (datetime.utcnow() - customer.last_login).days
        if days_inactive > 30:
            score -= 30
        elif days_inactive > 14:
            score -= 15
        
        # Reduce score based on open tickets
        open_tickets = len([t for t in customer.tickets if t == "open"])
        score -= (open_tickets * 5)
        
        customer.health_score = max(0, min(100, score))
        return customer.health_score
    
    def get_health_status(self, customer_id: str) -> HealthScore:
        score = self.calculate_health_score(customer_id)
        
        if score >= 80:
            return HealthScore.EXCELLENT
        elif score >= 60:
            return HealthScore.GOOD
        elif score >= 40:
            return HealthScore.AT_RISK
        else:
            return HealthScore.CRITICAL
    
    def create_ticket(self, customer_id: str, subject: str, priority: TicketPriority) -> str:
        ticket_id = str(uuid4())
        ticket = Ticket(ticket_id, customer_id, subject, priority)
        self.tickets[ticket_id] = ticket
        
        customer = self.customers.get(customer_id)
        if customer:
            customer.tickets.append("open")
        
        return ticket_id
    
    def resolve_ticket(self, ticket_id: str) -> bool:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        
        ticket.status = "resolved"
        ticket.resolved_at = datetime.utcnow()
        return True
    
    def get_at_risk_customers(self) -> List[Dict[str, Any]]:
        at_risk = []
        for customer in self.customers.values():
            health = self.get_health_status(customer.customer_id)
            if health in [HealthScore.AT_RISK, HealthScore.CRITICAL]:
                at_risk.append({
                    "customer_id": customer.customer_id,
                    "name": customer.name,
                    "health_score": customer.health_score,
                    "health_status": health.value
                })
        return at_risk
    
    def predict_churn(self, customer_id: str) -> Dict[str, Any]:
        customer = self.customers.get(customer_id)
        if not customer:
            return {"churn_risk": 0, "factors": []}
        
        risk_factors = []
        churn_risk = 0
        
        # Check inactivity
        days_inactive = (datetime.utcnow() - customer.last_login).days
        if days_inactive > 30:
            churn_risk += 40
            risk_factors.append("Inactive for 30+ days")
        
        # Check health score
        if customer.health_score < 50:
            churn_risk += 30
            risk_factors.append("Low health score")
        
        # Check open tickets
        open_tickets = len([t for t in customer.tickets if t == "open"])
        if open_tickets > 2:
            churn_risk += 20
            risk_factors.append("Multiple open tickets")
        
        return {
            "customer_id": customer_id,
            "churn_risk": min(100, churn_risk),
            "risk_factors": risk_factors,
            "recommendation": "Immediate outreach required" if churn_risk > 60 else "Monitor closely"
        }


customer_success_engine = CustomerSuccessEngine()