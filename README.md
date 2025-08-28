# El Senior Dumingag - Tailoring Management System

El Senior Dumingag is a comprehensive web-based tailoring management system designed to streamline the process of order management, tailor assignments, garment inventory tracking, commission-based payouts, and customer notifications. Based in Dumingag, Zamboanga del Sur, Philippines, it combines traditional Subanen craftsmanship with modern organic farming practices.

## Features

- **Role-based access control** (Admin, Tailor, Customer)
- **Task management workflow** from measurement to delivery
- **Real-time inventory tracking** with low-stock alerts
- **Commission calculation** and payout processing
- **Customer notification system**
- **Responsive web interface**

## Technology Stack

- **Backend**: Django (Python) with SQLite database
- **Frontend**: Tailwind CSS CDN and Django templates, Alpine.js for animations CDN, HTMX for AJAX CDN
- **Authentication**: Django built-in authentication system with Token Authentication
- **Database**: SQLite (development)
- **API**: Django REST Framework

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd stitchflow
   ```

2. Create a virtual environment using uv:
   ```bash
   pip install uv
   uv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

1. Access the admin panel at `http://127.0.0.1:8000/admin/`
2. Register users and assign roles (Admin, Tailor, Customer)
3. Manage inventory, orders, and commissions through the admin interface
4. Access the API endpoints as needed for integration

## API Endpoints

### Authentication
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `POST /api/register/` - User registration

### Admin Endpoints
- `GET/POST /api/admin/customers/` - List/create customers
- `GET/PUT/DELETE /api/admin/customers/<id>/` - Customer details
- `GET/POST /api/admin/tailors/` - List/create tailors
- `GET/PUT/DELETE /api/admin/tailors/<id>/` - Tailor details
- `GET/POST /api/admin/fabrics/` - List/create fabrics
- `GET/PUT/DELETE /api/admin/fabrics/<id>/` - Fabric details
- `GET/POST /api/admin/accessories/` - List/create accessories
- `GET/PUT/DELETE /api/admin/accessories/<id>/` - Accessory details
- `GET/POST /api/admin/orders/` - List/create orders
- `GET/PUT/DELETE /api/admin/orders/<id>/` - Order details
- `GET/POST /api/admin/tasks/` - List/create tasks
- `GET/PUT/DELETE /api/admin/tasks/<id>/` - Task details
- `GET /api/admin/commissions/` - List commissions
- `POST /api/admin/commissions/<id>/pay/` - Mark commission as paid

### Tailor Endpoints
- `GET /api/tailor/tasks/` - List assigned tasks
- `GET/PUT /api/tailor/tasks/<id>/` - Task details and status update
- `GET /api/tailor/commissions/` - View commissions

### Customer Endpoints
- `GET /api/customer/orders/` - View own orders
- `GET /api/customer/orders/<id>/` - Order details

## Project Structure

```
stitchflow/
├── etailoring/           # Main Django app
│   ├── models.py         # Data models
│   ├── views.py          # API views
│   ├── serializers.py    # API serializers
│   ├── admin.py          # Admin interface configuration
│   ├── urls.py           # URL routing
│   ├── apps.py           # App configuration
│   ├── business_logic.py # Business logic implementation
│   ├── tests.py          # Unit tests
│   └── migrations/       # Database migrations
├── stitchflow/           # Project settings
│   ├── settings.py       # Configuration
│   └── urls.py           # Main URL routing
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # Media files (uploads)
├── manage.py             # Django management script
└── requirements.txt      # Project dependencies
```

## Development

### Adding New Features

1. Create new models in `etailoring/models.py`
2. Create serializers in `etailoring/serializers.py`
3. Implement API views in `etailoring/views.py`
4. Register models in `etailoring/admin.py` for admin interface
5. Add URL patterns in `etailoring/urls.py`
6. Create/Update unit tests in `etailoring/tests.py`

### Running Tests

```bash
python manage.py test
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.