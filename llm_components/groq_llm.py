from groq import Groq
API_KEY= "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"
MODEL = "llama-3.1-8b-instant"
def get_model():
    llm = Groq(api_key=API_KEY)
    return llm

def get_response(model, prompt):
    llm = get_model()
    return llm.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    ).choices[0].message.content


def get_prompt():
    pass