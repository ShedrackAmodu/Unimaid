# 📚 University of Maiduguri Library Management System


A comprehensive, modern library management system built with Django for the University of Maiduguri. Features advanced cataloging, user management, analytics, and a beautiful responsive interface.



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
SQLite (development)

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


5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
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



## 🔧 Configuration


**Email Configuration**:
- Supports Gmail, SMTP, and other providers
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
`

## 📦 Deployment


## 🙏 Acknowledgments

- University of Maiduguri for the vision and support
- Django community for the excellent framework
- Open source contributors

## 📞 Support

For support and questions:
- Email: library@unimaid.edu.ng
- Issues: [GitHub Issues](https://github.com/ShedrackAmodu/Unimaid/issues)
- Documentation: [Wiki](https://github.com/ShedrackAmodu/Unimaid/wiki)

