from dotenv import load_dotenv
load_dotenv()

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage


class QueryLLM():
    
    template = PromptTemplate(
        template="""
        You are an expert software assistant.

        Documentation:
        {context}

        User Query:
        {query}

        Instructions:
        - Use ONLY the provided documentation to answer.
        - Do NOT invent facts outside the documentation.
        - If the user asks for Python code, you MUST provide:
        1. Complete runnable Python code
        2. Proper indentation
        3. No incomplete lines
        4. Enclosed STRICTLY inside triple backticks

        Required Code Format:
        ```python
        # complete runnable python code
        If code is not required, provide only explanation.
        Do not output partial code blocks.
        """,
        input_variables=['query', 'context']
        )

    def __init__(self):
        self.hugginface_model = HuggingFaceEndpoint(
            repo_id='deepseek-ai/DeepSeek-V3.2',
            task='text-generation',
            max_new_tokens=2048
        )
        self.hugginface_llm = ChatHuggingFace(llm=self.hugginface_model)
        
        self.chathistory = [
            SystemMessage(content="""
    You are an expert software assistant.
    Follow the formatting rules strictly.
    Never output incomplete code.
    If code is given, it must be inside python and fully runnable.
    """)
    ]

    def query_llm(self, context, query):
        prompt_text = self.template.format(context=context, query=query)
        self.chathistory.append(HumanMessage(content=prompt_text))
        
        result = self.hugginface_llm.invoke(self.chathistory)
        
        content = result.content.strip()

        # Safety: wrap code if model forgets backticks
        if ("def " in content or "import " in content) and "```" not in content:
            content = f"```python\n{content}\n```"

        result.content = content
        self.chathistory.append(AIMessage(content=result.content))
        return result