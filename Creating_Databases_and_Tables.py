import os
from dotenv import load_dotenv

load_dotenv()

import mysql.connector
connection = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "YOUR_PASSWORD_HERE")
)
cursor=connection.cursor()
cursor.execute("CREATE DATABASE job_portal")

cursor.execute("USE job_portal")

cursor.execute("CREATE TABLE job_seekers\
               (\
               id INT AUTO_INCREMENT PRIMARY KEY,\
               name VARCHAR(100) NOT NULL,\
               email VARCHAR(100) NOT NULL UNIQUE,\
               phone VARCHAR(15),\
               skills VARCHAR(255) NOT NULL,\
               experience INT(10),\
               resume_path TEXT,\
               date_registered DATETIME DEFAULT CURRENT_TIMESTAMP\
                )"
               )

cursor.execute("CREATE TABLE jobs\
               (\
               job_id INT AUTO_INCREMENT PRIMARY KEY,\
               employer_id INT NOT NULL,\
               title VARCHAR(100) NOT NULL,\
               location VARCHAR(255),\
               description TEXT NOT NULL,\
               required_skills VARCHAR (255),\
               experience_required INT(10),\
               date_posted DATETIME DEFAULT CURRENT_TIMESTAMP\
               )"
               )

cursor.execute("CREATE TABLE employers\
               (\
               employer_id INT AUTO_INCREMENT PRIMARY KEY,\
               job_id INT,\
               company_name VARCHAR(100) NOT NULL,\
               email VARCHAR(100) NOT NULL UNIQUE,\
               password VARCHAR(255) NOT NULL,\
               phone VARCHAR(15),\
               website VARCHAR(255),\
               description VARCHAR(255),\
               date_registered DATETIME DEFAULT CURRENT_TIMESTAMP,\
               FOREIGN KEY (job_id) REFERENCES jobs(job_id)\
               )"
               )

#Creating job_applications table

cursor.execute("CREATE TABLE applications\
               (\
               application_id INT AUTO_INCREMENT PRIMARY KEY,\
               job_id INT,\
               seeker_id INT,\
               status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',\
               application_date DATETIME DEFAULT CURRENT_TIMESTAMP,\
               FOREIGN KEY (job_id) REFERENCES jobs(job_id),\
               FOREIGN KEY (seeker_id) REFERENCES job_seekers(id)\
               )"
               )

#ALTER TABLE applications 
#ADD COLUMN application_date DATETIME DEFAULT CURRENT_TIMESTAMP;


cursor.execute("CREATE TABLE notifications\
               (\
                notification_id INT AUTO_INCREMENT PRIMARY KEY,\
                seeker_id INT,\
                job_id INT,\
                message TEXT NOT NULL,\
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,\
                FOREIGN KEY (seeker_id) REFERENCES job_seekers(id)\
                )"
                )

#ALTER TABLE notifications
#ADD COLUMN notification_id INT AUTO_INCREMENT PRIMARY KEY;

#ALTER TABLE notifications 
#ADD COLUMN is_read BOOLEAN DEFAULT FALSE;

#    is_read BOOLEAN DEFAULT FALSE,------>not needed
#    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

print("Successfully created")
