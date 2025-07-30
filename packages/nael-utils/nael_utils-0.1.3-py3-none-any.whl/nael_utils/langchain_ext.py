import os
from typing import Dict, Optional, Type, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, SecretStr
from langchain_openai.chat_models import ChatOpenAI


def call_gpt_with_prompt_model(
    api_key: str | None,
    prompt: str,
    pydantic_object: Optional[Type[BaseModel]],
    model: str = "gpt-4.1",
) -> Dict:
    """
    Generic function to ask for GPT's inference. Return value will be in pydantic_object
    :param api_key:
    :param prompt:
    :param pydantic_object:
    :return:
    """
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("OPENAI_API_KEY is not set")
    
    chat = ChatOpenAI(model=model, api_key=SecretStr(api_key))
    parser = JsonOutputParser(pydantic_object=pydantic_object)
    format_instructions = parser.get_format_instructions()
    _prompt = f"Answer the user query.\n{format_instructions}\n{prompt}\n"
    messages = [
        HumanMessage(
            content=[
                {"type": "text", "text": _prompt},
            ]
        )
    ]

    text_result = chat.invoke(messages)
    return parser.invoke(text_result)

T = TypeVar('T', bound=BaseModel)

def call_gpt(
    prompt: str,
    format_model: Type[T],
    model: str = "gpt-4.1",
    system_prompt: str = "",
    additional_messages: list[HumanMessage | SystemMessage] = [],
) -> T:
    """
    Generic function to ask for GPT's inference. Return value will be in pydantic_object
    :param prompt:
    :param format_model:
    :param model:
    :return:
    """

    api_key = os.getenv("OPENAI_API_KEY", None)
    if api_key is None:
        raise ValueError("OPENAI_API_KEY is not set")
    
    chat = ChatOpenAI(model=model, api_key=SecretStr(api_key))
    parser = JsonOutputParser(pydantic_object=format_model)
    format_instructions = parser.get_format_instructions()
    _prompt = f"Answer the user query.\n{format_instructions}\n{prompt}\n"
    messages: list[HumanMessage | SystemMessage] = [
        HumanMessage(
            content=[
                {"type": "text", "text": _prompt},
            ]
        ),
        *additional_messages,
    ]

    if system_prompt:
        messages = [
            SystemMessage(content=system_prompt),
            *messages,
        ]

    text_result = chat.invoke(messages)
    result = parser.invoke(text_result)

    return format_model.model_validate(result)