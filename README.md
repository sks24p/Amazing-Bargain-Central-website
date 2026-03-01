# ABC E-Commerce Platform

A secure e-commerce web application built with Flask demonstrating comprehensive security controls including authentication, authorisation, input validation, and GDPR-compliant logging.

## Project Description

This platform enables customers to browse and purchase products, sellers to manage inventory and orders, and administrators to oversee users and system operations. The application implements role-based access control (RBAC), secure session management, and defence-in-depth security measures aligned with OWASP Top 10 guidance.

**Key Features:**
- User authentication with bcrypt password hashing
- Three-tier role system (Customer, Seller, Admin)
- Product catalogue with search functionality
- Shopping cart and checkout system
- Product reviews with markdown formatting and image uploads
- Seller dashboards for inventory and order management
- Admin controls for user and system management
- Comprehensive security logging with IP anonymisation

## Technologies Used

- **Backend:** Python 3.9+, Flask 3.0
- **Database:** SQLite with SQLAlchemy ORM
- **Security:** Flask-WTF (CSRF), Flask-Login, Flask-Bcrypt, Flask-Talisman
- **File Upload:** python-magic, Werkzeug
- **Styling:** SASS/CSS
- **Other:** python-dotenv, Bleach, Markdown

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository:**
```bash
   git clone https://github.coventry.ac.uk/ahmedkhans/amazing-bargain-central.git
   cd abc-ecommerce
```

2. **Create virtual environment:**
```bash
   python -m venv venv
```

3. **Activate virtual environment:**
   
   **Windows:**
```bash
   venv\Scripts\activate
```
   
   **macOS/Linux:**
```bash
   source venv/bin/activate
```

4. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

5. **Create environment file:**
   
   Create a `.env` file in the project root with the following variables:
```
   SECRET_KEY=your-secret-key-here
   FLASK_DEBUG=True
   FLASK_ENV=development
```
   
   **Generate a secure SECRET_KEY:**
```python
   python -c "import secrets; print(secrets.token_hex(32))"
```

6. **Initialise database:**
```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
```

7. **Create admin account (optional):**
```bash
   python create_admin.py
```
   Follow the prompts to convert an existing user account to admin role.

## Dependencies

Full list available in `requirements.txt`. Key dependencies:

- **Flask** (3.0+): Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: Session management
- **Flask-Bcrypt**: Password hashing
- **Flask-WTF**: CSRF protection
- **Flask-Talisman**: HTTPS enforcement and security headers
- **python-magic**: File type validation (magic bytes)
- **Bleach**: HTML sanitisation
- **Markdown**: Safe text formatting for reviews
- **python-dotenv**: Environment variable management

## Environment Variables

Create a `.env` file in the project root:
```bash
# Required
SECRET_KEY=<generate-with-secrets.token_hex(32)>

# Development
FLASK_DEBUG=True
FLASK_ENV=development

# Production (set these for production deployment)
FLASK_DEBUG=False
FLASK_ENV=production
```

**Security Note:** Never commit `.env` to version control. The `.gitignore` file excludes it by default.

## Running the Application

1. **Ensure virtual environment is activated:**
```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
```

2. **Start the development server:**
```bash
   python app.py
```

3. **Access the application:**
   
   Open your browser and navigate to:
```
   http://127.0.0.1:5000
```

4. **Register an account:**
   - Navigate to Register page
   - Create customer account
   - Upgrade to seller via Account page (optional)

## Project Structure
```
abc-ecommerce/
├── app.py                 # Application entry point
├── config.py              # Configuration settings
├── models.py              # Database models
├── security.py            # Security utilities (file validation, sanitisation)
├── logger.py              # Logging system
├── create_admin.py        # Admin account creation script
├── routes/
│   ├── auth.py           # Authentication routes
│   ├── seller.py         # Seller routes
│   ├── admin.py          # Admin routes
│   └── products.py       # Product and cart routes
├── templates/            # Jinja2 HTML templates
├── static/
│   ├── css/             # Compiled CSS
│   ├── sass/            # SASS source files
│   └── uploads/         # User-uploaded images
├── requirements.txt      # Python dependencies
└── .env                 # Environment variables (create this)
```

## Security Features Summary

### Authentication & Authorisation
- **Password Hashing:** bcrypt with work factor 12
- **Session Management:** Flask-Login with encrypted cookies (HttpOnly, SameSite=Lax)
- **RBAC:** Three-tier role system with `before_request` validation
- **IDOR Protection:** Ownership verification on all user-specific resources

### Input Validation
- **SQL Injection Prevention:** SQLAlchemy ORM with parameterised queries
- **XSS Prevention:** Jinja2 autoescaping + Bleach sanitisation for user content
- **CSRF Protection:** Flask-WTF tokens on all state-changing requests
- **File Upload Security:**
  - Extension whitelist (PNG, JPEG, GIF, WebP)
  - Magic bytes validation via python-magic
  - 5MB size limit
  - Filename sanitisation (Werkzeug secure_filename)
  - UUID generation preventing overwrites

### Data Protection
- **Encryption in Transit:** HTTPS enforcement via Flask-Talisman (production)
- **Password Storage:** One-way bcrypt hashing (plaintext never stored)
- **Session Security:** Encrypted cookies, 30-minute timeout
- **GDPR Compliance:**
  - IP address anonymisation (SHA-256 hashing)
  - 90-day log retention with automated cleanup
  - Data minimisation (only essential information collected)

### Security Headers
- Content-Security-Policy (CSP)
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- Strict-Transport-Security (HSTS)

### Logging & Monitoring
- Security event logging (authentication, authorisation failures)
- Business analytics (product views, purchases)
- Admin-only log access with strict RBAC
- Sensitive data exclusion (no passwords, payment info, full IPs)

## Testing

### Run Security Scans

**Static Analysis (Bandit):**
```bash
bandit -r . --exclude ./venv -ll
```

**Dynamic Analysis (OWASP ZAP):**
1. Start the application
2. Open OWASP ZAP
3. Automated Scan → http://127.0.0.1:5000
4. Review results

## Known Limitations (Development Environment)

- Database encryption at rest not implemented (SQLite unencrypted)
- Rate limiting not configured (vulnerable to brute-force)
- Two-factor authentication not implemented
- Server version disclosure in development server (resolved in production via WSGI)
- SESSION_COOKIE_SECURE=False for localhost (must be True in production HTTPS)

## Production Deployment Notes

**Not suitable for production use without:**
- WSGI server deployment (Gunicorn/uWSGI)
- Reverse proxy (Nginx/Apache)
- Database encryption (SQLCipher)
- HTTPS with valid SSL certificates
- Rate limiting (Flask-Limiter)
- Environment variable: `FLASK_DEBUG=False`
- Environment variable: `SESSION_COOKIE_SECURE=True`

## Licence

This project was developed for academic purposes as part of the 6000CMD Security module at Coventry University.

---

**Last Updated:** February 2026