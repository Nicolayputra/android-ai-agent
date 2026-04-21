import os, json, logging, re
from brain import AIRouter

log = logging.getLogger("NLUProcessor")

class NLUProcessor:
    """Mesin Pemrosesan Bahasa Alami untuk menormalisasi dan mengekstrak intent."""
    
    @staticmethod
    def normalize_input(text: str) -> dict:
        """
        Menormalisasi input: memperbaiki typo, mengubah slang, dan mengekstrak struktur.
        Returns: {
            "original": str,
            "normalized": str,
            "intent": str,
            "entities": dict,
            "slang_detected": bool
        }
        """
        log.info(f"🧠 NLU: Normalizing input -> {text}")
        
        prompt = f"""
        Analyze this Indonesian user input: "{text}"
        
        TASKS:
        1. Fix any typos.
        2. Convert Indonesian slang to standard Indonesian (Formal/Semi-Formal).
        3. Extract the core INTENT (e.g., GET_BATTERY, TAKE_SCREENSHOT, GENERAL_QUERY).
        4. Extract entities (e.g., app name, brightness level).
        
        RETURN ONLY JSON in this format:
        {{
            "normalized": "standard text here",
            "intent": "INTENT_NAME",
            "entities": {{}},
            "slang_detected": true/false
        }}
        """
        
        try:
            # Menggunakan Gemini karena API key tersedia
            response = AIRouter.query_gemini(prompt)
            clean_json = response.strip().replace("```json", "").replace("```", "")
            result = json.loads(clean_json)
            result["original"] = text
            return result
        except Exception as e:
            log.error(f"NLU Normalization Failed: {e}")
            # Fallback jika AI gagal
            return {
                "original": text,
                "normalized": text,
                "intent": "UNKNOWN",
                "entities": {},
                "slang_detected": False
            }

    @staticmethod
    def extract_pattern(normalized_text: str):
        """Mengekstrak pola struktur kalimat untuk pembelajaran otonom."""
        # Contoh: "Tolong nyalakan lampu" -> "ACTION_REQUEST(verb=nyalakan, target=lampu)"
        prompt = f"Analyze the grammatical structure of this normalized sentence and return a pattern template: '{normalized_text}'"
        pattern = AIRouter.query_gemini(prompt)
        return pattern
