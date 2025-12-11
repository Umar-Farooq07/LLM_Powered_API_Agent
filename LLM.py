from dotenv import load_dotenv
load_dotenv()


from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage,AIMessage,HumanMessage

hugginface_model = HuggingFaceEndpoint(
    repo_id='deepseek-ai/DeepSeek-V3.2',
    task = 'text-generation'
    
)
hugginface_llm= ChatHuggingFace(llm=hugginface_model)



class QueryLLM():
    
    template = PromptTemplate(
        template="""you are an expert software assistent
                    Documentation: {context}
                    query: {query}

                    use only the documentation provided and give the executable python code enclosed in ``` ```where ever necessary also do not invent any false endpoints or information on your own""",
        input_variables=['query', 'context']
        )
    def __init__(self):
        
        chathistory = [
            SystemMessage(content = """you are an expert software assistent.
                        follow the given instructions strictly do not give the answer without knowledge""")
        ]
    
        
    def query_llm(self, context,query):
        self.chathistory.append(HumanMessage(content=self.template.invoke(context= context, query =query ).to_string()))
        result = hugginface_llm.invoke(self.chathistory)
        self.chathistory.append(AIMessage(content=result.content))
        return result


model = QueryLLM()
response = model.query_llm("delhi is capital of india", 'what is capital of india')
print(response.content)



    


