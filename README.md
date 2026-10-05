# Job Portal System 💼

A Python and MySQL-based recruitment application developed for the **CBSE Class XII Computer Science** practical project.

---

## 👥 Project Team
* **Rakshita Kamarthi**
* **Bavisyaa**
* **Rishikka**

---

## 📌 Overview
The **Job Portal System** is a software solution designed to streamline the hiring process. It provides job seekers with a platform to discover opportunities and allows recruiters/employers to manage job listings and applications efficiently.

---

## ✨ Key Features
* **Authentication & Security:** User registration and secure login handling using `bcrypt` password encryption.
* **Candidate Portal:** Browse job openings, search by role or location, and submit applications.
* **Recruiter Portal:** Post new job vacancies, review candidate profiles, and manage job listings.
* **Database Management:** Full database CRUD operations powered by MySQL.
* **Environment Protection:** Database credentials securely stored in local environment settings.

---

## 🛠️ Tech Stack
* **Programming Language:** Python 3.x
* **Database:** MySQL Server
* **Libraries & Dependencies:**
  * `mysql-connector-python` — MySQL database driver
  * `bcrypt` — Password hashing and authentication security
  * `python-dotenv` — Environment variable management

---

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure Python 3.x and MySQL Server are installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/RakshitaKamarthi/job-portal-system.git
cd job-portal-system
```

### 3. Install Required Dependencies
```bash
pip install mysql-connector-python bcrypt python-dotenv
```

### 4. Environment Configuration
Create a `.env` file in the project root directory and add your MySQL database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=job_portal
```

### 5. Run the Project
Execute the main Python script to launch the application:
```bash
python main.py
```

---

## 🎓 Academic Attribution
Developed for educational purposes as part of the CBSE Class XII Computer Science curriculum.