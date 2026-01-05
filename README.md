# Ramat Library Management System

A comprehensive Django-based library management system for Ramat Library, University of Maiduguri. This system provides advanced cataloging, user management, circulation, analytics, and a responsive public interface.

## Features

### Core Features

- **Advanced Catalog Management**: ISBN tracking, authors, publishers, genres, multiple copies management, QR code support, cover images, and full-text search
- **User Management**: Multi-tier membership (students, faculty, public), patron profiles with QR IDs, staff directory, and role-based access control
- **Circulation System**: Loan management with due dates, renewals, reservations, automated notifications, overdue fines processing, and streamlined returns
- **Analytics & Reporting**: Automated metrics generation, user analytics dashboards, system performance monitoring, and exportable reports
- **Communication Features**: Email templates and automated notices, optional SMS integration, newsletter system
- **Content Management**: Blog/news system with rich text, event calendar, document repository for file sharing
- **Institutional Repository**: Upload/submission system for theses, dissertations, papers, metadata management (Dublin Core), access control and embargo features
- **REST API**: Django REST Framework API with token-based authentication

## Technology Stack

- **Backend**: Django 5.2.6
- **Database**: SQLite (development) / PostgreSQL (production)
- **API**: Django REST Framework
- **Frontend**: Bootstrap 5, jQuery, Animate.css
- **Authentication**: Django Authentication + Token Authentication
- **Background Tasks**: Celery + Redis (optional)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd UNI_made_library
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin user (default: admin/admin123)

6. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - API: http://localhost:8000/api/

## Project Structure

```
unimaid_library/
├── manage.py
├── requirements.txt
├── README.md
├── unimaid_library/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/          # User management
├── catalog/           # Books/resources
├── circulation/       # Loans, reservations
├── repository/        # Institutional repository
├── blog/              # News/blog
├── events/             # Event calendar
├── analytics/         # Reporting system
├── api/               # REST API
├── static/            # CSS, JS, images
├── media/             # User uploads
└── templates/         # HTML templates
```

## Default Admin Credentials

- **Username**: admin
- **Password**: admin123

**⚠️ Important**: Change the default password immediately in production!

## Usage

### For Patrons

1. **Register/Login**: Create an account or login to access personalized features
2. **Browse Catalog**: Search and browse available books
3. **Reserve Books**: Reserve books that are currently on loan
4. **View Loans**: Check your current loans, due dates, and renew books
5. **Pay Fines**: View and pay outstanding fines
6. **Access Repository**: Browse and download institutional repository documents
7. **Register for Events**: Sign up for library events and workshops

### For Staff

1. **Admin Panel**: Access the Django admin panel at `/admin/`
2. **Manage Catalog**: Add, edit, and manage books and copies
3. **Process Circulation**: Handle checkouts, returns, and reservations
4. **Manage Users**: View and manage patron accounts
5. **Generate Reports**: Access analytics and generate reports
6. **Moderate Content**: Approve blog posts, repository documents, and event registrations

### For Administrators

1. **Full System Access**: Complete control over all system features
2. **User Management**: Create and manage user accounts and permissions
3. **System Configuration**: Configure system settings and preferences
4. **Analytics Dashboard**: View comprehensive system analytics
5. **Data Export**: Export data and generate custom reports

## API Usage

The system includes a REST API for programmatic access:

### Authentication

```python
# Get token
POST /api/auth/login/
{
    "username": "your_username",
    "password": "your_password"
}

# Use token in headers
Authorization: Token your_token_here
```

### Example Endpoints

- `GET /api/books/` - List all books
- `GET /api/books/{id}/` - Get book details
- `GET /api/loans/` - List loans (authenticated)
- `GET /api/documents/` - List repository documents
- `GET /api/events/` - List events

See `/api/` for full API documentation when running the server.

## Configuration

### Email Settings

Update email configuration in `settings.py` for production:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### Database Configuration

For production, use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unimaid_library',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Sample Data

```bash
python manage.py create_sample_data
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Set `ALLOWED_HOSTS` with your domain
- [ ] Use PostgreSQL database
- [ ] Configure static file serving (Nginx/Apache)
- [ ] Set up SSL/HTTPS
- [ ] Configure email backend
- [ ] Set up Celery and Redis for background tasks
- [ ] Configure media file storage (S3 or local)
- [ ] Set up backup procedures
- [ ] Configure logging
- [ ] Change default admin password

### Recommended Stack

- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Database**: PostgreSQL
- **Background Tasks**: Celery + Redis
- **Static Files**: Nginx or CDN (AWS S3, CloudFront)

## Support

For support, contact:
- **Email**: ramatlibrary@unimaid.edu.ng
- **Phone**: +234 80166 253 232

## License

This project is developed for Ramat Library, University of Maiduguri.

## Acknowledgments

- University of Maiduguri
- Django community
- Bootstrap team
- All open-source contributors

---

**Version**: 1.0.0  
**Last Updated**: January 2026

