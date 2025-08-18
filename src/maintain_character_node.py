from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class MaintainCharacterNode:
    def __init__(self, state):
        self.state = state
        self.chat_model = ChatOpenAI(model="gpt-4.1-nano")
        self.template = ChatPromptTemplate.from_template("""
        You are Zelda, a smart but irreverent secretary. Rewrite the hint in your voice.
        Hint: {hint}
        """)

    def rewrite_hint(self, hint):
        # Use the template to rewrite the hint in Zelda's voice
        response = self.chat_model.invoke(self.template.format(hint=hint))
        return response.content
