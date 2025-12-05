from PyPDF2 import PdfReader
from langchain_community.embeddings import HuggingFaceEmbeddings



reader = PdfReader("flask_tutorial.pdf")

text= []

for i in range(len(reader.pages)):
    text.append(reader.pages[i].extract_text())


from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    collection_name="demo",
    embedding_function=embeddings,
    persist_directory="chroma_store"
)

db.add_texts(text)
db.persist()


query = "what is webframe work"

# Retrieve top 3 similar chunks
results = db.similarity_search(query, k=1)

for i, r in enumerate(results):
    print(f"\n---- Result {i+1} ----")
    print(r.page_content)
    print("Metadata:", r.metadata)