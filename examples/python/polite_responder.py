from trainloop_llm_logging import collect, trainloop_tag

collect(flush_immediately=True)

from ai_request import make_ai_request

if __name__ == "__main__":
    complaint = "Your package arrived two weeks late and the box was damaged!"
    prompt = f"""You are a customer-support agent.
Reply to the following customer in ≤120 words.
Requirements:
1. Begin with a sincere apology
2. Acknowledge the specific problem
3. Offer a concrete next step or compensation
Customer: "{complaint}"
"""
    headers = trainloop_tag("polite-responder")
    print(make_ai_request(prompt, extra_headers=headers))
