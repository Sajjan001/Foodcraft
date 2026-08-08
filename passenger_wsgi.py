"""
Entry point for Hostinger (Passenger/LiteSpeed) Python App hosting.
Hostinger's hPanel Python App manager looks for an `application` object
in this file at the project root.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

application = create_app()
