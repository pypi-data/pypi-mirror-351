from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Make sure the API key is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")

# Instanser
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=api_key,
    temperature=0.5,
    max_tokens=None,
)
memory_chain = ConversationChain(llm=llm, memory=ConversationBufferMemory())

## Exempel: print(chatAI("Hej!", memory=True))

def chatAI(AI_in: str, memory: bool = False) -> str:
    """
    Skicka meddelande till AI:n.
    Om memory=True används minne i konversationen.
    """
    if memory:
        response = memory_chain.run(AI_in)
        return response
    else:
        response = llm([HumanMessage(content=AI_in)])
        return response.content

