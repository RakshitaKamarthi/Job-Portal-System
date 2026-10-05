import mysql.connector
from mysql.connector import Error
import sys
import os
import shutil
from datetime import datetime
import bcrypt

# Constants
RESUME_DIR = 'resumes'

# Ensure the resumes directory exists
if not os.path.exists(RESUME_DIR):
    os.makedirs(RESUME_DIR)

# Function to connect to MySQL database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  
            database='job_portal',
            user='root',        
            password='sql@123'  
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

# ----------------------- Job Seeker Functions (I) -----------------------

# Function to register a job seeker
def register_job_seeker(connection):
    name = input("Enter your name: ").strip()
    email = input("Enter your email: ").strip()
    phone = input("Enter your phone number: ").strip()
    skills = input("Enter your skills (comma-separated): ").strip()
    experience = input("Enter your years of experience: ").strip()
    
    # Validate experience input
    try:
        experience = int(experience)
    except ValueError:
        print("Experience must be a number.")
        return
    
    # Handle resume submission
    resume_path_input = input("Enter the path to your resume file (e.g., /path/to/resume.pdf): ").strip()
    if not os.path.isfile(resume_path_input):
        print("Resume file does not exist. Please provide a valid file path.")
        return
    
    # Generate a unique filename for the resume
    _, file_extension = os.path.splitext(resume_path_input)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    sanitized_email = email.replace('@', 'at').replace('.', '_')
    new_resume_filename = f"{sanitized_email}_{timestamp}{file_extension}"
    new_resume_path = os.path.join(RESUME_DIR, new_resume_filename)
    
    try:
        shutil.copy(resume_path_input, new_resume_path)
        print(f"Resume uploaded successfully to {new_resume_path}")
    except Exception as e:
        print(f"Failed to upload resume: {e}")
        return
    
    try:
        cursor = connection.cursor()
        query = """INSERT INTO job_seekers (name, email,phone, skills,experience, resume_path)
                   VALUES (%s,%s,%s,%s, %s, %s)"""
        values = (name, email,phone, skills, experience,new_resume_path)
        cursor.execute(query, values)
        connection.commit()
        print("Job seeker registered successfully!")
    except mysql.connector.IntegrityError:
        print("A job seeker with this email already exists.")
        # Optionally, remove the uploaded resume if registration fails
        if os.path.exists(new_resume_path):
            os.remove(new_resume_path)
    except Error as e:
        print(f"Failed to register job seeker: {e}")
        # Optionally, remove the uploaded resume if registration fails
        if os.path.exists(new_resume_path):
            os.remove(new_resume_path)

# Function to display all registered job seekers (Admin functionality)
def display_job_seekers(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, phone, skills, experience FROM job_seekers")
        result = cursor.fetchall()

        print("\n--- Registered Job Seekers ---")
        for row in result:
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Phone: {row[3]}, Skills: {row[4]}, Experience: {row[5]} years")
    except Error as e:
        print(f"Failed to fetch job seekers: {e}")

# ----------------------- Employer Functions -----------------------

# Function to register an employer
def register_employer(connection):
    company_name = input("Enter your company name: ").strip()
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()
    phone = input("Enter your contact phone number: ").strip()
    website = input("Enter your company website (e.g., https://www.company.com): ").strip()
    description = input("Enter a brief description of your company: ").strip()
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor = connection.cursor()
        query = """INSERT INTO employers (company_name, email, password, phone, website, description)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (company_name, email, hashed_password.decode('utf-8'), phone, website, description)
        cursor.execute(query, values)
        connection.commit()
        print("Employer registered successfully!")
    except mysql.connector.IntegrityError:
        print("An employer with this email already exists.")
    except Error as e:
        print(f"Failed to register employer: {e}")

# Function to login an employer
def login_employer(connection):
    email = input("Enter your employer email: ").strip()
    password = input("Enter your password: ").strip()
    
    try:
        cursor = connection.cursor()
        query = "SELECT employer_id, password FROM employers WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        
        if result:
            employer_id, hashed_password = result
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                print("Login successful!")
                employer_menu(connection, employer_id)
            else:
                print("Incorrect password.")
        else:
            print("No employer found with the provided email.")
    except Error as e:
        print(f"Failed to login: {e}")

# Employer menu after login
def employer_menu(connection, employer_id):
    while True:
        print("\n--- Employer Menu ---")
        print("1. Create/Update Company Profile")
        print("2. Post a Job")
        print("3. View My Job Listings")
        print("4. Review Job Applications")
        print("5. Logout")
        choice = input("Choose an option: ").strip()
        
        if choice == '1':
            create_update_company_profile(connection, employer_id)
        elif choice == '2':
            post_job(connection, employer_id)
        elif choice == '3':
            view_employer_job_listings(connection, employer_id)
        elif choice == '4':
            review_job_applications(connection, employer_id)
        elif choice == '5':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")

# Function to create or update company profile
def create_update_company_profile(connection, employer_id):
    print("\n--- Create/Update Company Profile ---")
    company_name = input("Enter your company name: ").strip()
    phone = input("Enter your contact phone number: ").strip()
    website = input("Enter your company website (e.g., https://www.company.com): ").strip()
    description = input("Enter a brief description of your company: ").strip()
    
    try:
        cursor = connection.cursor()
        # Check if the employer already has a profile
        cursor.execute("SELECT * FROM employers WHERE employer_id = %s", (employer_id,))
        if cursor.fetchone():
            # Update existing profile
            query = """UPDATE employers 
                       SET company_name = %s, phone = %s, website = %s, description = %s 
                       WHERE employer_id = %s"""
            values = (company_name, phone, website, description, employer_id)
            cursor.execute(query, values)
            connection.commit()
            print("Company profile updated successfully!")
        else:
            # Create new profile (This case might not occur as profile is created during registration)
            query = """INSERT INTO employers (company_name, phone, website, description)
                       VALUES (%s, %s, %s, %s)"""
            values = (company_name, phone, website, description)
            cursor.execute(query, values)
            connection.commit()
            print("Company profile created successfully!")
    except Error as e:
        print(f"Failed to create/update company profile: {e}")

# Function for employer to post a job
def post_job(connection, employer_id):
    print("\n--- Post a Job ---")
    job_id = input("Enter your job ID:").strip()
    title = input("Enter job title: ").strip()
    location = input("Enter job location: ").strip()
    description = input("Enter job description: ").strip()
    required_skills = input("Enter required skills (comma-separated): ").strip()
    experience_required = input("Enter required years of experience: ").strip()
    
    # Validate experience_required input
    try:
        experience_required = int(experience_required)
    except ValueError:
        print("Experience required must be a number.")
        return

    try:
        cursor = connection.cursor()
        query = """INSERT INTO jobs (job_id,title, location, description, required_skills, experience_required, employer_id)
                   VALUES (%s, %s,%s, %s, %s, %s, %s)"""
        values = (job_id,title, location, description, required_skills, experience_required, employer_id)
        cursor.execute(query, values)
        connection.commit()
        print("Job posted successfully!")
    except Error as e:
        print(f"Failed to post job: {e}")

# Function to view employer's job listings
def view_employer_job_listings(connection, employer_id):
    try:
        cursor = connection.cursor()
        query = "SELECT job_id, title, location, description, required_skills, experience_required FROM jobs WHERE employer_id = %s"
        cursor.execute(query, (employer_id,))
        job_name = cursor.fetchall()

        print("\n--- My Job Listings ---")
        '''
        if not jobs:
            print("You have no job listings.")
            return '''

        for job in job_name:
            print(f"\nJob ID: {job[0]}")
            print(f"Title: {job[1]}")
            print(f"Location: {job[2]}")
            print(f"Description: {job[3]}")
            print(f"Required Skills: {job[4]}")
            print(f"Experience Required: {job[5]} years")
    except Error as e:
        print(f"Failed to fetch your job listings: {e}")

# Function to review job applications
def review_job_applications(connection, employer_id):
    try:
        cursor = connection.cursor(dictionary=True)
        # Fetch all jobs posted by the employer
        cursor.execute("SELECT job_id, title FROM jobs WHERE employer_id = %s", (employer_id,))
        jobs = cursor.fetchall()
        
        if not jobs:
            print("You have no job listings to review applications for.")
            return
        
        print("\n--- Your Job Listings ---")
        for job in jobs:
            print(f"Job ID: {job['job_id']}, Title: {job['title']}")

        job_id = input("Enter the Job ID you want to review applications for: ").strip()
        try:
            job_id = int(job_id)
        except ValueError:
            print("Job ID must be a number.")
            return

        # Verify the job belongs to the employer
        if not any(job['job_id'] == job_id for job in jobs):
            print("Invalid Job ID. Please select a Job ID from your listings.")
            return

        # Fetch applications for the selected job
        query = """
            SELECT applications.application_id, job_seekers.id as seeker_id, job_seekers.name, job_seekers.email, job_seekers.phone, job_seekers.skills, job_seekers.experience, job_seekers.resume_path, applications.status, applications.application_date
            FROM applications
            JOIN job_seekers ON applications.seeker_id = job_seekers.id
            WHERE applications.job_id = %s
        """
        cursor.execute(query, (job_id,))
        applications = cursor.fetchall()

        if not applications:
            print("No applications found for this job.")
            return

        print(f"\n--- Applications for Job ID {job_id} ---")
        for app in applications:
            print(f"\nApplication ID: {app['application_id']}")
            print(f"Seeker ID: {app['seeker_id']}")
            print(f"Name: {app['name']}")
            print(f"Email: {app['email']}")
            print(f"Phone: {app['phone']}")
            print(f"Skills: {app['skills']}")
            print(f"Experience: {app['experience']} years")
            print(f"Resume Path: {app['resume_path']}")
            print(f"Status: {app['status']}")
            print(f"Application Date: {app['application_date']}")

        # Choose an application to update
        application_id = input("\nEnter the Application ID you want to update (or '0' to cancel): ").strip()
        if application_id == '0':
            print("Cancelling application review.")
            return
        try:
            application_id = int(application_id)
        except ValueError:
            print("Application ID must be a number.")
            return

        # Find the application
        application = next((app for app in applications if app['application_id'] == application_id), None)
        if not application:
            print("Invalid Application ID.")
            return

        if application['status'] != 'Pending':
            print(f"This application has already been {application['status']}.")
            #return

        # Decide to accept or reject
        decision = input("Enter 'A' to Accept or 'R' to Reject this application: ").strip().upper()
        if decision not in ['A', 'R']:
            print("Invalid decision. Please enter 'A' or 'R'.")
            return

        new_status = 'Accepted' if decision == 'A' else 'Rejected'

        # Update the application status
        update_query = "UPDATE applications SET status = %s WHERE application_id = %s"
        cursor.execute(update_query, (new_status, application_id))
        connection.commit()
        print(f"Application {application_id} has been {new_status}.")

        # Send notification to the job seeker
        send_notification(connection, application['seeker_id'], job_id, new_status)

    except Error as e:
        print(f"Failed to review applications: {e}")

# Function to send notifications to job seekers
def send_notification(connection, seeker_id, job_id, status):
    message = f"Your application for Job ID {job_id} has been {status}."
    print(f"Sending notification to Seeker ID {seeker_id}: {message}")
    
    try:
        cursor = connection.cursor()
        # Insert notification into the notifications table (if implemented)
        cursor.execute("""INSERT INTO notifications (seeker_id, job_id, message)
                          VALUES (%s, %s, %s)""", (seeker_id, job_id, message))
        connection.commit()
        print("Notification sent successfully!")
    except Error as e:
        print(f"Failed to send notification: {e}")

# ----------------------- Job Seeker Functions (II) -----------------------

# Function to search for jobs based on criteria
def search_jobs(connection):
    print("\n--- Search Jobs ---")
    print("Search by:")
    print("1. Job Title")
    print("2. Required Skill")
    print("3. Experience Required")
    print("4. Location")
    print("5. Combined Search")
    choice = input("Choose an option: ").strip()

    query = """SELECT jobs.job_id, jobs.title, employers.company_name, jobs.location, jobs.description, 
                      jobs.required_skills, jobs.experience_required
               FROM jobs
               JOIN employers ON jobs.employer_id = employers.employer_id
               WHERE """
    conditions = []
    values = []

    if choice == '1':
        title = input("Enter job title to search: ").strip()
        conditions.append("jobs.title LIKE %s")
        values.append(f"%{title}%")
    elif choice == '2':
        skill = input("Enter required skill to search: ").strip()
        conditions.append("jobs.required_skills LIKE %s")
        values.append(f"%{skill}%")
    elif choice == '3':
        experience = input("Enter maximum years of experience: ").strip()
        try:
            experience = int(experience)
            conditions.append("jobs.experience_required <= %s")
            values.append(experience)
        except ValueError:
            print("Experience must be a number.")
            return
    elif choice == '4':
        location = input("Enter job location to search: ").strip()
        conditions.append("jobs.location LIKE %s")
        values.append(f"%{location}%")
    elif choice == '5':
        title = input("Enter job title to search (leave blank if not applicable): ").strip()
        skill = input("Enter required skill to search (leave blank if not applicable): ").strip()
        experience = input("Enter maximum years of experience (leave blank if not applicable): ").strip()
        location = input("Enter job location to search (leave blank if not applicable): ").strip()

        if title:
            conditions.append("jobs.title LIKE %s")
            values.append(f"%{title}%")
        if skill:
            conditions.append("jobs.required_skills LIKE %s")
            values.append(f"%{skill}%")
        if experience:
            try:
                experience = int(experience)
                conditions.append("jobs.experience_required <= %s")
                values.append(experience)
            except ValueError:
                print("Experience must be a number.")
                return
        if location:
            conditions.append("jobs.location LIKE %s")
            values.append(f"%{location}%")
    else:
        print("Invalid choice.")
        return

    if not conditions:
        print("No search criteria provided.")
        return

    final_query = query + " AND ".join(conditions)
    
    try:
        cursor = connection.cursor()
        cursor.execute(final_query, tuple(values))
        results = cursor.fetchall()

        if results:
            print("\n--- Search Results ---")
            for job in results:
                print(f"\nJob ID: {job[0]}")
                print(f"Title: {job[1]}")
                print(f"Company: {job[2]}")
                print(f"Location: {job[3]}")
                print(f"Description: {job[4]}")
                print(f"Required Skills: {job[5]}")
                print(f"Experience Required: {job[6]} years")
        else:
            print("No jobs found matching the criteria.")
    except Error as e:
        print(f"Failed to search jobs: {e}")

# Function to apply for a job
def apply_for_job(connection):
    seeker_email = input("Enter your registered email: ").strip()
    
    try:
        cursor = connection.cursor()
        # Get seeker ID and resume_path
        cursor.execute("SELECT id, resume_path FROM job_seekers WHERE email = %s", (seeker_email,))
        seeker = cursor.fetchone()
        if not seeker:
            print("No job seeker found with the provided email.")
            return
        seeker_id, resume_path = seeker

        if not resume_path or not os.path.isfile(resume_path):
            print("Resume not found. Please ensure you have uploaded your resume during registration.")
            return

        job_id = input("Enter the Job ID you want to apply for: ").strip()
        try:
            job_id = int(job_id)
        except ValueError:
            print("Job ID must be a number.")
            return

        # Check if job exists
        cursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
        job = cursor.fetchone()
        if not job:
            print("No job found with the provided Job ID.")
            return

        # Check if already applied
        cursor.execute("SELECT * FROM applications WHERE job_id = %s AND seeker_id = %s", (job_id, seeker_id))
        if cursor.fetchone():
            print("You have already applied for this job.")
            return

        # Insert application
        cursor.execute("INSERT INTO applications (job_id, seeker_id) VALUES (%s, %s)", (job_id, seeker_id))
        connection.commit()
        print("Applied for the job successfully!")
    except Error as e:
        print(f"Failed to apply for job: {e}")

# Function to view applied jobs with resume details and status
def view_applied_jobs(connection):
    seeker_email = input("Enter your registered email: ").strip()
    
    try:
        cursor = connection.cursor()
        # Get seeker ID
        cursor.execute("SELECT id FROM job_seekers WHERE email = %s", (seeker_email,))
        seeker = cursor.fetchone()
        if not seeker:
            print("No job seeker found with the provided email.")
            return
        seeker_id = seeker[0]

        # Fetch applied jobs
        query = """
            SELECT jobs.job_id, jobs.title, employers.company_name, jobs.location, 
                   applications.application_date, applications.status
            FROM applications
            JOIN jobs ON applications.job_id = jobs.job_id
            JOIN employers ON jobs.employer_id = employers.employer_id
            WHERE applications.seeker_id = %s
        """
        cursor.execute(query, (seeker_id,))
        applications = cursor.fetchall()

        if applications:
            print("\n--- Applied Jobs ---")
            for app in applications:
                print(f"\nJob ID: {app[0]}")
                print(f"Title: {app[1]}")
                print(f"Company: {app[2]}")
                print(f"Location: {app[3]}")
                print(f"Application Date: {app[4]}")
                print(f"Status: {app[5]}")
        else:
            print("You have not applied for any jobs yet.")
    except Error as e:
        print(f"Failed to fetch applied jobs: {e}")

# ----------------------- Notification Functions -----------------------

# Function to view notifications (if using notifications table)
def view_notifications(connection):
    seeker_email = input("Enter your registered email: ").strip()
    
    try:
        cursor = connection.cursor()
        # Get seeker ID
        cursor.execute("SELECT id FROM job_seekers WHERE email = %s", (seeker_email,))
        seeker = cursor.fetchone()
        if not seeker:
            print("No job seeker found with the provided email.")
            return
        seeker_id = seeker[0]

        # Fetch notifications
        query = """
            SELECT notifications.notification_id, notifications.message, notifications.created_at
            FROM notifications
            WHERE notifications.seeker_id = %s
            ORDER BY notifications.created_at DESC
        """
        cursor.execute(query, (seeker_id,))
        notifications = cursor.fetchall()

        if notifications:
            print("\n--- Notifications ---")
            for notif in notifications:
                #status = "Read" if notif[2] else "Unread"
                print(f"\nNotification ID: {notif[0]}")
                print(f"Message: {notif[1]}")
                #print(f"Status: {status}")
                print(f"Date: {notif[2]}")
        else:
            print("No notifications found.")
    except Error as e:
        print(f"Failed to fetch notifications: {e}")

# ----------------------- Main Menu Functions -----------------------

# Function to display all job listings
def display_job_listings(connection):
    try:
        cursor = connection.cursor()
        query = """
            SELECT jobs.job_id, jobs.title, employers.company_name, jobs.location, jobs.description, 
                   jobs.required_skills, jobs.experience_required
            FROM jobs
            JOIN employers ON jobs.employer_id = employers.employer_id
        """
        cursor.execute(query)
        jobs = cursor.fetchall()

        print("\n--- Job Listings ---")
        for job in jobs:
            print(f"\nJob ID: {job[0]}")
            print(f"Title: {job[1]}")
            print(f"Company: {job[2]}")
            print(f"Location: {job[3]}")
            print(f"Description: {job[4]}")
            print(f"Required Skills: {job[5]}")
            print(f"Experience Required: {job[6]} years")
    except Error as e:
        print(f"Failed to fetch job listings: {e}")

# Function to send notifications to job seekers (email or in-app)
# Since it's terminal-based, we'll use in-app notifications via the notifications table
def send_notification(connection, seeker_id, job_id, status):
    message = f"Your application for Job ID {job_id} has been {status}."
    print(f"Sending notification to Seeker ID {seeker_id}: {message}")
    
    try:
        cursor = connection.cursor()
        # Insert notification into the notifications table
        cursor.execute("""INSERT INTO notifications (seeker_id, job_id, message)
                          VALUES (%s, %s, %s)""", (seeker_id, job_id, message))
        connection.commit()
        print("Notification sent successfully!")
    except Error as e:
        print(f"Failed to send notification: {e}")

# Main function to run the job portal
def main():
    connection = create_connection()
    if connection is None:
        print("Exiting program.")
        sys.exit()

    while True:
        print("\n--- Job Portal ---")
        print("Select your role:")
        print("1. Job Seeker")
        print("2. Employer")
        print("3. View Registered Job Seekers (Admin)")
        print("4. Exit")
        role_choice = input("Choose an option: ").strip()

        if role_choice == '1':
            # Job Seeker Menu
            while True:
                print("\n--- Job Seeker Menu ---")
                print("1. Register as a Job Seeker")
                print("2. View Registered Job Seekers")
                print("3. View Job Listings")
                print("4. Search Jobs")
                print("5. Apply for a Job")
                print("6. View Applied Jobs")
                print("7. View Notifications")
                print("8. Exit to Main Menu")
                choice = input("Choose an option: ").strip()

                if choice == '1':
                    register_job_seeker(connection)
                elif choice == '2':
                    display_job_seekers(connection)
                elif choice == '3':
                    display_job_listings(connection)
                elif choice == '4':
                    search_jobs(connection)
                elif choice == '5':
                    apply_for_job(connection)
                elif choice == '6':
                    view_applied_jobs(connection)
                elif choice == '7':
                    view_notifications(connection)
                elif choice == '8':
                    break
                else:
                    print("Invalid choice. Please try again.")
        
        elif role_choice == '2':
            # Employer Menu
            while True:
                print("\n--- Employer Menu ---")
                print("1. Register as an Employer")
                print("2. Login as Employer")
                print("3. Exit to Main Menu")
                choice = input("Choose an option: ").strip()

                if choice == '1':
                    register_employer(connection)
                elif choice == '2':
                    login_employer(connection)
                elif choice == '3':
                    break
                else:
                    print("Invalid choice. Please try again.")
        
        elif role_choice == '3':
            # Admin Functionality (View Job Seekers)
            display_job_seekers(connection)
        
        elif role_choice == '4':
            if connection.is_connected():
                connection.close()
                print("Disconnected from the database.")
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

# Entry point of the script
##if _name_ == "_main_": --> commented by US
main()
