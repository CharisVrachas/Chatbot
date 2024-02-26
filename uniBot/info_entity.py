import os
from google.cloud import dialogflow_v2 as dialogflow

# Set the credentials from Dialogflow.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key_uniBot.json"

# Connect with Dialogflow.
client = dialogflow.EntityTypesClient()

# Define the entity name.
entity_name = "projects/unibot-prvi/agent/entityTypes/21f36b89-d4c7-4931-9e13-bc1156fe221c"

# Read structured words from the text file.
with open("information.txt", "r") as file:
    structured_words = [line.strip() for line in file]

# Get the existing entity.
entity_type = client.get_entity_type(name=entity_name)

# Process and add synonyms to the entity for each structured word.
for word in structured_words:
    parts = word.split("/")
    
    # Check if the word contains "/".
    if len(parts) > 1:
        main_word = parts[0]
        synonyms = parts[1:]
    else:
        main_word = word
        synonyms = []
    
    # Add the main word and synonyms to the entity.
    entity_type.entities.append(dialogflow.EntityType.Entity(value=main_word, synonyms=synonyms))

# Update the existing entity.
client.update_entity_type(entity_type=entity_type)

print("Entity 'information' updated with synonyms from the text file.")