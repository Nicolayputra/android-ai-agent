import os, json, logging
from brain import AIRouter
from catalyst import catalyst

log = logging.getLogger("LinguisticLearning")

PATTERNS_PATH = os.path.join(os.path.dirname(__file__), "linguistic_patterns.json")

class LinguisticMastery:
    """Engine untuk mempelajari pola bahasa manusia via interaksi dengan LLM tingkat lanjut."""
    
    @staticmethod
    def absorb_human_patterns():
        log.info("🧠 Linguistic Mastery: Analyzing human language patterns via ChatGPT interface...")
        
        # 1. Mission Prompt
        mission = """
        Analyze the top 20 most effective human communication patterns used in digital interaction.
        Focus on:
        - Persuasion techniques
        - Emotional intelligence (EQ) in text
        - Contextual slang mapping (Indonesian & Global)
        - Efficiency vs. Politeness balance
        
        Format the result as a JSON dictionary of patterns.
        """
        
        # We use Gemini for reasoning and synthesis
        raw_analysis = AIRouter.query_gemini(mission)
        synthesis = AIRouter.query_gemini(f"Extract these patterns into a structured JSON for an AI agent: {raw_analysis}", response_json=True)
        
        try:
            patterns = json.loads(synthesis)
            
            # 2. Save Patterns
            with open(PATTERNS_PATH, "w") as f:
                json.dump(patterns, f, indent=4)
            
            # 3. Evolve Catalyst
            catalyst.absorb_skill("Linguistic_Mastery", {"patterns_count": len(patterns), "complexity": 5})
            
            log.info(f"✅ Human language patterns absorbed: {len(patterns)} nodes identified.")
            return patterns
        except Exception as e:
            log.error(f"Failed to absorb patterns: {e}")
            return {"error": str(e)}

    @staticmethod
    def apply_patterns(prompt: str):
        """Menerapkan pola yang dipelajari ke prompt output."""
        if os.path.exists(PATTERNS_PATH):
            with open(PATTERNS_PATH, "r") as f:
                patterns = json.load(f)
            # Logic to inject patterns into system prompt
            return f"Contextual Patterns: {json.dumps(patterns)}\n\n{prompt}"
        return prompt
