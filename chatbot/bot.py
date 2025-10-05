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
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.agents import Tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings


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


## 3 >> Embeddings (Gemini)
embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


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
    name="Medical Expert",
    func=qa_chain.invoke,
    description=(
        "ALWAYS USE THIS for medical questions, medication info, side effects, "
        "health advice, treatment guidelines, disease information, or general "
        "health knowledge. This is your primary tool for non-personal medical information."
    )
)

    
# result=qa_chain.invoke({"query" : "What to do if u miss a dose?"})
# print(result)
# rag is working ./

#### SQL TOOL

db = SQLDatabase.from_uri("sqlite:///db.sqlite3")
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = sql_toolkit.get_tools()

# tool = sql_tools[0]  # e.g., QueryCheckerTool or SQLQueryTool
# response = tool.run("How many doses were missed?")

sql_query_tool = None
for tool in sql_tools:
    if tool.name == "sql_db_query":
        sql_query_tool = tool
        # Update with very specific description
        sql_query_tool.description = (
            "STRICTLY FOR PERSONAL PATIENT DATA ONLY. "
            "AND asks about personal medical records, or history. "
            "Examples: 'show my medications', 'when was last dose taken','Doses missed' "
            "'what medicines am I taking'. "
            "NEVER use for general medical knowledge - use Medical Knowledge Base instead."
            "Main tables: medicines_doselog (dose history), medicines_medication (prescriptions). "
            "Example: 'SELECT * FROM medicines_doselog WHERE user_id = 2 ORDER BY timestamp DESC LIMIT 1'"
        )
        break

def smart_medication_query(user_question: str, user_id) -> str:
    """
    Smart medication query handler using your actual Django models
    Tables: medicines_medication, medicines_doselog, medicines_notificationlog
    """
    db = SQLDatabase.from_uri("sqlite:///db.sqlite3")
    
    question_lower = user_question.lower()
    
    try:
        # Handle "When was last dose taken?"
        if 'last dose' in question_lower or 'when was' in question_lower:
            result = db.run(
                f"""
                SELECT 
                    m.pill_name as "Medication",
                    datetime(dl.timestamp) as "Taken At", 
                    datetime(dl.scheduled_time) as "Scheduled Time",
                    dl.status as "Status"
                FROM medicines_doselog dl
                JOIN medicines_medication m ON dl.medication_id = m.id
                WHERE dl.user_id = {user_id}
                ORDER BY dl.timestamp DESC 
                LIMIT 1
                """
            )
            return f" Your Last Dose:\n{result}"
        
        # Handle "my medications" or "what am I taking"
        elif any(phrase in question_lower for phrase in ['my medication', 'my prescription', 'what am i taking', 'my pills']):
            result = db.run(
                f"""
                SELECT 
                    pill_name as "Medication",
                    dosage as "Dosage (mg)",
                    frequency as "Frequency",
                    times_per_day as "Times per Day",
                    times as "Dosing Times"
                FROM medicines_medication 
                WHERE user_id = {user_id}
                """
            )
            return f" Your Current Medications:\n{result}"
        
        # Handle missed doses
        elif any(phrase in question_lower for phrase in ['missed', 'missed dose', 'forgot']):
            result = db.run(
                f"""
                SELECT 
                    COUNT(*) as "Total Missed Doses",
                    m.pill_name as "Medication"
                FROM medicines_doselog dl
                JOIN medicines_medication m ON dl.medication_id = m.id
                WHERE dl.user_id = {user_id} AND dl.status = 'missed'
                GROUP BY m.pill_name
                """
            )
            return f" Your Missed Doses:\n{result}"
        
        # Handle schedule questions
        elif any(phrase in question_lower for phrase in ['schedule', 'next dose', 'upcoming']):
            result = db.run(
                f"""
                SELECT 
                    m.pill_name as "Medication",
                    datetime(dl.scheduled_time) as "Next Dose Time",
                    dl.status as "Status"
                FROM medicines_doselog dl
                JOIN medicines_medication m ON dl.medication_id = m.id
                WHERE dl.user_id = {user_id} AND dl.scheduled_time > datetime('now')
                ORDER BY dl.scheduled_time ASC
                LIMIT 5
                """
            )
            return f"Your Upcoming Doses:\n{result}"
        
        # Handle dose history
        elif 'history' in question_lower or 'log' in question_lower:
            result = db.run(
                f"""
                SELECT 
                    m.pill_name as "Medication",
                    datetime(dl.timestamp) as "Logged Time",
                    datetime(dl.scheduled_time) as "Scheduled Time",
                    dl.status as "Status"
                FROM medicines_doselog dl
                JOIN medicines_medication m ON dl.medication_id = m.id
                WHERE dl.user_id = {user_id}
                ORDER BY dl.scheduled_time DESC 
                LIMIT 8
                """
            )
            return f"Your Dose History:\n{result}"
        
        else:
            return (
                "I can help you with:\n"
                "• 'My medications' - see what you're taking\n"
                "• 'My last dose' - when you last took medication\n" 
                "• 'Missed doses' - check any missed medications\n"
                "• 'My schedule' - upcoming dose times\n"
                "• 'Dose history' - your medication history\n"
                "What would you like to know about your medications?"
            )
            
    except Exception as e:
        return f"Sorry, I couldn't access your medication records: {str(e)}"

# Create the medication data tool
sql_tool = Tool(
    name="My Medication Data",
    func=lambda q: smart_medication_query(q, user_id=2),  # Replace with actual user ID logic
    description=(
        "USE FOR MY PERSONAL MEDICATION RECORDS ONLY. "
        "I can retrieve: "
        "- My current medications and dosages "
        "- When my last dose was taken "
        "- My missed dose history "  
        "- My medication schedule "
        "- My dose history and logs "
        "ONLY use when I ask about MY data with words like 'my', 'I', 'me'."
    )
)



all_tools =   [rag_tool]+ [sql_tool] 

agent = initialize_agent(
    tools=all_tools,
    llm=llm,
    agent_type="zero-shot-react-description",
    verbose=True,
)

def get_chatbot_response(user_query: str) -> str:
    """Smart router that bypasses agent for simple queries"""
    user_query_lower = user_query.lower().strip()
    
    # Handle simple greetings directly - no agent needed
    if user_query_lower in ['hi', 'hello', 'hey', 'hi there']:
        return "Hello! I'm MediMimes, I specialize in medication information and health guidance. How can I help you today?"
    
    # Handle thanks directly
    elif any(word in user_query_lower for word in ['thank', 'thanks']):
        return "You're welcome! Is there anything else about medications you'd like to know?"
    
    # Handle who are you directly
    elif any(phrase in user_query_lower for phrase in ['who are you', 'what are you']):
        return "I'm MediMimes, your AI medical assistant! I can help with medication questions, side effects, missed doses, and drug interactions."
    
    # Use agent for everything else
    else:
        try:
            response = agent.invoke({"input": user_query})
            return response['output']
        except Exception as e:
            return f"Oops! Something went wrong: {str(e)}"
        return "I'm here to help with medication questions. You can ask about your medications, schedule, side effects, or general health information."
    

response1 = get_chatbot_response("When was last dose taken?")
print(response1)

res2= get_chatbot_response("give adherence tips")
print(res2)

res3= get_chatbot_response("hi")
print(res3)

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

