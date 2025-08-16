````markdown
# 💱 Currency Converter with LangChain + Groq

This project is a **currency conversion assistant** powered by [LangChain](https://www.langchain.com/), [Groq LLM](https://groq.com/), and [Streamlit](https://streamlit.io/).  
It demonstrates how to integrate tools (API calls + custom functions) with an LLM to fetch live exchange rates and perform currency conversion interactively.

---

## 🚀 Features
- Fetches live currency conversion rates using [ExchangeRate API](https://www.exchangerate-api.com/).  
- Uses **LangChain tool binding** to let the LLM decide when to call APIs.  
- Convert any base currency (e.g., INR) to any target currency (e.g., USD).  
- Provides a **Streamlit web UI** for ease of use.  
- Can also be run **directly from the terminal**.

---

## 📦 Installation

1. Clone this repository or copy the code:
   ```bash
   git clone https://github.com/your-username/currency-converter-langchain.git
   cd currency-converter-langchain
````

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your Groq API key:

   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

---

## 🖥️ Usage

### Run via Streamlit UI

Start the web application:

```bash
streamlit run app.py
```

Open the link shown in your terminal (default: [http://localhost:8501](http://localhost:8501)).
You’ll see an interface like this:

1. Enter **base currency** (e.g., `INR`).
2. Enter **target currency** (e.g., `USD`).
3. Enter the **amount** (e.g., `10`).
4. Click **Convert**.
5. The app will fetch the conversion rate via API → ask Groq to call the converter tool → and display the converted value.

---

### Run via Terminal

If you want to run the conversion without UI, you can directly execute the script with Python:

```bash
python app.py
```

Since `app.py` is built with Streamlit, running directly will just launch the UI in the browser.
To test tool usage in terminal only, you can create a small script `cli.py` like this:

```python
from app import get_conversion_factor, converter

if __name__ == "__main__":
    base_currency = "INR"
    target_currency = "USD"
    amount = 10

    # Get conversion rate
    rate = get_conversion_factor.invoke({"base_currency": base_currency, "target_currency": target_currency})
    conversion_rate = rate["conversion_rate"]

    # Convert
    converted = converter.invoke({"base_currency_value": amount, "conversion_rate": conversion_rate})
    print(f"{amount} {base_currency} = {converted:.2f} {target_currency}")
```

Run:

```bash
python cli.py
```

---

## 📂 Project Structure

```
currency-converter/
│── app.py          # Streamlit application (UI + LangChain tools)
│── cli.py          # Simple terminal script (optional)
│── .env            # Environment variables (Groq API key)
│── requirements.txt# Dependencies
│── README.md       # Documentation
```

---

## 🛠️ Tech Stack

* **Python 3.9+**
* **LangChain** (tool orchestration)
* **Groq LLM** (LLM backend)
* **ExchangeRate API** (live FX rates)
* **Streamlit** (UI)
* **dotenv** (environment management)

---

## ✅ Example

From UI:

```
Input: 10 INR → USD
Output: 10 INR = 0.12 USD
```

From Terminal:

```
10 INR = 0.12 USD
```

---

## 📜 License

MIT License – feel free to modify and use this project.
