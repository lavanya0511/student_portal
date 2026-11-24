Student Portal
A web-based Student Portal built using FastAPI, Python, SQLite, SQLAlchemy, HTML, and CSS.

Features
- Student registration with input validation
- Secure password hashing using Argon2
- User login and logout
- Session-based authentication
- Protected student dashboard
- Role-based access control for Admin and Students
- Admin dashboard to view registered students
- Admin can delete student accounts
- CSRF protection for form submissions
- Environment variables managed using .env

Technologies Used
- Python
- FastAPI
- SQLite
- SQLAlchemy
- HTML
- CSS
- Jinja2
- Argon2
- Starlette Sessions

Project Setup
1. Clone the repository
git clone https://github.com/lavanya0511/student_portal.git
2. Navigate to the project folder
cd student_portal
3. Create a virtual environment
python -m venv venv
4. Activate the virtual environment
Windows:
venv\Scripts\activate
5. Install dependencies
pip install -r requirements.txt
6. Configure environment variables
Create a .env file in the project root:
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./students.db
Replace the secret key with a secure random value.
Run the Application
uvicorn main:app --reload

Open the application in your browser:
http://127.0.0.1:8000

Security
- Passwords are stored as secure hashes, not plain text.
- Session-based authentication protects restricted pages.
- Role-based authorization prevents students from accessing admin pages.
- CSRF tokens protect form submissions.
- Sensitive configuration is stored in environment variables.

Author
Developed as a Python web development project.