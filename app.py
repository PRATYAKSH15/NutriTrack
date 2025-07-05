# # app.py
# import streamlit as st
# from PIL import Image
# from datetime import date
# from utils import generate_nutrition_report, generate_diet_plan, extract_macros
# from database import login_user, register_user, save_meal, get_meals_by_date
# from streamlit_echarts import st_echarts
# from utils import generate_pdf

# st.set_page_config(page_title="AI Nutritionist - Multi-user", layout="centered")

# # Session State for login
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
#     st.session_state.user_id = None
#     st.session_state.username = ""

# def login_ui():
#     st.title("🔐 Login to AI Nutritionist")
#     login_tab, register_tab = st.tabs(["Login", "Register"])

#     with login_tab:
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         if st.button("Login"):
#             user = login_user(username, password)
#             if user:
#                 st.session_state.logged_in = True
#                 st.session_state.user_id = user.id
#                 st.session_state.username = username
#                 st.success("✅ Logged in successfully!")
#                 st.rerun()
#             else:
#                 st.error("❌ Invalid credentials.")

#     with register_tab:
#         new_user = st.text_input("Choose Username", key="reg_user")
#         new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
#         if st.button("Register"):
#             if register_user(new_user, new_pass):
#                 st.success("🎉 Registration successful! You can now log in.")
#             else:
#                 st.warning("Username already exists.")

# if not st.session_state.logged_in:
#     login_ui()
#     st.stop()

# # ------------------------------
# # Main App
# # ------------------------------
# st.title(f"🥗 Welcome, {st.session_state.username}")
# st.caption("AI Nutritionist using Gemini 1.5 Flash with multi-user support")

# # Upload image
# uploaded_image = st.file_uploader("📤 Upload Food Image", type=["jpg", "jpeg", "png"])
# user_query = st.text_input("💬 Any dietary concerns or preferences? (optional)")

# if uploaded_image:
#     image = Image.open(uploaded_image)
#     st.image(image, caption="Uploaded Image", use_container_width=True)

#     if st.button("🔍 Analyze"):
#         with st.spinner("Analyzing with Gemini 1.5 Flash..."):
#             try:
#                 report = generate_nutrition_report(image, user_query)
#                 st.subheader("🧾 Nutrition Report")
#                 st.markdown(report)

#                 # Save to DB
#                 save_meal(uploaded_image.name, user_query, report, st.session_state.user_id)
#                 st.success("✅ Meal saved to your history!")
#             except Exception as e:
#                 st.error(f"❌ Error: {e}")

# # ------------------------------
# # Meal History
# # ------------------------------
# st.markdown("---")
# st.header("📅 Your Meal History by Date")

# selected_date = st.date_input("Pick a date", value=date.today())

# if st.button("📂 Show Meals"):
#     meals = get_meals_by_date(selected_date, st.session_state.user_id)
#     if not meals:
#         st.info("No meals found for this date.")
#     else:
#         for meal in meals:
#             st.markdown(f"#### 🕒 {meal.timestamp.strftime('%Y-%m-%d %H:%M')}")
#             st.markdown(f"**🖼 Image:** `{meal.image_name}`")
#             if meal.user_query:
#                 st.markdown(f"**💬 Query:** {meal.user_query}")
#             st.markdown("**🧾 Report:**")
#             st.markdown(meal.nutrition_report)
#             st.markdown("---")

# # ------------------------------
# # Personalized Diet Plan
# # ------------------------------
# st.markdown("---")
# st.header("🥗 Personalized Diet Plan Generator")

# with st.form("diet_form"):
#     age = st.number_input("Your Age", min_value=10, max_value=100)
#     gender = st.selectbox("Gender", ["Male", "Female", "Other"])
#     weight = st.number_input("Weight (kg)", min_value=30, max_value=200)
#     goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Weight Gain", "General Fitness"])
#     submitted = st.form_submit_button("🎯 Generate My Diet Plan")

# if submitted:
#     # ...inside the `if submitted:` block
#     with st.spinner("Generating AI diet plan..."):
#         profile = f"Age: {age}, Gender: {gender}, Weight: {weight}kg, Goal: {goal}"
#         try:
#             plan = generate_diet_plan(profile)
#             pdf_bytes = generate_pdf(plan)
#             st.download_button(
#             label="📥 Download Diet Plan (PDF)",
#             data=pdf_bytes,
#             file_name="diet_plan.pdf",
#             mime="application/pdf",
#             key="diet_pdf_download"  
# )
#             # # st.subheader("🧾 Your Personalized Diet Plan")
#             # # st.markdown(plan)
#             # # PDF Download
#             # pdf_bytes = generate_pdf(plan)
#             # st.download_button(
#             #     label="📥 Download Diet Plan (PDF)",
#             #     data=pdf_bytes,
#             #     file_name="diet_plan.pdf",
#             #     mime="application/pdf",
#             #     key="diet_pdf_download"  
#             # )

#         except Exception as e:
#             st.error(f"❌ Error generating plan: {e}")

# # ------------------------------
# # Logout
# # ------------------------------
# if st.button("🚪 Logout"):
#     st.session_state.logged_in = False
#     st.session_state.user_id = None
#     st.session_state.username = ""
#     st.rerun()

import streamlit as st
from PIL import Image
from datetime import date, datetime
import pytz

from utils import (
    generate_nutrition_report,
    generate_diet_plan,
    extract_macros,
    generate_pdf,
    get_indian_time,
)

from database import (
    login_user,
    register_user,
    save_meal,
    get_meals_by_date
)

from streamlit_echarts import st_echarts

# Page config
st.set_page_config(page_title="AI Nutritionist - Multi-user", layout="centered")

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""

# ----------------------------------------
# Login / Register UI
# ----------------------------------------

def login_ui():
    st.title("🔐 Login to AI Nutritionist")
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user.id
                st.session_state.username = username
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

    with register_tab:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("🎉 Registration successful! You can now log in.")
            else:
                st.warning("Username already exists.")

if not st.session_state.logged_in:
    login_ui()
    st.stop()

# ----------------------------------------
# Main App After Login
# ----------------------------------------

st.title(f"🥗 Welcome, {st.session_state.username}")
st.caption("AI Nutritionist using Gemini 1.5 Flash with multi-user support")

# Upload image for nutrition analysis
uploaded_image = st.file_uploader("📤 Upload Food Image", type=["jpg", "jpeg", "png"])
user_query = st.text_input("💬 Any dietary concerns or preferences? (optional)")

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Analyze"):
        with st.spinner("Analyzing with Gemini 1.5 Flash..."):
            try:
                report = generate_nutrition_report(image, user_query)
                st.subheader("🧾 Nutrition Report")
                st.markdown(report)

                # Save meal with Indian timestamp
                save_meal(uploaded_image.name, user_query, report, st.session_state.user_id)
                st.success("✅ Meal saved to your history!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ----------------------------------------
# Meal History by Date (with Indian Time)
# ----------------------------------------

st.markdown("---")
st.header("📅 Your Meal History by Date")

selected_date = st.date_input("Pick a date", value=date.today())

if st.button("📂 Show Meals"):
    meals = get_meals_by_date(selected_date, st.session_state.user_id)
    if not meals:
        st.info("No meals found for this date.")
    else:
        india = pytz.timezone("Asia/Kolkata")
        for meal in meals:
            ist_time = meal.timestamp.astimezone(india).strftime("%Y-%m-%d %I:%M %p IST")
            st.markdown(f"#### 🕒 {ist_time}")
            st.markdown(f"**🖼 Image:** `{meal.image_name}`")
            if meal.user_query:
                st.markdown(f"**💬 Query:** {meal.user_query}")
            st.markdown("**🧾 Report:**")
            st.markdown(meal.nutrition_report)
            st.markdown("---")

# ----------------------------------------
# Diet Plan Generator + PDF
# ----------------------------------------

st.markdown("---")
st.header("🥗 Personalized Diet Plan Generator")

with st.form("diet_form"):
    age = st.number_input("Your Age", min_value=10, max_value=100)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    weight = st.number_input("Weight (kg)", min_value=30, max_value=200)
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Weight Gain", "General Fitness"])
    submitted = st.form_submit_button("🎯 Generate My Diet Plan")

if submitted:
    with st.spinner("Generating AI diet plan..."):
        profile = f"Age: {age}, Gender: {gender}, Weight: {weight}kg, Goal: {goal}"
        try:
            plan = generate_diet_plan(profile)
            st.subheader("🧾 Your Personalized Diet Plan")
            st.markdown(plan)

            macros = extract_macros(plan)
            st.subheader("🍽 Macronutrient Breakdown")
            chart_data = {
                "tooltip": {"trigger": "item"},
                "legend": {"top": "5%", "left": "center"},
                "series": [
                    {
                        "name": "Macros",
                        "type": "pie",
                        "radius": ["40%", "70%"],
                        "avoidLabelOverlap": False,
                        "label": {"show": False, "position": "center"},
                        "emphasis": {"label": {"show": True, "fontSize": "18", "fontWeight": "bold"}},
                        "labelLine": {"show": False},
                        "data": [
                            {"value": macros["Carbs"], "name": "Carbs"},
                            {"value": macros["Proteins"], "name": "Proteins"},
                            {"value": macros["Fats"], "name": "Fats"},
                        ],
                    }
                ],
            }
            st_echarts(options=chart_data, height="400px")

            # ✅ Generate PDF
            pdf_bytes = generate_pdf(plan)
            st.download_button(
                label="📥 Download Diet Plan (PDF)",
                data=pdf_bytes,
                file_name=f"diet_plan_{get_indian_time()}.pdf",
                mime="application/pdf",
                key="diet_pdf_download"
            )

        except Exception as e:
            st.error(f"❌ Error generating plan: {e}")

# ----------------------------------------
# Logout
# ----------------------------------------

if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.rerun()
