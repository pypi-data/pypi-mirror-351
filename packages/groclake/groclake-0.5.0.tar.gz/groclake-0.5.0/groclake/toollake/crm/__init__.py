"""
CRM package for customer relationship management
"""

from .salesforce import Salesforce
from .dynamics365 import Microsoft365Dynamics

__all__ = ['Salesforce','Microsoft365Dynamics']