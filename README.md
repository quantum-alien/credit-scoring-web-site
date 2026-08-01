# Credit Scoring System

A web-based Credit Scoring System built with **Python** and **Django** that automates the evaluation of loan applicants by analyzing financial and personal information. The application helps financial institutions make faster, more consistent, and data-driven lending decisions through configurable scoring models and risk assessment.

## Overview

The Credit Scoring System is designed to simplify the credit evaluation process by replacing manual assessments with an automated scoring engine. Users can manage customer profiles, submit loan applications, calculate credit scores, classify risk levels, and review detailed assessment reports from a centralized web interface.

## Features

- Customer registration and profile management
- Loan application management
- Automated credit score calculation
- Configurable scoring criteria
- Credit risk classification
- Credit history and application tracking
- Dashboard with key statistics
- Search and filter applicants
- User authentication and authorization
- Admin panel for system management
- RESTful API support (optional)
- Responsive web interface

## Technology Stack

### Backend
- Python 3.x
- Django
- Django REST Framework

### Database
- PostgreSQL (recommended)
- SQLite (development)

### Frontend
- Django Templates
- HTML5
- CSS3
- Bootstrap
- JavaScript

### Authentication
- Django Authentication System

## Project Structure

```
credit-scoring/
│
├── app.py                # Main application
├── scoring.db              
├── credit_scoring_system.py            # Credit scoring logic
└── scoring_system.log
```

## Installation

### Clone the repository

```bash
git clone https://github.com/quantum-alien/credit-scoring-web-site.git

cd credit-scoring-web-site
```

### Create a virtual environment

```bash
python -m venv venv
```

Activate the environment.

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file and configure your settings.

Example:

```env
SECRET_KEY=your_secret_key
DEBUG=True

DATABASE_NAME=credit_scoring
DATABASE_USER=postgres
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### Apply migrations

```bash
python manage.py migrate
```

### Create an administrator

```bash
python manage.py createsuperuser
```

### Run the development server

```bash
python manage.py runserver
```

Visit:

```
http://127.0.0.1:8000/
```

## Workflow

1. Register or log in.
2. Create a customer profile.
3. Submit a credit or loan application.
4. The system evaluates the applicant using predefined scoring rules.
5. A credit score and risk category are generated.
6. Administrators review results and make lending decisions.

## Future Improvements

- Machine Learning–based credit prediction
- Integration with external credit bureaus
- Financial statement analysis
- Document verification
- Email and SMS notifications
- Audit logging
- Multi-factor authentication
- Docker deployment
- CI/CD pipeline
- Credit score visualization and analytics

## Security

- Secure password hashing
- CSRF protection
- SQL injection protection through Django ORM
- Role-based access control
- Secure authentication
- Input validation

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.
