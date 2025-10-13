import google.generativeai as genai
from src.config import GEMINI_API_KEY

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_response(self, prompt, context=None):
        try:
            full_prompt = f"Context: {context}\n\nUser: {prompt}" if context else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def generate_with_tools(self, prompt, tools_output):
        """Generate response incorporating tool outputs"""
        tool_context = "\n".join([f"{tool}: {output}" for tool, output in tools_output.items()])
        full_prompt = f"""
        Tool Outputs:
        {tool_context}
        
        User Question: {prompt}
        
        Please provide a helpful response incorporating the tool outputs above:
        """
        return self.generate_response(full_prompt)