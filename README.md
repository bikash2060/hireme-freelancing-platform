# HireMe – Freelancing Web App

**HireMe** is a freelancing web application tailored for the Nepali market, developed as a college project. It connects local freelancers with businesses and clients, providing a platform for posting projects, bidding, contracting, and secure payment integration using local methods like **eSewa** and **Khalti**.

## 🚀 Features

- User Authentication (Email Verification & Google Sign-In)
- Role-based Access: Freelancer & Client
- Project Posting & Bidding System
- Real-Time Messaging System
- Contract Management Workflow
- Ratings & Reviews for Freelancers
- Local Payment Integration: eSewa and Khalti
- Skill-Based Job Recommendations using AI
- Multilingual Support (English & Nepali)
- Admin Dashboard (Optional if added)

## 🔧 Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, Django Templates
- **Database**: MySQL
- **Authentication**: OTP Email Verification, Google OAuth 2.0
- **Payment Gateway**: eSewa, Khalti
- **AI/ML**: Logistic Regression, KNN, Naive Bayes (for job recommendations)

## 📁 Project Structure

HireMe/
├── accounts/ # User authentication and profile
├── projects/ # Project and bid management
├── chat/ # Real-time messaging
├── contracts/ # Contract handling
├── payment/ # Payment integration logic
├── templates/ # HTML templates
├── static/ # CSS, JS, Images
├── manage.py
├── requirements.txt
└── README.md

## 🧪 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/bikash2060/hireme-freelancing-platform.git
cd hireme-freelancing-platform
```
### 2. Create the Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### 3. Install the required dependencies and libraries
```bash
pip install -r requirements.txt
```
### 4. Apply the Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
### 5. Run the Server
```bash
python manage.py runserver
```

