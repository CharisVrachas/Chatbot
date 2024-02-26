from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

import mysql.connector

app = FastAPI()

# Configure your MySQL database connection
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "uniBot"
}


# This List match the input user information to database field
field_mapping = {
    "code": "course_code",
    "semester": "semester",
    "type": "course_type",
    "hours": "lectures",
    "ects": "ects",
    "instructor": "instructors",
    "teacher": "instructors",
    "url": "course_webpage",
    "link": "course_webpage",
    "webpage": "course_webpage",
    "goals": "educational_goals",
    "learns": "educational_goals",
    "content": "course_contents",
    "info": "course_contents",
    "teaching method": "teaching_method",
    "method": "teaching_method",
    "evaluation": "students_evaluation"
}


@app.get("/")
async def root():
    return {"message": "OK"}


@app.post("/")
async def handle_request(request: Request):

    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    intent = payload['queryResult']['intent']['displayName']
    user_input = payload['queryResult']['queryText']

    if intent == "subject.search-info" or intent == "info.search-subject":
        if intent == "subject.search-info":
            # Variable from JSON
            information = payload['queryResult']['parameters']['information']
            subject = payload['queryResult']['outputContexts'][0]['parameters']['subject']
        elif intent == "info.search-subject":
            # Variable from JSON
            subject = payload['queryResult']['parameters']['subject']
            information = payload['queryResult']['outputContexts'][0]['parameters']['information']

        # If input user there is into list
        matched_field = field_mapping.get(information)

        if matched_field:
            # Input user is matching the database field
            field_name = matched_field

            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()

                # SQL query in order to take information that we need
                query = f"""
                    SELECT {field_name}
                    FROM courses
                    WHERE course_title = %s
                """
                cursor.execute(query, (subject,))

                result = cursor.fetchone()

                cursor.close()
                connection.close()

                if result:
                    if result[0] == "N/A" or result[0] is None:
                        response_text = f"No information found for {subject}."
                    else:
                        response_text = f"{information.capitalize()} for {subject} is {result[0]}"
                else:
                    response_text = f"No information found for {subject}."
            except mysql.connector.Error as err:
                response_text = "An error occurred while retrieving information from the database."
        else:
            response_text = "The input does not match any field in the database."
    elif intent == "multiple.search":

        information_list = payload['queryResult']['parameters']['information']
        subject_list = payload['queryResult']['parameters']['subject']

        responses = []

        if len(information_list) > 0 and len(subject_list) > 0:
            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()

                for subject in subject_list:
                    subject_responses = []

                    for information in information_list:
                        matched_field = field_mapping.get(information)

                        if matched_field:
                            field_name = matched_field

                            query = f"""
                                SELECT {field_name}
                                FROM courses
                                WHERE course_title = %s
                            """
                            cursor.execute(query, (subject,))
                            result = cursor.fetchone()

                            if result:
                                if result[0] == "N/A" or result[0] is None:
                                    response_text = f"No information found for {subject}."
                                    subject_responses.append(response_text)
                                else:
                                    info_text = f"{information.capitalize()} for {subject} is {result[0]} \n"
                                    subject_responses.append(info_text)
                            else:
                                subject_responses.append(f"No {information} found for {subject}.")
                        else:
                            subject_responses.append(f"The input '{information}' does not match any field in the database for {subject}.")

                    responses.append("\n".join(subject_responses))

                cursor.close()
                connection.close()
            except mysql.connector.Error as err:
                responses.append("An error occurred while retrieving information from the database.")
        else:
            responses.append("Please provide at least one 'information' and 'subject'.")

        response_text = "\n\n".join(responses)
    elif intent == "info.study-program":
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Grab all semesters
            cursor.execute("SELECT semester FROM courses ORDER BY id DESC LIMIT 1;")
            last_semester = cursor.fetchone()

            cursor.close()
            connection.close()

            if last_semester:
                response_text = f"The latest semester is {last_semester[0]}. Do you want to learn more information about semesters?"
            else:
                response_text = "No semesters found in the database."
        except mysql.connector.Error as err:
            response_text = "An error occurred while connecting to the database."
    elif intent == "info.semester":
        semester_field = payload['queryResult']['parameters']['semester']

        if semester_field:
            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()

                cursor.execute("SELECT course_title, semester FROM courses WHERE semester = %s", (semester_field,))
                course_data = cursor.fetchall()

                semester_value = course_data[0][1]

                cursor.close()
                connection.close()

                if course_data:
                    course_info_list = [f"The courses for {semester_value} semester:"]

                    for idx, (title, _) in enumerate(course_data, start=1):
                        course_info_list.append(f"{idx}. {title}")

                    response_text = "\n".join(course_info_list)
                else:
                    response_text = f"No courses found for {semester_value} semester."
            except mysql.connector.Error as err:
                response_text = "An error occurred while connecting to the database."
        else:
            response_text = "The input of semester number does not match any field in the database."


    return JSONResponse(content={"fulfillmentText": response_text})


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)