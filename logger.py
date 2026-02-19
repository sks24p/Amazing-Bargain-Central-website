from models import db, Logs
from flask_login import current_user
from flask import request
import hashlib

def log_event(action_type, details = None, severity = "info"):
    """ Log an event to the database 
    - action_type: Type of action (e.g., login_success, product_created)
    - details: additional information
    - severity: info, warning, or error
    """
    # Get user ID (None if not logged in)
    user_id = current_user.id if current_user.is_authenticated else None
    # Get and anonymise IP address
    ip = request.remote_addr
    anonymised_ip = hashlib.sha256(ip.encode()).hexdigest()[:16] if ip else None
    # Create log entry
    log = Logs(
        user_id = user_id,
        action_type = action_type,
        details = str(details) if details else None,
        ip_address = anonymised_ip,
        severity = severity
    )
    try:
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Logging failed: {e}")