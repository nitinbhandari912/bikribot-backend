from fastapi import FastAPI, File, UploadFile
import google.generativeai as genai
import json

app = FastAPI()

# ==========================================
# 1. PASTE YOUR GEMINI API KEY HERE
# ==========================================
import os
import google.generativeai as genai

# Key yahan bilkul nahi honi chahiye
genai.configure(api_key=os.environ.get("GENAI_API_KEY"))

# We use gemini-1.5-flash as it is the fastest for image recognition
model = genai.GenerativeModel('gemini-2.0-flash')

@app.post("/scan")
async def scan_item(file: UploadFile = File(...)):
    try:
        # 1. Read the image sent from the Flutter app
        image_data = await file.read()
        
        # 2. Instruct Gemini exactly how to format the data
        prompt = """
        Analyze this image and identify the product. Return ONLY a valid JSON object. 
        Do not include markdown tags like ```json.
        Use exactly these keys and data types:
        {
            "item_name": "Name of the product (String)",
            "estimated_price": Estimated retail price in INR (Integer),
            "quantity": 1 (Integer),
            "color": "Primary color of the item (String)"
        }
        """
        
        # 3. Send the image and prompt to Gemini
        image_part = {"mime_type": file.content_type, "data": image_data}
        response = model.generate_content([prompt, image_part])
        
        # 4. Clean the response and convert it to a real JSON object
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(clean_text)
        
        # 5. Send the JSON straight back to the Flutter app!
        return result_json
        
    except Exception as e:
        print(f"Error: {e}")
        # Safe fallback if the AI gets confused
        return {
            "item_name": "AI Scan Failed", 
            "estimated_price": 0, 
            "quantity": 1, 
            "color": "Unknown"
        }