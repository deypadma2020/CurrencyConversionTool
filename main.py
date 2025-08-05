from langchain_core.tools import tool, InjectedToolArg
from typing import Annotated
import requests
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

@tool
def get_conversion_factor(base_currency: str, target_currency: str) -> float:
    """
    Fetch the currency conversion factor between a base currency and a target currency.
    """
    url = f"https://v6.exchangerate-api.com/v6/06ff5a588198d533c805437e/pair/{base_currency}/{target_currency}"
    response = requests.get(url)
    return response.json()

@tool
def converter(
    base_currency_value: float,
    conversion_rate: Annotated[float, InjectedToolArg]
) -> float:
    """
    Convert a base currency value to the target currency using the conversion rate.
    """
    return base_currency_value * conversion_rate

# Setup LLM and tools
llm = ChatGroq(model="llama3-70b-8192", temperature=0)
llm_with_tools = llm.bind_tools([get_conversion_factor, converter])

# Initial prompt
messages = [HumanMessage(content='Please fetch the conversion rate between INR and USD, and then convert 10 INR to USD using that rate.')]

# Loop until we get final answer
conversion_rate = None

while True:
    ai_message = llm_with_tools.invoke(messages)
    messages.append(ai_message)

    # If final answer is present, break
    if ai_message.content.strip():
        print("== Final Answer ==")
        print(ai_message.content)
        break

    # If more tools to call
    for tool_call in ai_message.tool_calls:
        if tool_call['name'] == 'get_conversion_factor':
            tool_response = get_conversion_factor.invoke(tool_call['args'])
            conversion_rate = tool_response['conversion_rate']
            messages.append(ToolMessage(tool_call_id=tool_call['id'], content=json.dumps(tool_response)))

        elif tool_call['name'] == 'converter':
            tool_args = dict(tool_call['args'])
            # In case the model didn't inject conversion_rate
            if 'conversion_rate' not in tool_args and conversion_rate:
                tool_args['conversion_rate'] = conversion_rate
            tool_response = converter.invoke(tool_args)
            messages.append(ToolMessage(tool_call_id=tool_call['id'], content=json.dumps(tool_response)))
