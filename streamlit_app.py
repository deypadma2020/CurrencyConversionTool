import streamlit as st
import json
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from langchain_core.tools import tool, InjectedToolArg
from typing import Annotated
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# --- Tools ---
@tool
def get_conversion_factor(base_currency: str, target_currency: str) -> float:
    """
    Fetch the currency conversion factor between a base currency and a target currency.
    """
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}"
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

# Bind tools to LLM
llm = ChatGroq(model="llama3-70b-8192", temperature=0)
llm_with_tools = llm.bind_tools([get_conversion_factor, converter])

# --- Currency List for Dropdown ---
currency_options = [
    "USD", "EUR", "GBP", "INR", "JPY", "CAD", "AUD", "CHF", "CNY", "SGD", "HKD", "NZD",
    "SEK", "NOK", "ZAR", "MXN", "BRL", "RUB", "KRW", "AED"
]

# --- Streamlit UI ---
st.set_page_config(page_title="Currency Converter AI", layout="centered")
st.title("💱 Currency Converter using Groq + LangChain")

base_currency = st.selectbox("Select Base Currency:", currency_options, index=currency_options.index("INR"))
target_currency = st.selectbox("Select Target Currency:", currency_options, index=currency_options.index("USD"))
amount = st.number_input("Amount to Convert:", min_value=0.01, step=1.0, value=10.0)

if st.button("Convert"):
    if base_currency == target_currency:
        st.warning("Base and Target currencies cannot be the same.")
    else:
        with st.spinner("Thinking..."):
            messages = [
                HumanMessage(
                    content=f"Please fetch the conversion rate between {base_currency} and {target_currency}, and then convert {amount} {base_currency} to {target_currency}."
                )
            ]
            conversion_rate = None

            while True:
                ai_message = llm_with_tools.invoke(messages)
                messages.append(ai_message)

                if ai_message.content.strip():
                    st.success("✅ Conversion Complete")
                    st.markdown(f"**{ai_message.content}**")
                    break

                for tool_call in ai_message.tool_calls:
                    if tool_call["name"] == "get_conversion_factor":
                        tool_response = get_conversion_factor.invoke(tool_call["args"])
                        conversion_rate = tool_response.get("conversion_rate")

                        if not conversion_rate:
                            st.error(f"❌ API Error: {tool_response}")
                            break

                        messages.append(
                            ToolMessage(tool_call_id=tool_call["id"], content=json.dumps(tool_response))
                        )

                    elif tool_call["name"] == "converter":
                        tool_args = dict(tool_call["args"])
                        if "conversion_rate" not in tool_args and conversion_rate:
                            tool_args["conversion_rate"] = conversion_rate
                        tool_response = converter.invoke(tool_args)
                        messages.append(
                            ToolMessage(tool_call_id=tool_call["id"], content=json.dumps(tool_response))
                        )
