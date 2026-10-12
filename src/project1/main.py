import os
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv

load_dotenv()

@tool
def calculator_tool(a:float, b:float) -> str: 
    """
    A simple calculator does basic arithemetic operations like addition, subtraction, multiplication, and division.
    """
    print("Tool has been called with inputs:")
       
    return f"The sum of {a} and {b} is {a + b}. The difference is {a - b}. The product is {a * b}. The quotient is {a / b if b != 0 else 'undefined (division by zero)'}."    

def run_app():
    print("AI Calculator App is running...")
    model = ChatAnthropic(model="claude-opus-5-5")
    tools = [calculator_tool]
    agent_executor = create_agent(tools=tools, model=model)

    print("Welcome! I am your AI assistant. How can I help you today? Type 'quit' to exit")
    print("You can ask me to perform calculations or chat with me.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        print("\nAssistant: ", end="", flush=True)

        stream = agent_executor.stream_events({"messages": [HumanMessage(content=user_input)]},version="v3")
        
        for message in stream.messages:
            for delta in message.text:
                print(delta, end="", flush=True)
           
            print()

if __name__ == "__main__":
    run_app()


    
