import streamlit as st
import pyodbc
from google import genai

# 1. Establish database connection
def get_db_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=New_T2D_treatment_data;"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

# 2. Function to generate lifestyle advice using a free AI model API
def get_ai_lifestyle_advice(age, bmi, sugar, duration, complications):
    try:
        # Initialize client (uses GEMINI_API_KEY environment variable, or paste your raw key string)
        client = genai.Client(api_key="AQ.Ab8RN6J9oBMHxk4I9ccg6BnQUXH1KvskI3tDtf7YIDSFxdvX4g")
        
        # Build a highly contextual prompt based on UI selections
        prompt = f"""
        You are an expert clinical endocrinologist and diabetes dietician. 
        Provide a concise, practical, bulleted list of dietary and exercise modifications 
        IN HINDI LANGUAGE (using clean Devanagari script) for a Type 2 Diabetes patient 
        with the following active profiles:
        - Age Group: {age}
        - BMI Category: {bmi}
        - Fasting Blood Sugar Range: {sugar}
        - History Duration: {duration}
        - Complications Present: {complications}      
        Keep the tone highly professional, realistic for Indian patients, and structure it into two distinct headings:
        🥗 व्यक्तिगत पोषण लक्ष्य (Personalized Nutritional Targets)
        🏃‍♂️ शारीरिक गतिविधि दिशानिर्देश (Tailored Physical Activity Guidelines)
        
        Do not include English translations for the bullet points. Write purely in clear medical Hindi. Do not add general intro or outro fluff."""
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Could not generate AI advice layout: Ensure your API credentials are set up. Details: {str(e)}"

# 3. Streamlit Page Setup
st.set_page_config(page_title="T2D Recommendation System", page_icon="🩺", layout="centered")
st.title("🩺 Type 2 Diabetes Treatment Selector")
st.write("Select patient metrics below to look up drug recommendations and AI-generated lifestyle protocols.")

# Metric Dictionaries
age_display = {"15-20 years": 1, "21-30 years": 2, "31-40 years": 3, "41-65 years": 4, "66-75 years": 5, "1-14 years": 6, "75-100 years": 7}
bmi_display = {"17-23": 1, "24-25": 2, "26-28": 3, "29-32": 4, "33-45": 5}
su_display = {"100-125 mg/dl": 1, "126-140 mg/dl": 2, "141-160 mg/dl": 3, "161-200 mg/dl": 4, "201-300 mg/dl": 5, "Above 300 mg/dl": 6}
duration_display = {"Less than 5 years": 1, "6 or more than 6 years": 2}
comp_display = {"No Complications": 0, "Mild Complications": 1}

# UI Layout Grid
col1, col2 = st.columns(2)
with col1:
    age_sel = st.selectbox("Patient Age Group", list(age_display.keys()))
    bmi_sel = st.selectbox("BMI Range", list(bmi_display.keys()))
    duration_sel = st.selectbox("Disease Duration", list(duration_display.keys()))
with col2:
    su_sel = st.selectbox("Fasting Blood Sugar", list(su_display.keys()))
    comp_sel = st.selectbox("Complications Status", list(comp_display.keys()))

st.markdown("---")

if st.button("🔍 Get Recommended Treatment Plan", type="primary"):
    # First: Run the SQL Database lookup
    with st.spinner("Querying database stored procedure..."):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            args = (age_display[age_sel], bmi_display[bmi_sel], su_display[su_sel], comp_display[comp_sel], duration_display[duration_sel], 0, 0)
            cursor.execute("{CALL GetRecommendedDrugs (?, ?, ?, ?, ?, ?, ?)}", args)
            rows = cursor.fetchall()
            
            if rows:
                st.subheader("📋 Treatment Protocol Order")
                for row in rows:
                    st.write(f"**{row[0]}.** {row[1]}")
            else:
                st.warning("No standard drug protocol match found in database rules.")
            conn.close()
        except Exception as e:
            st.error(f"Database Error: {str(e)}")
            
    st.markdown("---")
    
    # Second: Run the Live AI Guidance Engine
    # Second: Run the Live AI Guidance Engine
    with st.spinner("AI Engine generating customized diet & exercise charts..."):
        ai_advice = get_ai_lifestyle_advice(age_sel, bmi_sel, su_sel, duration_sel, comp_sel)
        st.subheader("🤖 Lifestyle Prescription")
        st.info(ai_advice)
        st.caption("It's an AI Generated advice, consult your Doctor for any clarification")