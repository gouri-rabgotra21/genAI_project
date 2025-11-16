import streamlit as st
import ollama
import json
import re

# --- Step 1: Nutrition "Tool" (The backend logic) ---
# We keep this function in the same file for simplicity.
def get_nutrition_data(ingredient_name: str, quantity_grams: int) -> str:
    """
    Gets nutritional data for a given ingredient and quantity.
    This is our MOCK function.
    """
    # --- This is the MOCK DATA ---
    mock_database = {
        "paneer": {"calories_per_100g": 265, "protein_per_100g": 18, "fat_per_100g": 20, "carbs_per_100g": 3},
        "spinach": {"calories_per_100g": 23, "protein_per_100g": 2.9, "fat_per_100g": 0.4, "carbs_per_100g": 3.6},
        "onion": {"calories_per_100g": 40, "protein_per_100g": 1.1, "fat_per_100g": 0.1, "carbs_per_100g": 9.3},
        "tomato": {"calories_per_100g": 18, "protein_per_100g": 0.9, "fat_per_100g": 0.2, "carbs_per_100g": 3.9},
        "butter": {"calories_per_100g": 717, "protein_per_100g": 0.9, "fat_per_100g": 81, "carbs_per_100g": 0.1},
        "garlic": {"calories_per_100g": 149, "protein_per_100g": 6.4, "fat_per_100g": 0.5, "carbs_per_100g": 33},
        "ginger": {"calories_per_100g": 80, "protein_per_100g": 1.8, "fat_per_100g": 0.8, "carbs_per_100g": 18},
        "oil": {"calories_per_100g": 884, "protein_per_100g": 0, "fat_per_100g": 100, "carbs_per_100g": 0},
    }
    
    ingredient_key = ingredient_name.lower()
    if "ghee" in ingredient_key or "vegetable oil" in ingredient_key:
        ingredient_key = "oil"
    if "tomatoes" in ingredient_key:
        ingredient_key = "tomato"
    
    if ingredient_key in mock_database:
        data = mock_database[ingredient_key]
        factor = quantity_grams / 100.0
        nutrition_result = {
            "ingredient": ingredient_key,
            "quantity_grams": quantity_grams,
            "calories": round(data["calories_per_100g"] * factor),
            "protein": round(data["protein_per_100g"] * factor, 2),
            "fat": round(data["protein_per_100g"] * factor, 2),
            "carbs": round(data["carbs_per_100g"] * factor, 2)
        }
        return json.dumps(nutrition_result)
    else:
        print(f"--- [Tool Warning] Ingredient not in mock DB: {ingredient_name} ---")
        return json.dumps({"error": "Ingredient not found in mock database"})

# --- Step 2: Main Function to Get Recipe (Refactored) ---
def generate_recipe_and_nutrition(user_ingredients):
    """
    This function contains the core logic from app.py.
    It takes ingredients, calls Ollama, and returns the recipe and nutrition.
    """
    
    # Connect to the local Ollama client
    client = ollama.Client()
    
    user_prompt = f"""
    You are a recipe and nutrition assistant.
    Your task is to generate a recipe using the following ingredients: {user_ingredients}.

    You MUST follow this two-part format:
    PART 1: A JSON list of all ingredients used in the recipe and their quantities in grams.
    This JSON block MUST start with the exact tag `[JSON-START]` and end with the exact tag `[JSON-END]`.
    The JSON must be an array of objects, where each object has two keys: "ingredient_name" (string) and "quantity_grams" (integer).
    Example:
    [JSON-START]
    [
      {{"ingredient_name": "paneer", "quantity_grams": 200}},
      {{"ingredient_name": "spinach", "quantity_grams": 300}}
    ]
    [JSON-END]

    PART 2: The full recipe, including a title, a short description, and the step-by-step cooking instructions.

    Generate your response now.
    """

    messages = [{'role': 'user', 'content': user_prompt}]
    
    try:
        # Call the model
        response = client.chat(model='llama3', messages=messages)
        response_text = response['message']['content']
        
        # --- Parse the Response ---
        json_match = re.search(r'\[JSON-START\](.*)\[JSON-END\]', response_text, re.DOTALL)
        
        if not json_match:
            return None, "Error: AI did not return a valid JSON block. Try again."

        json_string = json_match.group(1).strip()
        recipe_part = response_text.split('[JSON-END]')[-1].strip()
        
        ingredient_list = json.loads(json_string)
        
        # --- Calculate Nutrition ---
        total_nutrition = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        nutrition_details_html = "<ul>"

        for item in ingredient_list:
            ingredient_name = item.get("ingredient_name")
            quantity_grams = item.get("quantity_grams")
            
            if not ingredient_name or not quantity_grams:
                continue

            nutrition_json_string = get_nutrition_data(ingredient_name, quantity_grams)
            nutrition_data = json.loads(nutrition_json_string)
            
            if "error" not in nutrition_data:
                total_nutrition["calories"] += nutrition_data["calories"]
                total_nutrition["protein"] += nutrition_data["protein"]
                total_nutrition["fat"] += nutrition_data["fat"]
                total_nutrition["carbs"] += nutrition_data["carbs"]
                nutrition_details_html += f"<li><b>{nutrition_data['ingredient']}</b>: {nutrition_data['calories']} cal, {nutrition_data['protein']}g protein</li>"

        nutrition_details_html += "</ul>"
        
        # Format the final nutrition chart
        nutrition_chart = f"""
        {nutrition_details_html}
        <hr>
        <p><strong>Total Calories:</strong> {round(total_nutrition['calories'])}</p>
        <p><strong>Total Protein:</strong> {round(total_nutrition['protein'], 1)}g</p>
        <p><strong>Total Fat:</strong> {round(total_nutrition['fat'], 1)}g</p>
        <p><strong>Total Carbs:</strong> {round(total_nutrition['carbs'], 1)}g</p>
        """
        
        return recipe_part, nutrition_chart

    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None, f"An error occurred. Make sure Ollama is running.\nDetails: {e}"
    except json.JSONDecodeError:
        return None, "Error: AI returned invalid JSON. Could not parse."


# --- Step 3: The Streamlit UI ---
# This is the code that creates the webpage.
# Streamlit converts these Python commands into a real webpage.

st.set_page_config(page_title="AI Recipe Generator", layout="centered")
st.title("🧑‍🍳 AI Food Recipe & Nutritional Chart Generator")
st.write("Enter the ingredients you have, and the AI will generate a recipe and a nutritional chart for you.")

# Create a text input box
user_input = st.text_input("Enter your ingredients (e.g., paneer, spinach, onion)")

# Create a button
if st.button("Generate Recipe"):
    if user_input:
        # Show a "spinner" while it's working
        with st.spinner("Generating your recipe... This might take a moment."):
            recipe, nutrition = generate_recipe_and_nutrition(user_input)
        
        if recipe:
            # Display the results
            st.subheader("Generated Recipe")
            st.markdown(recipe) # Use markdown to render formatting
            
            st.subheader("Approximate Nutritional Chart")
            st.markdown(nutrition, unsafe_allow_html=True) # Use HTML for the list
        else:
            # Show an error if it failed
            st.error(nutrition) # The 'nutrition' var holds the error message
    else:
        st.warning("Please enter some ingredients.")