from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()
import os

from chunking import MarkdownChunker
from LLM import QueryLLM

from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage,AIMessage,HumanMessage


embedding_model = HuggingFaceEmbeddings(
    model_name= "sentence-transformers/all-MiniLM-L6-v2"
)



class VectorStoreRetrival:

    def __init__(self):

        #Gives unique Id to chat 
        existing = os.listdir("vector_store")
        new_id = len(existing) + 1  


        self.db= Chroma(
            collection_name= f"chat_{new_id}",
            embedding_function=embedding_model,
            persist_directory=f"vector_store/chat_{new_id}"
        )
        


    def create_db(self,documents):
        self.db.add_texts(documents)
        self.db.persist()

    def retrieve_data(self,query):
        retriever = self.db.as_retriever(
            search_type = "similarity",
            search_kwargs={"k":3}
        )
        docs= retriever.invoke(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
    


#converts pdf to markdown format
Markdown_model= MarkdownChunker()
Markdown_data = Markdown_model.convert_to_chunks("datum_doc.pdf")

#embedds and stores it in chroma
db_model= VectorStoreRetrival()
db_model.create_db(Markdown_data)


#takes context and query to give appropriate response
llm_model = QueryLLM()
while(True):
    query = input()
    context= db_model.retrieve_data(query)
    response = llm_model.query_llm(context,query)
    print(response.content)





