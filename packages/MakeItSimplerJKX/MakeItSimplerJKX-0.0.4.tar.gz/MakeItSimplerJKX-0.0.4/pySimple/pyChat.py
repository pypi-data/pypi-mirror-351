from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Make sure the API key is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=api_key,
    temperature=0.5,
)

# Global variables
prompt = ""
message_histories = {}
session_id = ""

def setPrompt(promptMessage: str) -> None:
    """Set a custom system prompt for the AI."""
    global prompt
    prompt = promptMessage

def setID(sessionID: str) -> None:
    """Set a custom session ID for conversation memory."""
    global session_id
    session_id = sessionID

def chatAI(AI_in: str, m: bool = False, p: bool = False) -> str:
    """
    Send a message to the AI.
    If m=True, conversation memory is used.
    If p=True, the custom prompt is used.
    
    Raises:
        ValueError: If p=True but no prompt has been set using setPrompt().
        ValueError: If m=True but no session ID has been set using setID().
    """
    global prompt, message_histories, session_id
    
    if p and not prompt:
        raise ValueError("No prompt has been set. Use setPrompt() before using p=True.")
    
    if m and not session_id:
        raise ValueError("No session ID has been set. Use setID() before using m=True.")
    
    # Use the custom session ID
    current_session_id = session_id
    
    if m or p:
        # Set up the prompt template
        if p:
            messages = [
                SystemMessage(content=prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
        else:
            messages = [
                SystemMessage(content="You are a helpful assistant."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
        
        prompt_template = ChatPromptTemplate.from_messages(messages)
        chain = prompt_template.pipe(llm)
        
        # Set up message history
        if m:
            runnable_with_history = RunnableWithMessageHistory(
                chain,
                lambda session_id: _get_message_history(session_id),
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            
            # Invoke the chain with history
            response = runnable_with_history.invoke(
                {"input": AI_in},
                config={"configurable": {"session_id": current_session_id}}
            )
            return response.content
        else:
            # No memory, just use the prompt
            response = chain.invoke({"input": AI_in, "chat_history": []})
            return response.content
    else:
        # Direct LLM call without chain or memory
        response = llm.invoke([HumanMessage(content=AI_in)])
        return response.content

def _get_message_history(session_id):
    """Helper function to get or create message history for a session."""
    global message_histories
    if session_id not in message_histories:
        message_histories[session_id] = InMemoryChatMessageHistory()
    return message_histories[session_id]
