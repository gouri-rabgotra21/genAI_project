import ollama
import json
import re

# --- Step 1: Define Your Python Tool (The "Calculator") ---
# This part is unchanged.
def get_nutrition_data(ingredient_name: str, quantity_grams: int) -> str:
    """
    Gets nutritional data for a given ingredient and quantity.
    
    Args:
        ingredient_name (str): The name of the ingredient (e.g., "paneer", "spinach").
        quantity_grams (int): The weight of the ingredient in grams.

    Returns:
        str: A JSON string of the nutritional info (calories, protein, fat, carbs).
    """
    print(f"--- [Tool Called] Searching nutrition for: {quantity_grams}g of {ingredient_name} ---")
    
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
    
    # Look up the ingredient
    ingredient_key = ingredient_name.lower()
    
    # Handle common similar names
    if "ghee" in ingredient_key or "vegetable oil" in ingredient_key:
        ingredient_key = "oil"
    if "tomatoes" in ingredient_key:
        ingredient_key = "tomato"
    
    if ingredient_key in mock_database:
        data = mock_database[ingredient_key]
        
        # Calculate nutrition based on the requested quantity
        factor = quantity_grams / 100.0
        nutrition_result = {
            "ingredient": ingredient_key,
            "quantity_grams": quantity_grams,
            "calories": round(data["calories_per_100g"] * factor),
            "protein": round(data["protein_per_100g"] * factor, 2),
            "fat": round(data["fat_per_100g"] * factor, 2),
            "carbs": round(data["carbs_per_100g"] * factor, 2)
        }
        # Return it as a JSON string
        return json.dumps(nutrition_result)
    else:
        # Handle cases where the mock ingredient isn't found
        print(f"--- [Tool Warning] Ingredient not in mock DB: {ingredient_name} ---")
        return json.dumps({"error": "Ingredient not found in mock database"})

# --- Step 2: Set up the Main "Agent" Logic (New Version) ---

# Connect to the local Ollama client
client = ollama.Client()

# 1. Define the user's request
user_ingredients = "paneer, spinach, and onion"

# This is our new, highly-engineered prompt.
# We are telling the AI to give us JSON in a specific format.
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

# 2. Start the conversation
messages = [
    {'role': 'user', 'content': user_prompt}
]

print(f"User: I have {user_ingredients}. What can I make?")
print("--- [AI Thinking...] ---")

# 3. Call the model (Note: no 'tools' parameter)
response = client.chat(
    model='llama3',
    messages=messages
)

response_text = response['message']['content']

# 4. Manually parse the AI's response
try:
    # Use regex to find the JSON block. This is more robust.
    json_match = re.search(r'\[JSON-START\](.*)\[JSON-END\]', response_text, re.DOTALL)
    
    if not json_match:
        print("--- [Error] AI did not return a valid JSON block. ---")
        print(response_text)
        exit()

    json_string = json_match.group(1).strip()
    
    # The AI might have included the recipe *inside* the tags, so let's find the recipe part *after*
    recipe_part = response_text.split('[JSON-END]')[-1].strip()

    # Parse the JSON string into a Python list
    ingredient_list = json.loads(json_string)

    # 5. Manually call our "tool" for each ingredient
    total_nutrition = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
    nutrition_details_list = []

    for item in ingredient_list:
        ingredient_name = item.get("ingredient_name")
        quantity_grams = item.get("quantity_grams")
        
        if not ingredient_name or not quantity_grams:
            print(f"--- [Tool Warning] Skipping invalid ingredient item: {item} ---")
            continue

        # Call our Python function
        nutrition_json_string = get_nutrition_data(ingredient_name, quantity_grams)
        nutrition_data = json.loads(nutrition_json_string)
        
        if "error" not in nutrition_data:
            # Add to totals
            total_nutrition["calories"] += nutrition_data["calories"]
            total_nutrition["protein"] += nutrition_data["protein"]
            total_nutrition["fat"] += nutrition_data["fat"]
            total_nutrition["carbs"] += nutrition_data["carbs"]
            
            # Add to details list for printing
            nutrition_details_list.append(
                f"  - {nutrition_data['ingredient']}: {nutrition_data['calories']} cal, {nutrition_data['protein']}g protein"
            )

    # 6. Print the final, combined result
    print("\n=================================")
    print("      AI Recipe Generator      ")
    print("=================================\n")
    
    # Print the recipe text
    print(recipe_part)
    
    # Print our calculated nutrition
    print("\n--- Approximate Nutritional Chart ---")
    print("\n".join(nutrition_details_list))
    print("---------------------------------")
    print(f"**Total Calories:** {round(total_nutrition['calories'])}")
    print(f"**Total Protein:** {round(total_nutrition['protein'], 1)}g")
    print(f"**Total Fat:** {round(total_nutrition['fat'], 1)}g")
    print(f"**Total Carbs:** {round(total_nutrition['carbs'], 1)}g")


except json.JSONDecodeError:
    print("--- [Error] AI returned invalid JSON. Could not parse. ---")
    print("Raw AI response:")
    print(response_text)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print("Raw AI response:")
    print(response_text)