from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
model_name = "mistralai/Mistral-7B-Instruct-v0.2"

print("Lade Modell einmal...")

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16
).to("cuda")

def check_ambiguity_in_question(question: str):
    prompt = check_ambiguity_in_question_prompt(question)

    messages = [
        {
            "role": "system",
            "content": "You are an expert at identifying ambiguity in questions that are intended to be translated into SQL queries. "
            "If the question is unambiguous, return an empty string. "
            "If the question is ambiguous, clearly explain what makes it ambiguous and list possible interpretations of the question."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt"
    ).to("cuda")
    outputs = model.generate(**inputs)

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "[/INST]" in result:
        result = result[result.index("[/INST]") + len("[/INST]"):]

    return result.strip()



def check_ambiguity_in_question_prompt(question: str) -> str:
    return f"""
Analyze the following question in the context of generating a SQL query.

If the question is clear and unambiguous, return an empty string.

If the question is ambiguous, ask clarifying questions and describe the possible interpretations that would affect the SQL query.

Question: {question}
"""