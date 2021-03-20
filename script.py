import sqlite3
from datetime import datetime
from pkg_resources import resource_string

from jenkinsapi.jenkins import Jenkins


# Authenticate and get server instance
server = Jenkins(
	baseurl='http://localhost:8080',
	username='miracle',
	password='jenkins')

# connect to database 
connection = sqlite3.connect(database='jenkins.db')
cursor = connection.cursor()


# get jobs 
for job_name, job_instance in server.get_jobs():
	if job_instance.is_running():
		status = 'RUNNING'
	elif job_instance.get_last_build_or_none() is None :
		status = 'NOT_BUILT'
	else:
		job = server.get_job(job_instance.name)
		build = job.get_last_build()
		status = build.get_status()
		
	date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

	create_data = (job_instance.name, status, date)

	# create table if it does not exist
	cursor.execute('''CREATE TABLE IF NOT EXISTS jenkins (id INTEGER PRIMARY KEY AUTOINCREMENT, 
				job_name VARCHAR(100) NOT NULL, status VARCHAR(50) NOT NULL,
				date TEXT NOT NULL)''')

	cursor.execute("SELECT id FROM jenkins WHERE job_name = ?", (job_instance.name,))
	result = cursor.fetchone()

	if result is None:
		print('Saving..! Job details: ', create_data)
		cursor.execute('INSERT INTO jenkins (job_name, status, date) VALUES (?,?,?)', create_data)
	else:
		update_data = (status, date, job_instance.name)
		print('Updating..! Job details: ', update_data)
		cursor.execute('UPDATE jenkins SET status=?, date=? WHERE job_name=?', update_data)


print("Success..!")

# save and close the connection 
connection.commit()
cursor.close()

	
