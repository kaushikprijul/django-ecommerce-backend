# Django E-Commerce Backend

A Django REST Framework-based E-Commerce Backend providing APIs for product management, shopping carts, and order processing.

## ✨ Features

- 🛍️ Product management (CRUD operations)
- 🛒 Shopping cart and cart item management
- 📦 Order creation and management
- 🔐 Token-based authentication
- 🛡️ Role-based permissions (Admin and User)
- 🔎 Product search and price filtering
- 📊 Sorting and pagination
- 💰 Automatic order total calculation
- 📉 Automatic stock management
- ✅ Cart quantity and stock validation

## 🛠️ Technologies Used

- Python
- Django
- Django REST Framework
- SQLite
- Django Filter

## ▶️ How to Run

Install the required packages:

```bash
pip install django djangorestframework django-filter pillow
```

Apply migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```
