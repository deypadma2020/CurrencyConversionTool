import streamlit as st
from langchain_core.tools import tool, InjectedToolArg
from typing import Annotated
import requests
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# --- Tools ---
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

# --- Setup LLM + tools ---
llm = ChatGroq(model="llama3-70b-8192", temperature=0)
llm_with_tools = llm.bind_tools([get_conversion_factor, converter])


# --- Streamlit App ---
st.set_page_config(page_title="Currency Converter with LangChain + Groq", page_icon="💱")

st.title("💱 Currency Converter (LangChain + Groq)")

# Input fields
base_currency = st.text_input("Base Currency (e.g. INR)", "INR")
target_currency = st.text_input("Target Currency (e.g. USD)", "USD")
amount = st.number_input("Amount to Convert", min_value=0.0, value=10.0, step=1.0)

if st.button("Convert"):
    with st.spinner("Fetching conversion rate and calculating..."):
        messages = [
            HumanMessage(content=f"Please fetch the conversion rate between {base_currency} and {target_currency}, "
                                 f"and then convert {amount} {base_currency} to {target_currency} using that rate.")
        ]

        conversion_rate = None
        result = None

        while True:
            ai_message = llm_with_tools.invoke(messages)
            messages.append(ai_message)

            if ai_message.content.strip():
                result = ai_message.content
                break

            for tool_call in ai_message.tool_calls:
                if tool_call['name'] == 'get_conversion_factor':
                    tool_response = get_conversion_factor.invoke(tool_call['args'])
                    conversion_rate = tool_response['conversion_rate']
                    messages.append(
                        ToolMessage(tool_call_id=tool_call['id'], content=json.dumps(tool_response))
                    )

                elif tool_call['name'] == 'converter':
                    tool_args = dict(tool_call['args'])
                    if 'conversion_rate' not in tool_args and conversion_rate:
                        tool_args['conversion_rate'] = conversion_rate
                    tool_response = converter.invoke(tool_args)
                    messages.append(
                        ToolMessage(tool_call_id=tool_call['id'], content=json.dumps(tool_response))
                    )

        st.success("✅ Conversion Completed")
        st.write(result)
