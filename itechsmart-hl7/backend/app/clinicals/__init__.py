"""
iTechSmart Clinicals Module
AI-powered clinical workflows and decision support
"""

from .workflow_engine import ClinicalWorkflowEngine
from .ai_insights import ClinicalAIInsights
from .drug_checker import DrugInteractionChecker
from .decision_support import ClinicalDecisionSupport
from .care_coordination import CareCoordinator

__all__ = [
    "ClinicalWorkflowEngine",
    "ClinicalAIInsights",
    "DrugInteractionChecker",
    "ClinicalDecisionSupport",
    "CareCoordinator",
]
