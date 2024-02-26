from bs4 import BeautifulSoup 
import requests
import re
import mysql.connector

# For testing
# import pandas as pd



# Connect with DB
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="uniBot"
)

# Create a cursor
cursor = db.cursor()


# MATHS
url = 'https://www.iee.ihu.gr/en/udg_courses/'

pages = requests.get(url)

soup = BeautifulSoup(pages.text, 'html.parser')

# find the <div> that include the table with Subjects
div_element = soup.find('div', style="overflow-x: auto;")

# Target the (table) into <div>
tables = div_element.find_all('table')

count = 0

# For testing
# data_list = []

total_count_courses = 0

# Use regular expressions in order to find Course Title and Course Code
course_title_pattern = re.compile(r"Course Title: (.+)")
course_code_pattern = re.compile(r"Course Code: (\d+)")
for table in tables:
    td_elements_title = table.find_all('td', title=course_title_pattern)
    td_elements_code = table.find_all('td', title=course_code_pattern)
    
    # Find Course Title and Course Code and save it into variables
    for title, code in zip(td_elements_title, td_elements_code):
        title_text = course_title_pattern.search(title['title']).group(1)
        code_text = course_code_pattern.search(code['title']).group(1)

        count = count + 1

        # Check if there is the Course Code
        if code_text:
            course_url = f'https://www.iee.ihu.gr/en/course/{code_text}/'
            response = requests.get(course_url)
       


            # GENERAL
            # Check if response is ok
            if response.status_code == 200:
                # Grab the HTML page with Soup
                soup = BeautifulSoup(response.text, 'html.parser')

                # find the h1 title that include Course Title
                course_title = soup.find('h1').text.strip()

                # Find the ul which include the <li> that we need
                ul = soup.find('h2', string='General').find_next('ul')

                # Init variables
                course_code = 'N/A'
                semester = 'N/A'
                course_type = 'N/A'
                lectures = 'N/A'
                ects = 'N/A'
                instructors = 'N/A'
                course_webpage = 'N/A'

                # Export data after if...else
                data_items = ul.find_all('li')
                for item in data_items:
                    text = item.text.strip()
                    if text.startswith("Course Code:"):
                        course_code = text.split(":")[1].strip()
                    elif text.startswith("Semester:"):
                        semester = text.split(":")[1].strip()
                    elif text.startswith("Course Type:"):
                        course_type = text.split(":")[1].strip()
                    elif text.startswith("Lectures:"):
                        lectures = text.split(":")[1].strip()
                        lectures_number = re.search(r'\d+', lectures)
                    elif text.startswith("ECTS units:"):
                        ects = text.split(":")[1].strip()
                    elif text.startswith("Instructors:"):
                        instructors = ', '.join([i.text.strip() for i in item.find_all('a')])
                    elif text.startswith("Course webpage:"):
                        course_webpage = item.find('a')['href']



                # EDUCATIONAL GOALS
                # Find the first <h2> tag that include "Educational goals" content
                start_h2_educational_goals = soup.find('h2', string='Educational goals')

                # If you find <h2> tag for Educational Goals, It will start the deep dive in order to save the whole content and save it into list
                if start_h2_educational_goals:
                    educational_goals = []
                    current_tag = start_h2_educational_goals.find_next_sibling()
                    while current_tag and current_tag.name != 'h2':
                        # Use .get_text() method so as to remove HTML tags
                        text = current_tag.get_text(separator=' ')
                        educational_goals.append(text)
                        current_tag = current_tag.find_next_sibling()

                    # Check if there is content into educational_goals list
                    if educational_goals:
                        # If there is, save it into variable
                        educational_goals_content = "\n".join(educational_goals)
                    else:
                        # If there is not, save "N/A" into variable
                        educational_goals_content = "N/A"
                else:
                    # If there is not "Educational goals", save "N/A" into variable
                    educational_goals_content = "N/A"



                # COURSE - CONTENT
                # Find the first <h2> tag that include "Course Contents" content
                start_h2 = soup.find('h2', string='Course Contents')

                # If you find the <h2> tag, It will start the deep dive in order to save the whole content and save it into list
                if start_h2:
                    course_content = []
                    current_tag = start_h2.find_next_sibling()
                    while current_tag and current_tag.name != 'h2':
                        # Use the .get_text() method so as to remove HTML tags
                        text = current_tag.get_text(separator=' ')
                        course_content.append(text)
                        current_tag = current_tag.find_next_sibling()

                    # Check if there is content into course_content variable
                    if course_content:
                        # If there is, save it into variable
                        course_contents_content = "\n".join(course_content)
                    else:
                        # If there is not, save "N/A" into variable
                        course_contents_content = "N/A"
                else:
                    # If there is not "Course Contents", save "N/A" intro variable
                    course_contents_content = "N/A"



                # TEACHING METHOD
                # Find the <h2> tag that include "Teaching Methods - Evaluation" title
                teaching_method_header = soup.find('h2', class_='widget-title', string='Teaching Methods - Evaluation')

                # Init the Teaching Method variable
                teaching_method_content = "N/A"

                # If you find "Teaching Methods - Evaluation" title
                if teaching_method_header:
                    # Find the next <h5> tag that include "Teaching Method" title
                    next_h5 = teaching_method_header.find_next('h5', string='Teaching Method')

                    # If you find "Teaching Method" title and the <ul>
                    if next_h5:
                        next_ul = next_h5.find_next('ul')
                        if next_ul:
                            # Response the <ul>
                            teaching_method_content = next_ul.text.strip()



                # STUDENT EVALUATION
                # Find the <h5> tag that it have "Students evaluation" as content
                h5_element = soup.find('h5', string='Students evaluation')

                # If thare is <h5> tag
                if h5_element:
                    # Find the next <p> tag in the row
                    next_p = h5_element.find_next_sibling('p')
                    
                    # If there is <p>
                    if next_p:
                        # Add break line (\n) before "- ..."
                        students_evaluation_text = next_p.get_text("\n ", strip=True)
                    else:
                        # If there is no <p> tag, add "N/A" into variable
                        students_evaluation_text = "N/A"
                else:
                    # If there is no <h5> tag, add "N/A" into variable
                    students_evaluation_text = "N/A"



                # Insert data into table
                insert_query = "INSERT INTO courses (course_title, course_code, semester, course_type, lectures, ects, instructors, course_webpage, educational_goals, course_contents, teaching_method, students_evaluation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                insert_data = (course_title, course_code, semester, course_type, lectures, ects, instructors, course_webpage, educational_goals_content, course_contents_content, teaching_method_content, students_evaluation_text)
                cursor.execute(insert_query, insert_data)
                
                # # Commit the insert
                db.commit()

                # Append data to the data_list (For testing)
                # data_list.append([course_title, course_code, semester, course_type, lectures, ects, instructors, course_webpage, educational_goals_content, course_contents_content, teaching_method_content, students_evaluation_text])
                
                # It's OK!
                print(f"The {course_title} has been inserted into DB! \n")
                total_count_courses += 1

            else:
                print("The request is failed.")



# Create a DataFrame (For testing)
# df = pd.DataFrame(data_list, columns=["Course Title", "Course Code", "Semester", "Course Type", "Lectures", "ECTS", "Instructors", "Course Webpage", "Educational Goals", "Course Contents", "Teaching Method", "Students Evaluation"])

# Export the DataFrame to an Excel file (For testing)
# df.to_excel("courses_data.xlsx", index=False)

# Close the cursor after the inserts
cursor.close()
db.close()

print(f"Done! {total_count_courses} Subjects have been inserted into DB!")