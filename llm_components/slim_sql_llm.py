from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "llmware/slim-sql-1b-v0"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32
)