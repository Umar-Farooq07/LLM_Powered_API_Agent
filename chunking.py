from docling.document_converter import DocumentConverter 
from docling.datamodel.document import DocumentStream
from langchain_text_splitters import MarkdownTextSplitter, RecursiveCharacterTextSplitter
from io import BytesIO


class MarkdownChunker:
    def __init__(self):
        self.converter = DocumentConverter()
        self.separators = [
            # 1. CODE BLOCKS (strongest boundary)
            "\n```",                    # Start or end of code block

            # 2. HEADINGS (markdown structure)
            "\n###### ",                # h6 heading
            "\n##### ",                 # h5 heading
            "\n#### ",                  # h4 heading
            "\n### ",                   # h3 heading
            "\n## ",                    # h2 heading
            "\n# ",                     # h1 heading

            # 3. API-SPECIFIC KEYWORDS (common across all API docs)
            "\nHTTP Method:",           
            "\nRequest Parameters:",    
            "\nParameters:",            
            "\nResponse:",              
            "\nJSON Response:",         
            "\nExample:",               
            "\nEndpoint:",              
            "\nURL:",                   
            "\nDescription:",           
            "\nStatus Codes:",          
            "\nError Codes:",           

            # 4. LISTS (unordered & ordered)
            "\n- ",                     # bullet list
            "\n* ",                     # bullet list alternative
            "\n+ ",                     # additional bullet format
            "\n1. ",                    # numbered list
            "\n2. ",                    # etc., numbers generalize automatically

            # 5. TABLES
            "\n|",                      # table row
            "\n:-",                     # table header separator

            # 6. BLOCK QUOTES
            "\n> ",                     

            # 7. PARAGRAPHS
            "\n\n",                    # paragraph break

            # 8. FALLBACK SEPARATORS
            "\n",                      # line break
            " "                        # final fallback (rarely used)
        ]

    def convert_to_chunks(self,pdf_file):
        pdf_file.seek(0)

        # 2️⃣ Read bytes ONCE
        pdf_bytes = pdf_file.read()

        # 3️⃣ Convert bytes → BytesIO
        pdf_stream = BytesIO(pdf_bytes)

        # 4️⃣ Create DocumentStream for Docling
        doc = DocumentStream(
            name=pdf_file.name,
            stream=pdf_stream
        )

        # 5️⃣ Convert using Docling
        converter = DocumentConverter()
        result = converter.convert(doc)
        markdown_form = result.document.export_to_markdown()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap =100,
            separators= self.separators
        )
        chunks= splitter.split_text(markdown_form)
        return chunks


