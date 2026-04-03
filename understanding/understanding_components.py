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
            "content": "You analyze questions intended for SQL queries. "
                       "If the question is clear and unambiguous, return an empty string. "
                       "If the question is ambiguous, briefly explain why and list possible interpretations. "
                       "Do not repeat the question. Do not add any extra text. "
                       "Always answer in German."
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
    outputs = model.generate(**inputs, max_new_tokens=2000,
    temperature=0.2,
    do_sample=False)
    generated_tokens = outputs[0][inputs.shape[-1]:]
    result = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    print(f"res answer {result}")
    return result.strip()


def check_ambiguity_in_question_prompt(question: str) -> str:
    return f"""
Analyze the following question in the context of generating a SQL query.

If the question is clear and unambiguous, return an empty string.

If the question is ambiguous, ask clarifying questions and describe the possible interpretations that would affect the SQL query.

Your answer will only be in german.

Question: {question}
"""
