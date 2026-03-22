def get_prompt_with_question_decom_and_table_link(question, database_schema):
    return f"""
und was macht dieser code ### SQLite SQL tables, with their properties:
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
SQL table (column):  documents (sent_date)
2.  Find out the send dates of the documents with the grant amount of more than
5000.
SQL table (column):  grants (grant_amount, grant_id)
3.  Find out the send dates of the documents with the grant amount of more than 5000
were granted by organisation type described as "Research".
SQL table (column):  organisation_Types (organisation_type_description,
organisation_type), organisations (organisation_type, organisation_id)
# Thus, the answer for the question is:  Find out the send dates of the documents
with the grant amount of more than 5000 were granted by organisation type described
as "Research".
SELECT T1.sent_date FROM documents AS T1 JOIN Grants AS T2 ON T1.grant_id =
T2.grant_id JOIN Organisations AS T3 ON T2.organisation_id = T3.organisation_id
JOIN organisation_Types AS T4 ON T3.organisation_type = T4.organisation_type WHERE
T2.grant_amount > 5000 AND T4.organisation_type_description = ’Research’
### SQLite SQL tables, with their properties:
{database_schema}
#
### Question:  {question}
decompose the question and use only the given Tables and columns. 
Return only a sql query without any comments or explanation.  
"""