# utils.py
import os
import io
import re
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF
import unicodedata
import re
from datetime import datetime
import pytz


# Load secrets from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def load_model():
    return genai.GenerativeModel("models/gemini-2.5-flash")

def image_to_bytes(image: Image.Image) -> bytes:
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()

def generate_nutrition_report(image: Image.Image, user_query: str = "") -> str:
    model = load_model()
    image_bytes = image_to_bytes(image)

    prompt = f"""
    You are a certified AI nutritionist. Based on the image and user query, provide detailed nutritional information including:
    - Names of food items
    - Estimated calories
    - Macronutrients (Carbs, Proteins, Fats)
    - Vitamins & Minerals
    - Health recommendations (e.g. diabetic friendly, heart health)

    User Query: {user_query}
    """

    response = model.generate_content(
        [
            prompt,
            {"mime_type": "image/png", "data": image_bytes}
        ],
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 2048
        }
    )
    return response.text

def generate_diet_plan(profile: str) -> str:
    model = load_model()
    prompt = f"""
    You are a certified Indian dietician with more than 20 years of experience and Create a full-day personalized Indian diet plan based on this profile:

    Profile:
    {profile}

    Include:
    - Breakfast, Lunch, Dinner, and 2 Snacks
    - Simple Indian food items
    - Calorie + macronutrient breakdown (Carbs, Proteins, Fats)
    - Diet tips for goal achievement
    """
    response = model.generate_content(prompt)
    return response.text

def extract_macros(diet_plan_text):
    pattern = r"(?i)(Carbs|Proteins|Fats):\s*(\d+)\s*g"
    macros = {"Carbs": 0, "Proteins": 0, "Fats": 0}
    for match in re.findall(pattern, diet_plan_text):
        macro, value = match
        macros[macro.capitalize()] += int(value)
    return macros

def clean_text(text: str) -> str:
    import unicodedata

    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        "–": "-",    # en dash
        "—": "-",    # em dash
        "’": "'",    # curly apostrophe
        "‘": "'",    # left quote
        "“": '"',    # left double quote
        "”": '"',    # right double quote
        "•": "-",    # bullet
        "⁄": "/",    # fraction slash
        "¼": "1/4",  # common fractions
        "½": "1/2",
        "¾": "3/4",
    }

    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # Normalize and remove remaining non-latin1 characters
    normalized = unicodedata.normalize("NFKD", text)
    ascii_compatible = normalized.encode("latin-1", errors="ignore").decode("latin-1")

    return ascii_compatible

def generate_pdf(text: str, title: str = "Diet Plan") -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)

    # Set default font
    pdf.set_font("Arial", size=10)
    line_height = 5  # Reduced from 7
    heading_size = 13

    lines = clean_text(text).split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(1)  # small line gap, not too much space
            continue

        # Bold heading lines
        if stripped.startswith("**") and stripped.endswith("**") and len(stripped) > 4:
            heading = re.sub(r"\*\*(.*?)\*\*", r"\1", stripped)
            pdf.set_font("Arial", style="B", size=heading_size)
            pdf.cell(0, line_height + 1, heading, ln=1)
            pdf.set_font("Arial", size=10)
            continue

        # Inline bold inside a regular line
        parts = re.split(r"(\*\*.*?\*\*)", line)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                bold_text = part[2:-2]
                pdf.set_font("Arial", style="B", size=10)
                pdf.multi_cell(0, line_height, bold_text)
                pdf.set_font("Arial", size=10)
            else:
                pdf.multi_cell(0, line_height, part)

    return pdf.output(dest="S").encode("latin1", errors="ignore")

def get_indian_time():
    india = pytz.timezone("Asia/Kolkata")
    return datetime.now(india).strftime("%Y-%m-%d_%H-%M")
