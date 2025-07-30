A library to import simple functions to make a clean coded project.

### pyChat - A simple chat function for AI

##pyChat provides an extremely simple way to interact with AI models in your Python projects.
#
#        #### Basic Usage
#
#        ```python
#        from pySimple.pyChat import chatAI
#
#        # Simple chat without memory or custom prompt
#        response = chatAI("What is the capital of France?")
#        print(response)
#        ```
#
#        #### Using Memory
#
#        To maintain conversation context across multiple interactions:
#
#        ```python
#       from pySimple.pyChat import chatAI, setID
#
#        # Set a session ID for this conversation
#        setID("my_conversation_1")
#
#        # First message with memory enabled
#        response1 = chatAI("Tell me about Paris", m=True)
#        print(response1)
#
#        # Follow-up question (will remember previous context)
#        response2 = chatAI("What famous monument is there?", m=True)
#        print(response2)
#        ```
#
#        #### Using Custom Prompts
#
#        To guide the AI's behavior with a system prompt:
#
#        ```python
#        from pySimple.pyChat import chatAI, setPrompt
#
#        # Set a custom system prompt
#        setPrompt("You are a helpful assistant that specializes in geography.")
#
#        # Chat with the custom prompt enabled
#        response = chatAI("Tell me about France", p=True)
#        print(response)
#        ```
#
#        #### Combining Memory and Custom Prompts
#
#        ```python
#        from pySimple.pyChat import chatAI, setID, setPrompt
#
#        # Set up the conversation
#        setID("travel_advisor")
#        setPrompt("You are a travel advisor who gives concise recommendations.")
#
#        # Have a conversation with memory and custom prompt
#        response1 = chatAI("I'm planning a trip to Paris", m=True, p=True)
#        print(response1)
#
#        response2 = chatAI("What should I see there?", m=True, p=True)
#        print(response2)
#        ```
####################################################################################################
