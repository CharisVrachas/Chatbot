import os
import mysql.connector
from google.cloud import dialogflow_v2 as dialogflow

# Set the credentials from Dialogflow.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key_uniBot.json"

# Connect with DB.
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="uniBot"
)

cursor = db.cursor()

# Run the SQL query in order to grab the subjects title.
cursor.execute("SELECT course_title FROM courses")
courses = cursor.fetchall()

# Save the previous results into array.
subjects = [course[0] for course in courses]

# Connect with Dialogflow.
client = dialogflow.EntityTypesClient()

# Set the entity name that you want to update.
entity_name = "projects/unibot-prvi/agent/entityTypes/51ba006f-d57f-4ba4-804c-84c643afae97"

# Target the entity that there is
entity_type = client.get_entity_type(name=entity_name)

# Update the entity.
for subject in subjects:
    entity_type.entities.append(dialogflow.EntityType.Entity(value=subject))

client.update_entity_type(entity_type=entity_type)

print("Entity updated:", entity_type.name)

# Close DB connection.
cursor.close()
db.close()
