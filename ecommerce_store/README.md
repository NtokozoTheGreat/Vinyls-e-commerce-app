# Vinyls e-commerce app

A full-stack multi-vendor e-commerce application built with Django, enabling vendors to create and manage online vinyl record stores while allowing customers to browse products, place orders, track purchases, exchange messages with vendors, and receive automated email notifications.

### live url link:
https://vinyls-e-commerce-app-production.up.railway.app/

Test credentials if you'd like to explore without registering:
- ** Buyer account:
- ** Vendor account: 

---

## Screenshots

---

## Features

- Secure user authentication (register, login, and logout).
- Vendors can create, customize and manage their own independent stores.
- Full product management (create, edit, and delete listings).
- Browse, search, and purchase vinyl records from multiple vendors.
- In-app messaging between buyers and vendors (general and product-specific conversations).
- Order tracking dashboard for buyers.
- Product and store rating system.
- Automated email notifications for important account and order updates.
- Responsive design for desktop.
---

##  Tech Stack

### Backend
- Python
- Django

### Database
- PostgreSQL

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Deployment
- Railway
- Gunicorn

### Version Control
- Git
- GitHub

---

### Prerequisites
- Python 3.x
- PostgreSQL
- Git

## To Run the application locally

### Installation

# Clone the repository

```bash
git clone https://github.com/NtokozoTheGreat/Vinyls-e-commerce-app
```

# Navigate into the project
```bash
cd ecommerce_store
```

# Create and activate a virtual environment

#### for MacOS
```bash
python -m venv venv
source venv/bin/activate
```

#### for Windows
```bash
python -m venv venv
env\Scripts\activate
```

# Install dependencies (requires Python 3.x and PostgreSQL)
```bash
pip install -r requirements.txt
```

# Create a .env file in the root directory and add:
SECRET_KEY=your_secret_key
DATABASE_URL=your_postgresql_database_url
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password

# Apply migrations
```bash
python manage.py migrate
```

# Create a superuser (optional but recommended)
```bash
python manage.py createsuperuser
```

# Run the development server
```bash
python manage.py runserver
```

---

## Project Structure

----

## upcoming features
- Twitter API integration (auto-tweet when new stores/products are added)
- REST API for mobile clients
- Advanced search filters
- Payment gateway integration (PayPal)

## Author 

Lihle
GitHub : https://github.com/NtokozoTheGreat
LinkedIn : www.linkedin.com/in/lihle-ntokozo-557484314