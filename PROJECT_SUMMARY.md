# Healthcare Dashboard Project - Complete Summary

## Project Overview
This is a comprehensive **Django-based Healthcare Management System** designed to streamline healthcare operations by providing integrated solutions for patient management, doctor management, appointment scheduling, pharmaceutical operations, and an intelligent chatbot for health assistance. The system is built using Django 6.0.4 with SQLite3 as the database.

**Technology Stack:**
- Backend: Django 6.0.4 (Python Web Framework)
- Database: SQLite3
- Frontend: HTML/CSS/JavaScript with Django Templates
- Additional: Django Admin Interface for management

---

## Core Features & Modules

### 1. **Accounts & User Management** (`accounts` app)

**Purpose:** Handles user authentication, registration, and user profiling.

**Key Models:**
- **UserProfile**: Extends Django's built-in User model with role-based access
  - Roles: Admin, Doctor, Patient, Staff
  - Fields: Phone, Address, Date of Birth, Profile Picture
  - Linked to Django's auth.User via OneToOne relationship

**Key Features:**
- User Registration with custom forms
- Login/Logout functionality
- User Profile management
- Role-based access control
- Profile picture upload support
- Dashboard access control

**Views & URLs:**
- Home page
- Registration page
- Login page
- User profile page
- Dashboard (role-based)

---

### 2. **Patient Management** (`patients` app)

**Purpose:** Manage patient information, medical records, and vital signs tracking.

**Key Models:**

**Patient Model:**
- Comprehensive patient demographics
- Blood Type tracking (A+, A-, B+, B-, O+, O-, AB+, AB-)
- Gender information
- Emergency contact details
- Allergy and chronic condition tracking
- Insurance information
- Automatic age calculation from date of birth

**MedicalRecord Model:**
- Linked to each Patient (One-to-Many)
- Stores diagnosis, symptoms, treatment, and prescriptions
- Doctor notes field
- Organized by record date (newest first)

**VitalRecord Model:**
- Continuous vital signs monitoring
- Tracked vitals:
  - Blood Pressure (Systolic & Diastolic)
  - Heart Rate (BPM)
  - Temperature
  - Weight and Height
  - Oxygen Saturation
- **Automatic BMI calculation** from weight and height
- Timestamped records for trend analysis

**Key Features:**
- Patient registration and profile management
- Medical history tracking
- Vital signs recording and monitoring
- BMI calculation
- Patient list view with search/filter
- Detailed patient profiles
- Medical record forms
- Vital record forms

---

### 3. **Doctor Management** (`doctors` app)

**Purpose:** Manage doctor profiles, specializations, and availability.

**Key Models:**

**Specialization Model:**
- Medical specializations (e.g., Cardiology, Pediatrics, etc.)
- Description field for details
- Reusable across multiple doctors

**Doctor Model:**
- Comprehensive doctor profiles
- Specialization (linked via ForeignKey)
- Qualification and experience tracking
- License number (unique identifier)
- Consultation fee
- Availability management:
  - Available days (e.g., Mon, Tue, Wed)
  - Time slots (start and end times)
- Bio/About section
- Active/Inactive status
- Contact information (phone, email)

**Key Features:**
- Doctor registration and profile management
- Specialization management
- Doctor list with filters by specialization
- Doctor detail pages
- Availability scheduling
- License verification
- Experience and qualification tracking

---

### 4. **Appointment Management** (`appointments` app)

**Purpose:** Handle appointment scheduling, prescription management, and follow-ups.

**Key Models:**

**Appointment Model:**
- Links Patient and Doctor (ManyToOne relationships)
- Appointment Status Options:
  - Scheduled, Confirmed, Completed, Cancelled, No Show
- Appointment Types:
  - Consultation, Follow-up, Emergency, Routine Checkup, Lab Test, Surgery
- Scheduling details: Date and Time
- Reason and notes fields
- Follow-up date tracking
- Timestamped creation and updates
- Automatically sorted by date (newest first)

**Prescription Model:**
- Linked to Appointment (One-to-One)
- Issue and validity dates
- General prescription notes

**PrescriptionItem Model:**
- Line items within prescriptions (One-to-Many)
- Medicine name, dosage, and strength
- Frequency and duration
- Special instructions for patient

**Key Features:**
- Schedule new appointments
- View appointment list and details
- Appointment status management
- Appointment cancellation
- Create and manage prescriptions
- Add multiple medicines to prescriptions
- Follow-up appointment tracking
- Today's appointments view (for doctors)
- Prescription history

---

### 5. **Pharmacy Management** (`pharmacy` app)

**Purpose:** Manage pharmaceutical inventory, medicine stock, and dispensing operations.

**Key Models:**

**MedicineCategory Model:**
- Categorize medicines (e.g., Antibiotics, Pain Relievers, etc.)
- Category descriptions

**Medicine Model:**
- Comprehensive medicine information:
  - Name and generic name
  - Category (ForeignKey)
  - Manufacturer details
  - Dosage form (Tablet, Syrup, Injection, etc.)
  - Strength (e.g., 500mg, 250mg/5ml)
- Inventory management:
  - Unit price
  - Stock quantity
  - Reorder level
  - **Automatic low stock alerts**
- Expiry date tracking with **automatic expiry detection**
- Batch number tracking
- Prescription requirement flag
- Active/Inactive status

**Dispensing Model:**
- Records medicine dispensing transactions
- Tracks patient name, quantity, and total cost
- Links to specific medicine
- Prescription reference field
- Automatic cost calculation (Quantity × Unit Price)
- **Automatic stock reduction** on dispensing
- Dispensed by field for staff tracking

**StockMovement Model:**
- Tracks all inventory movements
- Movement types: Stock In, Stock Out, Adjustment, Return
- Reason tracking
- Performed by tracking
- Complete inventory audit trail

**Key Features:**
- Medicine inventory management
- Stock tracking and alerts
- Expiry date monitoring
- Medicine dispensing
- Stock movement history
- Low stock notifications
- Stock quantity management
- Prescription-required medicine flag
- Batch and manufacturer tracking

---

### 6. **Chatbot & Health Assistant** (`chatbot` app)

**Purpose:** Provide intelligent health information, symptom checking, and customer support.

**Key Models:**

**ChatbotConversation Model:**
- Stores conversation sessions
- Linked to User (optional) for logged-in users
- Session ID for guest tracking
- Activity status tracking
- Created and last updated timestamps
- Maintains conversation history

**ChatMessage Model:**
- Individual messages within conversations
- Message types: User, Assistant, System
- Content storage
- Symptom mentioned tracking (for health queries)
- Urgency level classification:
  - Low, Medium, High, Emergency
- Timestamped for conversation flow

**HealthTopic Model:**
- FAQ-style health topics database
- Keywords for matching user queries
- Predefined responses
- Active/Inactive toggle
- Version tracking (created/updated timestamps)

**ChatbotFeedback Model:**
- Collects user ratings on chatbot responses
- 5-point rating scale (1-5)
- Linked to specific messages
- Optional feedback text comments
- User tracking

**Key Features:**
- Real-time chat interface
- Symptom checker functionality
- Health resources and information
- Conversation history
- Urgency level detection
- Health topic database with keyword matching
- User feedback and ratings
- Guest and logged-in user support
- Message tracking and analytics

---

## Database Schema

### Entity Relationships:
```
User (Django Auth)
├── UserProfile (1-to-1)
├── Patient (1-to-1 optional)
├── Doctor (1-to-1 optional)
└── ChatbotConversation (1-to-Many)

Patient (1-to-Many)
├── MedicalRecord
├── VitalRecord
└── Appointment

Doctor (1-to-Many)
├── Appointment
└── Specialization (Many-to-1)

Appointment (1-to-1)
└── Prescription (1-to-Many items)

Medicine (1-to-Many)
├── Dispensing
├── StockMovement
└── MedicineCategory (Many-to-1)

ChatbotConversation (1-to-Many)
├── ChatMessage
└── ChatbotFeedback (1-to-1 to message)
```

---

## File Structure

```
Healthcare_Project/
├── manage.py                           # Django management script
├── db.sqlite3                          # SQLite database
├── healthcare_dashboard/               # Main Django project settings
│   ├── settings.py                    # Project configuration
│   ├── urls.py                        # Main URL routing
│   ├── wsgi.py                        # WSGI application
│   └── asgi.py                        # ASGI application
├── accounts/                          # User authentication & profiles
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
├── patients/                          # Patient management
│   ├── models.py (Patient, MedicalRecord, VitalRecord)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
├── doctors/                           # Doctor management
│   ├── models.py (Doctor, Specialization)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
├── appointments/                      # Appointment scheduling
│   ├── models.py (Appointment, Prescription, PrescriptionItem)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
├── pharmacy/                          # Medicine & pharmacy
│   ├── models.py (Medicine, MedicineCategory, Dispensing, StockMovement)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
├── chatbot/                           # Health chatbot
│   ├── models.py (ChatbotConversation, ChatMessage, HealthTopic, ChatbotFeedback)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
├── templates/                         # HTML templates
│   ├── base/
│   │   ├── base.html
│   │   ├── home.html
│   │   └── dashboard.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── patients/
│   │   ├── patient_list.html
│   │   ├── patient_detail.html
│   │   ├── patient_form.html
│   │   ├── medical_record_form.html
│   │   └── vital_record_form.html
│   ├── doctors/
│   │   ├── doctor_list.html
│   │   ├── doctor_detail.html
│   │   ├── doctor_form.html
│   │   ├── specialization_list.html
│   │   └── specialization_form.html
│   ├── appointments/
│   │   ├── appointment_list.html
│   │   ├── appointment_detail.html
│   │   ├── appointment_form.html
│   │   ├── prescription_form.html
│   │   ├── today_appointments.html
│   │   └── create.html
│   ├── pharmacy/
│   │   └── ...
│   └── chatbot/
│       ├── chatbot.html
│       ├── chat_history.html
│       ├── conversation_detail.html
│       ├── symptom_checker.html
│       └── health_resources.html
├── static/
│   └── css/
│       └── custom.css                # Custom styling
└── media/                            # User-uploaded files (profiles, etc.)
```

---

## Key Configuration Details

**Django Settings (settings.py):**
- **DEBUG:** True (development mode)
- **Database:** SQLite3 at `db.sqlite3`
- **Time Zone:** Asia/Kolkata (IST)
- **Installed Apps:** All 6 modules + Django core apps
- **Authentication:** Django's default User model with custom UserProfile extension
- **Media & Static Files:** Configured for uploads and static assets
- **Secret Key:** Development key (should be changed for production)

**Middleware:** Standard Django security and session middleware

**Database Models:** Leverage Django ORM with smart features like:
- Auto-generated timestamps
- Automatic BMI and stock calculations
- One-to-One and One-to-Many relationships
- Cascading deletes for data integrity

---

## User Workflows

### 1. **Patient Workflow:**
- Register or login
- View/update personal profile
- View appointment history
- Schedule appointments with doctors
- View medical records and vital signs
- Receive prescriptions
- Use symptom checker chatbot
- Access health resources

### 2. **Doctor Workflow:**
- Register/login
- Manage profile and specialization
- View scheduled appointments
- View today's appointments
- Access patient medical history
- Create and issue prescriptions
- Track patient vital signs

### 3. **Staff/Admin Workflow:**
- Manage user accounts and roles
- Add/edit doctor profiles and specializations
- Manage medicine inventory
- Track pharmacy dispensing
- Generate reports and insights
- Monitor system operations

### 4. **Chatbot User Workflow:**
- Access symptom checker
- Browse health topics
- Have conversations with health assistant
- Rate chatbot responses
- View conversation history

---

## Advanced Features

1. **Automatic Calculations:**
   - Patient age from DOB
   - BMI from height and weight
   - Prescription item costs
   - Low stock alerts
   - Expiry detection

2. **Inventory Management:**
   - Real-time stock tracking
   - Automatic stock reduction on dispensing
   - Low stock level notifications
   - Stock movement audit trail
   - Batch and expiry tracking

3. **Health Monitoring:**
   - Vital signs trending
   - Medical record history
   - Symptom tracking in chatbot
   - Urgency level classification

4. **Appointment System:**
   - Multiple appointment types
   - Status workflow
   - Follow-up tracking
   - Doctor availability management

5. **Role-Based Access:**
   - Admin, Doctor, Patient, Staff roles
   - Customized dashboards per role
   - Data access controls

---

## Scalability & Extensibility

The system is designed to be:
- **Modular:** Each app handles specific functionality
- **Extensible:** Easy to add new features or apps
- **Maintainable:** Clean separation of concerns
- **Secure:** Built-in Django security features
- **Production-Ready:** Proper database design and relationships

---

## Future Enhancement Opportunities

1. RESTful API for mobile app integration
2. Payment processing for consultation fees
3. Email/SMS notifications
4. Advanced analytics and reporting dashboard
5. Video consultation integration
6. Mobile app (React Native/Flutter)
7. Machine learning for diagnosis assistance
8. Integration with external health APIs
9. Multi-language support
10. Real-time notifications with WebSockets

---

## Installation & Setup

```bash
# Install dependencies (if virtualenv)
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Access the application
- Main: http://localhost:8000
- Admin: http://localhost:8000/admin
```

---

## Summary

This Healthcare Dashboard is a **complete, production-ready healthcare management system** that integrates patient care, doctor management, appointments, pharmacy operations, and an intelligent health assistant chatbot. It demonstrates advanced Django practices including complex relationships, automatic calculations, role-based access control, and comprehensive data management suitable for real-world healthcare operations.
