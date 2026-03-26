def get_question_decomp_prompt(question, db_schema)->str:
    return f"""    
 ### SQLite SQL tables, with their properties:
# document_types (document_type_code, document_description)
# documents (document_id, document_type_code, grant_id, sent_date, response_-
received_date, other_details)
# grants (grant_id, organisation_id, grant_amount, grant_start_date, grant_end_date,
other_details)
# organisation_types (organisation_type, organisation_type_description)
# organisations (organisation_id, organisation_type, organisation_details)
# project_outcomes (project_id, outcome_code, outcome_details)
# project_staff (staff_id, project_id, role_code, date_from, date_to, other_details)
# projects (project_id, organisation_id, project_details)
# research_outcomes (outcome_code, outcome_description)
# research_staff (staff_id, employer_organisation_id, staff_details)
# staff_roles (role_code, role_description)
# tasks (task_id, project_id, task_details, eg agree objectives)
#
### Question:  Find out the send dates of the documents with the grant amount of
more than 5000 were granted by organisation type described as "Research".
decompose the question
1.  Find out the send dates of the documents.
2.  Find out the send dates of the documents with the grant amount of more than
5000.
3.  Find out the send dates of the documents with the grant amount of more than 5000
were granted by organisation type described as "Research".
# Thus, the answer for the question is:  Find out the send dates of the documents
with the grant amount of more than 5000 were granted by organisation type described
as "Research".
SELECT T1.sent_date FROM documents AS T1 JOIN Grants AS T2 ON T1.grant_id =
T2.grant_id JOIN Organisations AS T3 ON T2.organisation_id = T3.organisation_id
JOIN organisation_Types AS T4 ON T3.organisation_type = T4.organisation_type WHERE
T2.grant_amount > 5000 AND T4.organisation_type_description = ’Research’
### SQLite SQL tables, with their properties:
# stadium (stadium_id, location, name, capacity, highest, lowest, average)
# singer (singer_id, name, country, song_name, song_release_year, age, is_male)
# concert (concert_id, concert_name, theme, stadium_id, year)
# singer_in_concert (concert_id, singer_id)
#
### Question:  {question}
### Database schema: {db_schema}
decompose the question and use with the given Database schema the question. 
Return only a sql query without any comments or explanation.  
"""