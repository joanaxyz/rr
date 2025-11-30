<div align="center">

# 🍽️ Restaurant Reservation System

**A modern, full-featured restaurant reservation platform built with Django**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

*Simplify restaurant reservations. Empower diners. Streamline operations.*

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## ✨ Overview

The **Restaurant Reservation System** is a comprehensive web application that revolutionizes how restaurants manage reservations and how customers book dining experiences. Built with Django 5.2.6, this platform offers a seamless interface for diners, powerful management tools for restaurant owners, and robust administrative capabilities.

### 🎯 Key Highlights

- 🚀 **Modern Architecture** - Built with Django 5.2.6 and RESTful API support
- 🔐 **Secure Authentication** - Email verification, password reset, and user management
- 📱 **Responsive Design** - Beautiful, mobile-first UI that works on all devices
- 🏪 **Multi-Restaurant Support** - Restaurant owners can manage multiple establishments
- 👥 **Role-Based Access** - Customers, Owners, Managers, and Staff roles
- 📊 **Real-Time Management** - Dashboard with live reservation updates
- 🗺️ **Interactive Floor Plans** - Visual table management with drag-and-drop
- 📧 **Email Notifications** - Automated reservation confirmations and updates

---

## 🚀 Features

### 👥 For Customers

- ✅ **Easy Registration & Login** - Quick signup with email verification
- 📅 **Smart Reservation Booking** - Select date, time, party size with real-time availability
- 🔍 **Restaurant Discovery** - Search and filter restaurants by location, cuisine, and ratings
- 📋 **Reservation Management** - View, modify, and cancel reservations from your dashboard
- 💬 **Communication** - Email notifications for confirmations, updates, and reminders
- ⭐ **Reviews & Ratings** - Share your dining experiences with other users

### 🏢 For Restaurant Owners

- 🎛️ **Comprehensive Dashboard** - Centralized control panel for all operations
- 🍽️ **Restaurant Profile Management** - Update details, upload photos, set hours
- 📊 **Reservation Analytics** - Track bookings, peak times, and customer trends
- 🪑 **Table Management** - Create and manage floor plans with interactive drag-and-drop
- 👨‍💼 **Staff Management** - Invite and manage team members with role assignments
- ✅ **Owner Verification** - Secure verification process with document uploads
- 📈 **Performance Insights** - View statistics and generate reports

### 👨‍💼 For Staff & Managers

- 📝 **Reservation Handling** - View and manage incoming reservations
- 🔄 **Real-Time Updates** - See new bookings as they come in
- 🎯 **Customer Service Tools** - Access customer information and history
- 🔔 **Notification System** - Stay updated on reservation changes

### 🔧 System Features

- 🌐 **RESTful API** - Full API support via Django REST Framework
- 🔒 **Security** - Password hashing, CSRF protection, secure file uploads
- 📧 **Email Service** - Automated email notifications using Resend
- 🗄️ **Database Support** - SQLite (default) or PostgreSQL for production
- ☁️ **Cloud Storage** - Supabase integration for file storage
- 🎨 **Modern UI/UX** - Beautiful, intuitive interface with smooth animations
- 📱 **Mobile Responsive** - Optimized for all screen sizes

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.2.6
- **API**: Django REST Framework 3.16.1
- **Language**: Python 3.13
- **Database**: SQLite / PostgreSQL (via psycopg2-binary)
- **Authentication**: Django Authentication + JWT (PyJWT)
- **File Storage**: Supabase Storage

### Frontend
- **Templates**: Django Templates
- **Styling**: Custom CSS with modern design
- **Interactivity**: Vanilla JavaScript
- **Icons**: Font Awesome

### DevOps & Tools
- **Web Server**: Gunicorn
- **Static Files**: WhiteNoise
- **Environment**: python-decouple
- **CORS**: django-cors-headers
- **Image Processing**: Pillow
- **Email**: Resend API
- **Maps**: django-leaflet

---

## 📦 Installation

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Git (optional)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rr
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv env
   ```

3. **Activate the virtual environment**
   
   *On Windows:*
   ```bash
   env\Scripts\activate
   ```
   
   *On macOS/Linux:*
   ```bash
   source env/bin/activate
   ```

4. **Navigate to project directory**
   ```bash
   cd rr_project
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Set up environment variables**
   
   Create a `.env` file in `rr_project/` directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   SUPABASE_URL=your-supabase-url
   SUPABASE_ANON_KEY=your-supabase-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
   EMAIL_HOST=your-email-host
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email
   EMAIL_HOST_PASSWORD=your-email-password
   ```

7. **Run migrations**
   ```bash
   python manage.py migrate
   ```

8. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

9. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

10. **Run the development server**
    ```bash
    python manage.py runserver
    ```

11. **Access the application**
    
    Open your browser and navigate to:
    - Main site: `http://127.0.0.1:8000/`
    - Admin panel: `http://127.0.0.1:8000/admin/`

### Quick Setup Script

For automated setup, use the provided build script:

```bash
cd rr_project
bash build.sh
```

---

## 📁 Project Structure

```
rr_project/
├── accounts/                 # User authentication & management
│   ├── models.py            # Custom User model
│   ├── views.py             # Auth views (login, register, profile)
│   ├── forms.py             # Registration & authentication forms
│   └── api.py               # Account API endpoints
│
├── restaurants/             # Restaurant listing & details
│   ├── models.py            # Restaurant models
│   ├── views.py             # Restaurant views
│   └── api.py               # Restaurant API
│
├── reservations/            # Reservation booking system
│   ├── models.py            # Reservation models
│   ├── views.py             # Reservation views
│   └── api.py               # Reservation API
│
├── manage_restaurant/       # Owner dashboard
│   ├── views.py             # Dashboard & management views
│   ├── models.py            # Restaurant management models
│   └── utils.py             # Utility functions
│
├── owner_verification/      # Owner verification workflow
│   ├── models.py            # Verification request models
│   ├── views.py             # Verification views
│   └── supabase_utils.py    # Supabase integration
│
├── email_service/           # Email notification service
│   └── views.py             # Email sending functions
│
├── settings/                # User settings & preferences
│   └── views.py             # Settings views
│
├── home/                    # Home page & landing
│   ├── views.py             # Home views
│   └── urls.py              # Home URLs
│
├── api/                     # REST API structure
│   └── v1/                  # API version 1
│       ├── accounts/        # Account endpoints
│       ├── restaurants/     # Restaurant endpoints
│       └── reservations/    # Reservation endpoints
│
├── templates/               # HTML templates
│   ├── accounts/            # Auth templates
│   ├── restaurants/         # Restaurant templates
│   ├── reservations/        # Reservation templates
│   ├── manage_restaurant/   # Dashboard templates
│   └── common/              # Shared templates
│
├── static/                  # Static files (CSS, JS, images)
│   ├── accounts/            # Account-specific assets
│   ├── restaurants/         # Restaurant-specific assets
│   ├── reservations/        # Reservation-specific assets
│   └── common/              # Shared assets
│
├── media/                   # User-uploaded files
│
├── rr_project/              # Django project settings
│   ├── settings.py          # Main settings file
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
│
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── build.sh                 # Build script
```

---

## 🔌 API Documentation

The application provides a comprehensive REST API for integration with mobile apps or third-party services.

### Base URL
```
/api/v1/
```

### Available Endpoints

- **Accounts**: `/api/v1/accounts/` - User registration, login, profile management
- **Restaurants**: `/api/v1/restaurants/` - Restaurant listing and details
- **Reservations**: `/api/v1/reservations/` - Reservation booking and management
- **Management**: `/api/v1/management/` - Restaurant management endpoints

### Authentication

Most API endpoints require authentication. Include your token in the request headers:

```http
Authorization: Bearer <your-token>
```

For detailed API documentation, see the API endpoints in the `api/v1/` directory.

---

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

Run tests for a specific app:

```bash
python manage.py test accounts
python manage.py test restaurants
python manage.py test reservations
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Set up static file serving
- [ ] Configure email backend
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS settings
- [ ] Set up logging
- [ ] Run migrations
- [ ] Collect static files

### Using Gunicorn

```bash
gunicorn rr_project.wsgi:application
```

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Commit your changes** (`git commit -m 'Add some amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write clear, descriptive commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Django community for the amazing framework
- All contributors who have helped improve this project
- Restaurant owners and customers who provided valuable feedback

---

## 📞 Support

If you encounter any issues or have questions:

- 🐛 **Report bugs**: Open an issue on GitHub
- 💡 **Request features**: Submit a feature request
- 📧 **Contact**: Reach out through the application

---

<div align="center">

**Made with ❤️ using Django**

⭐ Star this repo if you find it helpful!

</div>