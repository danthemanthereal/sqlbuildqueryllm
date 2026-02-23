from llm_components.groq.prompt_get_whole_schema import with_c3_prompt

api_key_1 = "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"
api_key_2 = "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"
api_key_3 = "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"
api_key_4 = "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"
api_key_5 = "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"

api_keys = [api_key_1, api_key_2, api_key_3, api_key_4, api_key_5]
from groq import Groq
model_name = "groq/compound"

def get_api_key(index: int) -> str:
    return api_keys[index % len(api_keys)]


def get_tables_groq(question: str, index ) -> str:
    prompt = with_c3_prompt(question)
    api_key = get_api_key(index)

    client = Groq(
        api_key=
        api_key
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model_name,
    )

    return chat_completion.choices[0].message.content



def get_action_in_auto_link_groq(question: str, prompt: str ) -> str:

    api_key = get_api_key(0)

    client = Groq(
        api_key=
        api_key
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model_name,
    )

    return chat_completion.choices[0].message.content