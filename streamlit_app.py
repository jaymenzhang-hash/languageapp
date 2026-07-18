import streamlit as st
import json
from openai import OpenAI
import base64

def get_base64(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

img = get_base64("images/food.jpg")

page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpg;base64,{img}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)
client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
if "screen" not in st.session_state:
    st.session_state["screen"] = "start"
if st.session_state["screen"] == "start":
    st.markdown(
        "<h1 style = 'color: #407ee3; "
        "'>Calorie Tracker</h1>",
        unsafe_allow_html=True )
    st.session_state["daily_goal"] = st.text_input("Enter your daily calorie goal:")
    if st.button("Start"):
        st.session_state["screen"] = "Today's Nutrients"
        st.rerun()
if st.session_state["screen"] == "Today's Nutrients":
    st.markdown(
    "<h1 style = 'color: #FFFFFF; "
    "'>Today's Calories</h1>",
    unsafe_allow_html=True )
    if "listofFoods" not in st.session_state:
        st.session_state["listofFoods"] = {}
    if "quantity" not in st.session_state:
        st.session_state["quantity"] = ""        
    if "food" not in st.session_state:
        st.session_state["food"] = ""
    st.session_state["food"] = st.text_input("Which food did you eat?")
    st.session_state["quantity"] = st.text_input("How much of it did you eat?")
    if st.button("Add a food"):
        st.session_state["listofFoods"][st.session_state["food"]] = st.session_state["quantity"]
        for key, value in st.session_state["listofFoods"].items():
            st.write("Food: " + str(key) + ", Quantity:", value)
    if len(st.session_state["listofFoods"]) != 0:
            if st.button("Submit"):
                st.session_state["screen"] = "result"
                st.rerun()
if st.session_state["screen"] == "result":
        system_prompt = """You are managing a calorie tracker app for the user.
    The user will input which foods they eat and how much of it they ate. They will also input
    a daily calorie goal that they should not exceed or go under by 500. Figure out the nutrient value and calories in the food and log it. Respond in
    a format like: Calories: 
                   Protein:
                   Fiber:
                   Fat:
                   Sugar: , etc. and at the end, tell the user how close they are to reaching the calorie goal. Do not show your calculations
                   Give the nutrition information for each added food before telling the user the total intake.
                   if they mention anything extremely unhealthy, be sure to remind them and give them better food options."""

        user_prompt = "My goal is to maintain an average of " + str(st.session_state["daily_goal"]) + " calories. Today, I ate " + str(st.session_state["listofFoods"]) + ". "

        response = client.chat.completions.create(
            model = "gpt-4o",
            messages =[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        st.write(response.choices[0].message.content)
        if "meal_image" not in st.session_state:         
            image = client.images.generate(
                model = "gpt-image-1",
                prompt ="Create a realistic, cooked(if applicable) image of " +
                str(st.session_state["listofFoods"])
            )
            image_base64 = image.data[0].b64_json
            st.session_state["meal_image"] = base64.b64decode(image_base64)
            st.image(st.session_state["meal_image"])
        if st.button("Add another food"):
             st.session_state["screen"] = "Today's Nutrients"
             st.session_state.pop("meal_image")
             st.rerun()
        if st.button("New day"):
             st.session_state["screen"] = "start"
             st.session_state.pop("meal_image")
             st.session_state["listofFoods"].clear()
             st.rerun()
            
        

            
        
        


        
