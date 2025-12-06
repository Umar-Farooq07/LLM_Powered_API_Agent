from dotenv import load_dotenv
load_dotenv()

from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage

huggingface_llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V3.2",
    task="text-generation"
)

Chat_History= [
    SystemMessage("you are a lazy man answer the question in as many less words as possible ")
]

#template


template= PromptTemplate(template= """
    

""",
input_variables=['question'])


while(True):
    question= input()
    Chat_History.append(HumanMessage(question))
    hugginface_model = ChatHuggingFace(llm= huggingface_llm)
    response = hugginface_model.invoke(Chat_History).content
    Chat_History.append(AIMessage(response))
    print(response)


