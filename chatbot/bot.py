from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, Tool
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.prompts import PromptTemplate
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.agents import Tool


## 1 >> Document loading
import pdfplumber

def load_pdf_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text
text=load_pdf_text(r"chatbot\resources\mock knowledge base.pdf")
# print(text)

## 2 >> Text Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize the splitter
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_text(text)

chunks=split_text(text)
# print(chunks)


## 3 >> Embeddings (HuggingFace)
embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')


## 4 >> Vector Store (Chroma)
def create_vector_store(chunks):
    vector_db = Chroma.from_texts(
        chunks,
        embedding=embedding_model,
        persist_directory="./db"  
    )
    return vector_db

# vector_store=create_vector_store(chunks)

## 5 >> RAG retreival + Generation
def load_vector_store(persist_dir="./db"): 
    """Load existing vector store.""" 
    if os.path.exists(persist_dir):
        return Chroma(persist_directory=persist_dir, embedding_function=embedding_model) 
    else: return None

vector_store = load_vector_store(persist_dir="./db")

if vector_store is None:
    raise ValueError("Vector store not found! Make sure it has been created and persisted at ./db")



# retreiver
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 2 , "lambda_mult":0.7}
    )

# query="what happens if i miss dose?"
# results=retriever.invoke(query)

# for i, doc in enumerate(results):
#     print(f"\n-------results{i+1}---------")
#     print(doc.page_content[:100])
    

# llm
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.3,
)



#  RAG QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # "map_reduce" or "stuff" depending on preference
    retriever=retriever,
    return_source_documents=False
)

# rag tool
rag_tool = Tool(
    name="Medical RAG Assistant",
    func=qa_chain.invoke,
    description=(
        "Use this tool to answer medical questions from uploaded documents, "
        "such as what to do if a dose is missed, or the side effects of a medicine."
    )
)

    
# result=qa_chain.invoke({"query" : "What to do if u miss a dose?"})
# print(result)
# rag is working ./

#### SQL TOOL

# Step 1: Connect to the database
db = SQLDatabase.from_uri("sqlite:///db.sqlite3")

# Step 2: Create the toolkit
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Step 3: Get the tools
sql_tools = sql_toolkit.get_tools()

# test
# tool = sql_tools[0]  # e.g., QueryCheckerTool or SQLQueryTool

# response = tool.run("How many doses were missed?")
# print(response)

all_tools = sql_tools + [rag_tool]

agent = initialize_agent(
    tools=all_tools,
    llm=llm,
    agent_type="zero-shot-react-description",
    verbose=True
)

def get_chatbot_response(user_query: str) -> str:
    """Routes user query through Gemini agent."""
    try:
        response = agent.invoke({"input":user_query})
        return response
    except Exception as e:
        return f"Oops! Something went wrong: {str(e)}"

response = get_chatbot_response("When was last dose taken?")
print(response)

#### Rescheduling tool
# from datetime import datetime, timedelta

# def reschedule_dose(info: str) -> str:
#     """
#     info: string describing which dose to reschedule
#     Example: "I missed my 9 AM paracetamol dose today"
    
#     Returns a confirmation string
#     """
#     # For now, we'll parse simple info using keywords
#     # In real case, you can parse dose name, time, date, user_id, etc.

#     # Mock logic: always reschedule 2 hours from now
#     new_time = datetime.now() + timedelta(hours=2)
#     new_time_str = new_time.strftime("%Y-%m-%d %H:%M")

#     # Here you would normally update your database or calendar
#     # e.g., UPDATE doses SET dose_time=new_time WHERE ...  

#     return f"Your dose has been rescheduled to {new_time_str}."

# # wrap it as a langchain tool
# from langchain.agents import Tool

# rescheduler_tool = Tool(
#     name="Dose Rescheduler",
#     func=reschedule_dose,
#     description=(
#         "Use this tool when the user wants to reschedule a missed medication dose. "
#         "The input will describe which dose and when it was missed."
#     )
# )

