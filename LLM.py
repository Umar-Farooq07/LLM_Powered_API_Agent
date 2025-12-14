from dotenv import load_dotenv
load_dotenv()


from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage,AIMessage,HumanMessage





class QueryLLM():
    
    template = PromptTemplate(
        template="""you are an expert software assistent
                    Documentation: {context}
                    query: {query}

                    use only the documentation provided and give the executable python code enclosed in ``` ```when ever asked  also do not invent any false endpoints or information on your own""",
        input_variables=['query', 'context']
        )
    def __init__(self):
        self.hugginface_model = HuggingFaceEndpoint(
        repo_id='deepseek-ai/DeepSeek-V3.2',
        task = 'text-generation'
        
        )
        self.hugginface_llm= ChatHuggingFace(llm=self.hugginface_model)
        
        self.chathistory = [
            SystemMessage(content = """you are an expert software assistent.
                        follow the given instructions strictly do not give the answer without knowledge""")
        ]
    
        
    def query_llm(self, context,query):
        prompt_text= self.template.format(context=context,query= query)
        self.chathistory.append(HumanMessage(content=prompt_text))
        result = self.hugginface_llm.invoke(self.chathistory)
        self.chathistory.append(AIMessage(content=result.content))
        return result






    


