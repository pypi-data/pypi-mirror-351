"""
CRM package for customer relationship management
"""

from .salesforce import Salesforce
from .dynamics365 import Microsoft365Dynamics
from .pipedrive import Pipedrive
__all__ = ['Salesforce','Microsoft365Dynamics','Pipedrive']