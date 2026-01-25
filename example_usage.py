"""
Example Usage - Customer Support AI with Escalation
--------------------------------------------------

This file demonstrates:
1. Agent conversation
2. Tool usage
3. Memory behavior
4. Escalation decision
5. AI → Human handoff simulation

Run:
    python example_usage.py
"""

import logging
from termcolor import colored

from agent import CustomerSupportAgent
from escalation_manager import EscalationManager
from utils import setup_logging, create_ticket_payload

# --------------------------------------------------
# Setup logging
# --------------------------------------------------

setup_logging()
logger = logging.getLogger(__name__)


def demo_normal_conversation():
    print(colored("\n=== DEMO 1: Normal AI Conversation ===", "cyan", attrs=["bold"]))

    agent = CustomerSupportAgent()
    message = "How can I reset my account password?"

    response = agent.chat(message)

    print(colored("User:", "yellow"), message)
    print(colored("AI:", "green"), response)


def demo_tool_usage():
    print(colored("\n=== DEMO 2: Tool Usage ===", "cyan", attrs=["bold"]))

    agent = CustomerSupportAgent()
    message = "Calculate my last bill if I paid 1200 taka for 3 months"

    response = agent.chat(message)

    print(colored("User:", "yellow"), message)
    print(colored("AI:", "green"), response)


def demo_memory_behavior():
    print(colored("\n=== DEMO 3: Memory Behavior ===", "cyan", attrs=["bold"]))

    agent = CustomerSupportAgent()

    agent.chat("My name is Rahim")
    response = agent.chat("What is my name?")

    print(colored("AI:", "green"), response)


def demo_escalation_flow():
    print(colored("\n=== DEMO 4: Escalation Trigger ===", "cyan", attrs=["bold"]))

    agent = CustomerSupportAgent()
    escalator = EscalationManager()

    user_message = "I want a refund, this service is terrible!"

    decision = escalator.should_escalate(user_message)

    print(colored("User:", "yellow"), user_message)
    print(colored("Escalation Decision:", "red"), decision)

    if decision["escalate"]:
        ticket = create_ticket_payload(
            user_message=user_message,
            reason=decision["reason"],
            session_id="demo-session-001",
        )
        print(colored("\n🚨 Escalated to Human Support", "red", attrs=["bold"]))
        print(ticket)
    else:
        response = agent.chat(user_message)
        print(colored("AI:", "green"), response)


def demo_full_conversation():
    print(colored("\n=== DEMO 5: Full Conversation Flow ===", "cyan", attrs=["bold"]))

    agent = CustomerSupportAgent()
    escalator = EscalationManager()

    conversation = [
        "Hello",
        "I cannot login to my account",
        "This is very frustrating",
        "I want to talk to a human agent",
    ]

    for msg in conversation:
        print(colored("\nUser:", "yellow"), msg)

        decision = escalator.should_escalate(msg)

        if decision["escalate"]:
            ticket = create_ticket_payload(
                user_message=msg,
                reason=decision["reason"],
                session_id="conversation-007",
            )
            print(colored("🚨 Escalated:", "red"), ticket)
            break
        else:
            reply = agent.chat(msg)
            print(colored("AI:", "green"), reply)


def main():
    print(colored("\n=========================================", "magenta", attrs=["bold"]))
    print(colored(" CUSTOMER SUPPORT AI - EXAMPLE USAGE ", "magenta", attrs=["bold"]))
    print(colored("=========================================", "magenta", attrs=["bold"]))

    demo_normal_conversation()
    demo_tool_usage()
    demo_memory_behavior()
    demo_escalation_flow()
    demo_full_conversation()

    print(colored("\nAll demos completed successfully ✔", "green", attrs=["bold"]))
    print(colored("Next: Run streamlit app for full UI 🚀", "cyan"))


if __name__ == "__main__":
    main()
