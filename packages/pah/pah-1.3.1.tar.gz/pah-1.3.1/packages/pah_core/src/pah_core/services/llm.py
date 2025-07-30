import json
from pydantic import BaseModel, Field

from pah_core.models import Highlight


class HighlightResponse(BaseModel):
    highlights: list[Highlight] = Field(
        ...,
        description="List of highlights",
    )


SYSTEM_PROMPT = """
You are an AI assistant that highlights text in a PDF document based on a given prompt.
You will be given the text of each page of a PDF document and a prompt. Your task is to identify the relevant sections of the text that answer the prompt and return them as highlights.
You MUST return a list of highlights, each with the following fields:
    - `page`: The page number where the highlight is located.
        - You MUST start counting from 0.
    - `text`: The text that should be highlighted.
        - You MUST preserve the original formatting of the text (e.g. typos, newlines, spaces, unicodes, etc.).
        - You NEVER dehyphenate any hyphenated words.
    - `reason`: A brief explanation of why this text is relevant to the prompt.
    - `color`: The color of the highlight. If you are unsure, use "yellow".
"""


def get_highlights(
    model: str,
    prompt: str,
    page_texts: list[str],
    api_key: str | None = None,
) -> list[Highlight]:
    from litellm.main import completion
    from litellm.types.utils import Choices, ModelResponse

    input_prompt = f"""Here is the text of each page of the PDF document:
```json
{json.dumps(page_texts, indent=2, ensure_ascii=False)}
```
"""

    response = completion(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that highlights text in a PDF document based on a given prompt.",
            },
            {"role": "user", "content": prompt},
            {
                "role": "user",
                "content": input_prompt,
            },
        ],
        stream=False,
        response_format=HighlightResponse,
        api_key=api_key,
    )
    assert isinstance(response, ModelResponse), "Response is not a HighlightResponse"
    choice = response.choices[0]
    assert isinstance(choice, Choices), "Choice is not a HighlightResponse"
    content = choice.message.content
    assert isinstance(content, str), "Content is not a string"

    highlights = HighlightResponse.model_validate_json(content).highlights
    return highlights
