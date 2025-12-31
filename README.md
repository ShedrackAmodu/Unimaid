# 📚 University of Maiduguri Library Management System

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, modern library management system built with Django for the University of Maiduguri. Features advanced cataloging, user management, analytics, and a beautiful responsive interface.

![Library Management System](https://img.shields.io/badge/Status-Active-success?style=for-the-badge&logo=github)

## ✨ Features

### 📖 Advanced Catalog Management
- **Complete Book Cataloging**: ISBN, authors, publishers, genres, descriptions
- **Physical & Digital Copies**: Track multiple copies with QR codes
- **Smart Search**: Full-text search with analytics and performance tracking
- **Popular Books Tracking**: Automated popularity scoring and trending analysis
- **Cover Images & Samples**: Visual book representations

### 👥 User Management
- **Multi-tier Membership**: Students, faculty, public members, special access
- **Patron Profiles**: Complete user information with QR code identification
- **Staff Directory**: Library personnel management with social links
- **Role-based Access**: Different permissions for different user types

### 🔄 Circulation System
- **Loan Management**: Automated due dates, extensions, and tracking
- **Reservation System**: Hold books with automatic notifications
- **Fine Calculation**: Automated overdue fines with payment tracking
- **Return Processing**: Streamlined book returns with condition notes

### 📊 Analytics & Reporting
- **System Metrics**: Daily automated metrics generation
- **User Analytics**: Search patterns, popular content, engagement tracking
- **Performance Monitoring**: Search performance and system usage statistics
- **Visual Dashboards**: Admin interface with comprehensive reporting

### 🔔 Communication System
- **Email Notifications**: Automated reminders, due notices, and updates
- **SMS Integration**: Text message notifications for urgent alerts
- **Notification Templates**: Customizable message templates
- **Asynchronous Processing**: Celery-based background email sending

### 🌐 Web Features
- **Responsive Design**: Mobile-first Bootstrap 4 interface
- **Blog System**: News, announcements, and library updates
- **Event Calendar**: Library events and program listings
- **Document Repository**: File sharing and document management
- **Contact Forms**: User inquiry and feedback system

### 🔧 Technical Features
- **REST API**: Full Django REST Framework integration
- **Admin Theming**: Customizable admin interface
- **Asset Optimization**: Django Compressor for CSS/JS minification
- **Background Tasks**: Celery + Redis for async operations
- **Import/Export**: Bulk data operations with django-import-export

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Redis (for Celery)
- PostgreSQL/MySQL (recommended) or SQLite (development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShedrackAmodu/Unimaid.git
   cd library
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env  # Configure your environment variables
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Load sample data** (optional)
   ```bash
   python manage.py loaddata sample_data.json
   ```

7. **Start Redis server**
   ```bash
   redis-server
   ```

8. **Start Celery worker**
   ```bash
   celery -A library worker -l info
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Main site: http://localhost:8000
    - Admin panel: http://localhost:8000/admin

## 📋 Usage

### For Patrons
- **Browse Catalog**: Search and browse books by title, author, or genre
- **Place Reservations**: Reserve books that are currently checked out
- **View Account**: Check loan history, current loans, and fines
- **Access Repository**: Download documents and resources

### For Staff
- **Manage Circulation**: Process checkouts, returns, and reservations
- **User Management**: Register patrons and manage memberships
- **Catalog Maintenance**: Add new books and update existing records
- **Generate Reports**: View analytics and system metrics

### For Administrators
- **System Configuration**: Configure library settings and policies
- **User Management**: Manage staff accounts and permissions
- **Content Management**: Update blog posts, events, and pages
- **Analytics Dashboard**: Monitor system performance and usage

## 🏗️ Project Structure

```
library/
├── catalog/          # Book catalog and circulation management
├── core/            # Main pages, events, and contact forms
├── blog/            # News and announcements
├── staff/           # Staff directory
├── repository/      # Document management
├── static/          # CSS, JS, images
├── templates/       # HTML templates
├── media/           # User uploaded files
└── library/         # Django project settings
```

## 🔧 Configuration

### Key Settings

**Library Policies** (`settings.py`):
```python
LIBRARY_SETTINGS = {
    "DEFAULT_LOAN_DAYS": 14,
    "MAX_BOOKS_PER_PATRON": 5,
    "OVERDUE_FINE_PER_DAY": 0.50,
    "RESERVATION_EXPIRY_DAYS": 7,
    "MAX_RESERVATIONS_PER_PATRON": 3,
}
```

**Email Configuration**:
- Supports Gmail, SMTP, and other providers
- Asynchronous sending with Celery
- HTML and plain text templates

**API Configuration**:
- REST Framework with filtering and pagination
- Token authentication
- CORS support for frontend integration

## 📊 API Endpoints

The system provides a comprehensive REST API:

- `GET /api/books/` - List books with filtering
- `POST /api/loans/` - Create new loans
- `GET /api/patrons/{id}/` - Patron details
- `GET /api/analytics/` - System analytics

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test catalog

# Generate coverage report
coverage run manage.py test
coverage report
```

## 📦 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure production database
- [ ] Set up email backend
- [ ] Configure static files serving
- [ ] Set up SSL certificate
- [ ] Configure Redis for production
- [ ] Set up monitoring and logging

### Docker Support
```dockerfile
# Basic Dockerfile included
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- University of Maiduguri for the vision and support
- Django community for the excellent framework
- Open source contributors

## 📞 Support

For support and questions:
- Email: library@unimaid.edu.ng
- Issues: [GitHub Issues](https://github.com/ShedrackAmodu/Unimaid/issues)
- Documentation: [Wiki](https://github.com/ShedrackAmodu/Unimaid/wiki)

---

<div align="center">
  <p><strong>University of Maiduguri Library Management System</strong></p>
  <p>Built with ❤️ for the academic community</p>
</div>
