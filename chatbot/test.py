# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from dotenv import load_dotenv
# load_dotenv()


# embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
# vector = embeddings.embed_query("hello, world!")
# print(vector[:5])

from dotenv import load_dotenv
load_dotenv()

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# llm
from langchain_groq import ChatGroq
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.3,
)

db = SQLDatabase.from_uri("sqlite:///db.sqlite3")
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = sql_toolkit.get_tools()

# Print available tools to see what we have
print("Available SQL tools:")
for i, tool in enumerate(sql_tools):
    print(f"{i}: {tool.name} - {tool.description[:100]}...")