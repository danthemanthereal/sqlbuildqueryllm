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
    pass


def check_ambiguity_in_question_prompt(question: str)->str:
    return f"""


"""