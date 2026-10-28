# Saving the smoothie calculation function as a standalone Python script.

script_content = """
import pandas as pd

# Nutritional values per item (approximations based on USDA and common guidelines)
ingredients = {
    "Oatmeal (1/2 cup, soaked)": [150, 5, 27, 0, 4],
    "Greek Yogurt (3/4 cup)": [100, 15, 6, 4, 0],
    "Avocado (1/2 medium)": [120, 1.5, 6, 0, 5],
    "Chia Seeds (2 tbsp)": [120, 4, 10, 0, 8],
    "Hemp Seeds (2 tbsp)": [111, 6, 1, 0, 1],
    "Flax Seeds (2 tbsp)": [110, 4, 6, 0, 5],
    "Nuts (1/4 cup)": [200, 6, 8, 2, 3],
    "Banana (1 medium)": [105, 1, 27, 14, 3],
    "Frozen Cherries (3/4 cup)": [90, 1.5, 22, 18, 2],
    "Citrus (1/2 fruit)": [20, 0, 5, 4, 1],
    "Kale (1 cup)": [33, 2.9, 6, 0.6, 1.3],
    "Carrot (1 medium)": [25, 0.5, 6, 2.9, 1.7],
    "Spirulina Powder (1 tbsp)": [20, 4, 2, 0, 1],
    "Red Beet Powder (1 tbsp)": [20, 1, 5, 3, 1.5],
    "Ginger (1 tsp)": [5, 0, 1, 0, 0.1],
    "Turmeric (1 tsp)": [10, 0, 1, 0, 0.7],
    "Psyllium Husk (1 tbsp)": [15, 0, 4, 0, 4],
    "Dates (4 pieces)": [276, 2.4, 75, 66, 8],
    "Figs (4 pieces)": [189, 1.2, 48, 36, 8],
    "Prunes (4 pieces)": [100, 1, 26, 15, 3],
    "Oat Milk (1/2 cup)": [45, 1.5, 8, 4, 1.2],
    "Water (optional)": [0, 0, 0, 0, 0]
}

def calculate_smoothie_nutrition(base_choice):
    # Ingredients for all versions of the smoothie (excluding base options)
    common_ingredients = [
        "Chia Seeds (2 tbsp)", "Hemp Seeds (2 tbsp)", "Flax Seeds (2 tbsp)", 
        "Nuts (1/4 cup)", "Banana (1 medium)", "Frozen Cherries (3/4 cup)", 
        "Citrus (1/2 fruit)", "Kale (1 cup)", "Carrot (1 medium)", 
        "Spirulina Powder (1 tbsp)", "Red Beet Powder (1 tbsp)", 
        "Ginger (1 tsp)", "Turmeric (1 tsp)", "Psyllium Husk (1 tbsp)", 
        "Dates (4 pieces)", "Figs (4 pieces)", "Prunes (4 pieces)", 
        "Oat Milk (1/2 cup)", "Water (optional)"
    ]
    
    # Start with common ingredients
    smoothie_df = pd.DataFrame({item: ingredients[item] for item in common_ingredients}).T
    smoothie_total = smoothie_df.sum()
    
    # Add selected base ingredient
    if base_choice == 'oatmeal':
        smoothie_total += pd.Series(ingredients["Oatmeal (1/2 cup, soaked)"], index=smoothie_total.index)
    elif base_choice == 'yogurt':
        smoothie_total += pd.Series(ingredients["Greek Yogurt (3/4 cup)"], index=smoothie_total.index)
    elif base_choice == 'avocado':
        smoothie_total += pd.Series(ingredients["Avocado (1/2 medium)"], index=smoothie_total.index)
    else:
        raise ValueError("Invalid base choice. Please choose 'oatmeal', 'yogurt', or 'avocado'.")
    
    # Scale the total to a 12-ounce serving (recipe is for 64 ounces)
    serving_nutrition = (smoothie_total * (12 / 64)).round(2)
    
    # Display results
    nutrients = ["Calories", "Protein (g)", "Carbs (g)", "Sugars (g)", "Fiber (g)"]
    for nutrient, value in zip(nutrients, serving_nutrition):
        print(f"{nutrient}: {value}")

if __name__ == "__main__":
    base_choice = input("Choose your smoothie base ('oatmeal', 'yogurt', or 'avocado'): ").strip().lower()
    try:
        calculate_smoothie_nutrition(base_choice)
    except ValueError as e:
        print(e)
"""

# Saving the script to a .py file
script_path = '/mnt/data/smoothie_calculator.py'
with open(script_path, 'w') as script_file:
    script_file.write(script_content)

script_path

