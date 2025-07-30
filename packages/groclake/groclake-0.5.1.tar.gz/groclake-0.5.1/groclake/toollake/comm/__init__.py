"""
Communication tools module
"""

from .gupshup import Gupshup
from .mailchimp import Mailchimp
from .slack import Slack
from .gmail import Gmail
from .twilio import Twilio
from .outlook import Outlook
__all__ = ['Gupshup','Slack','Gmail','Mailchimp','Twilio','Outlook']

