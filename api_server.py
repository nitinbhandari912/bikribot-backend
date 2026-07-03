from fastapi import FastAPI, File, UploadFile, HTTPException
import google.generativeai as genai
import json
import os

app = FastAPI()

# ==========================================
# GEMINI CONFIGURATION (Using Environment Variables)
# ==========================================
genai.configure(api_key=os.environ.get("GENAI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

@app.post("/scan")
async def scan_item(file: UploadFile = File(...)):
    try:
        # 1. Read the compressed image sent from the Flutter app
        image_data = await file.read()
        
        # 2. UPGRADED BATCH PROMPT: Instruct Gemini to find ALL items and return a JSON Array
        prompt = """
        Analyze this image and identify ALL visible products. Return ONLY a valid JSON array of objects. 
        Do not include markdown tags like ```json.
        Use exactly these keys and data types for EACH object in the array:
        [
            {
                "item_name": "Name of the product (String)",
                "estimated_price": Estimated retail price in INR (Integer),
                "quantity": 1 (Integer),
                "color": "Primary color or category of the item (String)"
            }
        ]
        """
        
        # 3. Send the image and prompt to Gemini
        image_part = {"mime_type": file.content_type, "data": image_data}
        response = model.generate_content([prompt, image_part])
        
        # 4. Clean the response and convert it to a real JSON list
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(clean_text)
        
        # 5. Send the JSON Array back to the Flutter app
        return result_json
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        # NO MORE FAKE PRODUCTS. Throw a real error so Flutter can show the "Retry" button.
        raise HTTPException(status_code=500, detail=str(e))
