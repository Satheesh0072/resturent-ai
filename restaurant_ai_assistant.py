import streamlit as st
import pandas as pd
from streamlit_chat import message

# Load and clean Excel data
@st.cache_data
def load_data():
    df = pd.read_excel("Restaurant_Google sheet001.xlsx", sheet_name="Sheet1", skiprows=3)
    df = df.dropna(subset=["Dish"])
    df.columns = df.columns.map(str)
    df["Weekly Orders"] = pd.to_numeric(df["Weekly Orders"], errors='coerce')
    df["Waste in cost"] = pd.to_numeric(df["Waste in cost"], errors='coerce')
    df["Dish Profit Margin ₹"] = pd.to_numeric(df["Dish Profit Margin ₹"], errors='coerce')
    return df

df = load_data()

# Combined title
st.title("🍽️ Smart Menu Optimization Assistant with AI Chatbot 🤖")

# ------------------- STATIC MENU ANALYSIS SECTION -------------------

st.header("1️⃣ Dishes to Remove (Low-Selling & High Waste)")
remove_dishes = df[(df["Weekly Orders"] < 5) & (df["Waste in cost"] > 100)]
st.dataframe(remove_dishes[["Dish", "Weekly Orders", "Waste in cost", "Keep/Remove"]])

st.header("2️⃣ Most Wasted Ingredients")
waste_by_ingredient = df[["Dish", "Ingredients", "Waste in cost"]].sort_values(by="Waste in cost", ascending=False)
st.dataframe(waste_by_ingredient)

st.header("3️⃣ Suggested Dish Ideas Using High-Waste Ingredients")
suggestions = df[df["Waste in cost"] > 100][["Dish", "Ingredients", "Waste in cost", "Suggested Dishes"]]
st.dataframe(suggestions)

st.header("4️⃣ High Margin Dishes with Overlapping Ingredients")
margin_threshold = st.slider("Set minimum profit margin:", 50, 200, 100)
high_margin_dishes = df[df["Dish Profit Margin ₹"] >= margin_threshold]
st.dataframe(high_margin_dishes[["Dish", "Ingredients", "Dish Profit Margin ₹"]])

st.header("5️⃣ Most Wasted Ingredient")
max_waste_row = df.loc[df["Waste in cost"].idxmax()]
st.success(f"🥇 Most wasted: {max_waste_row['Ingredients']} costing ₹{max_waste_row['Waste in cost']}")

st.header("6️⃣ Suggest Dish Using Existing Ingredients")
all_ingredients = ", ".join(df["Ingredients"].dropna().tolist())
st.text_area("Available Ingredients (auto-filled)", value=all_ingredients, height=100)

st.header("7️⃣ Candidates for Removal")
st.dataframe(remove_dishes[["Dish", "Weekly Orders", "Waste in cost", "Keep/Remove"]])

st.header("8️⃣ Suggestions to Reduce Stock Next Week")
to_stock_less = df[df["Weekly Orders"] < 5][["Dish", "Ingredients", "Weekly Orders"]]
st.dataframe(to_stock_less)

st.download_button(
    "📥 Download Cleaned Data",
    data=df.to_csv(index=False),
    file_name="optimized_menu_data.csv",
    key="download_button_static"  # ✅ unique key to avoid error
)

# ------------------- AI CHATBOT SECTION -------------------

st.header("🤖 Chat with AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=msg["is_user"], key=f"msg_{i}")

# Chat input box
prompt = st.chat_input("Ask me anything about your menu...")

def chatbot_response(user_input):
    user_input = user_input.lower()
    if "remove" in user_input or "low-selling" in user_input:
        result = df[(df["Weekly Orders"] < 5) & (df["Waste in cost"] > 100)][["Dish", "Weekly Orders", "Waste in cost"]]
        return f"You can consider removing: {', '.join(result['Dish'])}"
    elif "most wasted" in user_input or "waste" in user_input:
        max_row = df.loc[df["Waste in cost"].idxmax()]
        return f"The most wasted ingredient is in **{max_row['Dish']}** using **{max_row['Ingredients']}** costing ₹{max_row['Waste in cost']}."
    elif "high margin" in user_input:
        result = df[df["Dish Profit Margin ₹"] >= 100]
        return f"High margin dishes are: {', '.join(result['Dish'])}"
    elif "suggest" in user_input or "create" in user_input:
        result = df[df["Waste in cost"] > 100][["Dish", "Suggested Dishes"]]
        return "Suggested rework dishes:\n" + "\n".join([f"{row['Dish']} ➝ {row['Suggested Dishes']}" for _, row in result.iterrows()])
    else:
        return "Try asking: *Which dish is most wasted?*, *What should I remove?*, or *Give me high margin dishes.*"

if prompt:
    st.session_state.messages.append({"content": prompt, "is_user": True})
    reply = chatbot_response(prompt)
    st.session_state.messages.append({"content": reply, "is_user": False})
    message(prompt, is_user=True)
    message(reply, is_user=False)

# Dataset viewer
with st.expander("📊 Full Dataset"):
    st.dataframe(df)

st.download_button(
    "📥 Download Chat-Enhanced Dataset",
    data=df.to_csv(index=False),
    file_name="menu_with_chat.csv",
    key="download_button_chat"  # ✅ another unique key
)
