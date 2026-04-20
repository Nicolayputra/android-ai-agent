import os, json, logging, requests
from brain import AIRouter, ResearchEngine

log = logging.getLogger("SkillAcquisition")

SKILL_LIBRARY_PATH = os.path.join(os.path.dirname(__file__), "skill_library.json")

class SkillAcquisitionEngine:
    """Engine untuk menemukan dan mengintegrasikan alat AI baru secara otonom."""
    
    @staticmethod
    def discover_and_integrate(topic: str):
        log.info(f"🔍 Discovering new AI tools for: {topic}")
        
        # 1. Web Research untuk mencari API/Tools gratis
        search_query = f"top free AI API for {topic} with documentation link"
        search_results = AIRouter.web_search(search_query)
        
        # 2. Analisis mendalam menggunakan model AI
        analysis_prompt = f"""
        Berdasarkan hasil pencarian ini: {search_results}
        Tentukan satu alat AI terbaik untuk {topic}. 
        Ekstrak informasi berikut dalam format JSON:
        - name: Nama alat
        - endpoint: URL API Utama
        - method: GET/POST
        - auth_type: None/API_Key/Bearer
        - description: Kegunaan alat
        - usage_example: Contoh payload JSON (jika POST)
        """
        
        analysis = AIRouter.query_gemini(analysis_prompt)
        
        try:
            # Bersihkan AI response dari markdown jika ada
            clean_json = analysis.strip().replace("```json", "").replace("```", "")
            tool_data = json.loads(clean_json)
            
            # 3. Simpan ke Skill Library
            SkillAcquisitionEngine.save_skill(tool_data)
            return tool_data
        except Exception as e:
            log.error(f"Failed to integrate skill: {e}")
            return {"error": str(e), "raw_response": analysis}

    @staticmethod
    def save_skill(tool_data: dict):
        library = {}
        if os.path.exists(SKILL_LIBRARY_PATH):
            with open(SKILL_LIBRARY_PATH, "r") as f:
                library = json.load(f)
        
        library[tool_data["name"]] = tool_data
        
        with open(SKILL_LIBRARY_PATH, "w") as f:
            json.dump(library, f, indent=4)
        log.info(f"✅ Skill integrated: {tool_data['name']}")

    @staticmethod
    def get_integrated_skills():
        if os.path.exists(SKILL_LIBRARY_PATH):
            with open(SKILL_LIBRARY_PATH, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def execute_skill(skill_name: str, user_input: str):
        skills = SkillAcquisitionEngine.get_integrated_skills()
        if skill_name not in skills:
            return f"Skill {skill_name} belum terintegrasi."
        
        tool = skills[skill_name]
        log.info(f"🚀 Executing dynamic skill: {skill_name}")
        
        # Logic eksekusi dinamis (sederhana)
        try:
            if tool["method"] == "POST":
                # AI menyusun payload berdasarkan user_input dan contoh usage
                payload_prompt = f"Berdasarkan input '{user_input}', susunlah payload JSON untuk API ini: {json.dumps(tool)}. Berikan HANYA JSON."
                payload_str = AIRouter.query_qwen(payload_prompt).strip().replace("```json", "").replace("```", "")
                payload = json.loads(payload_str)
                
                resp = requests.post(tool["endpoint"], json=payload, timeout=15)
            else:
                resp = requests.get(tool["endpoint"], params={"q": user_input}, timeout=15)
            
            return resp.json()
        except Exception as e:
            return f"Execution Error: {e}"
