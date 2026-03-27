def get_question_decomposition_prompt(QUESTION):
    return f"""
You are tasked with decomposing a natural language question into smaller subquestions to help generate an SQL query from a database.
Your goal is to break the question into simple, specific subquestions that together fully address the original question. Each subquestion should focus on a single aspect or step needed to answer the original question, such as identifying data, filtering, or calculating something.
Here are some examples:
Example 1:
Original Question: “What is the total revenue from orders placed in 2023?” Subquestions:
1.“Which orders were placed in 2023?”
2.“What is the revenue for each of those orders?” 3.“What is the total of that revenue?”
Example 2:
Original Question: “Which employees work in departments located in New York?” Subquestions:
1.“Which departments are located in New York?”
2.“Which employees work in those departments?”
Now, decompose the following question into subquestions. Provide the subquestions as a numbered list.
Original Question: {QUESTION}
Provide the subquestions in a json object without any explanation. Please respond with a JSON
object structured as follows:{{"Subquestions": list of subquestions.}}
Do not include “‘json in your response. Only output a json object as your response.

"""