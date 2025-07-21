from trainloop_llm_logging import collect, trainloop_tag

collect(flush_immediately=True)

from ai_request import make_ai_request

if __name__ == "__main__":
    passive = "The quarterly report was prepared by the finance team."
    prompt = f"""Rewrite the sentence below in ACTIVE voice, preserving meaning.  
Sentence: "{passive}"
Only output the rewritten sentence."""
    headers = trainloop_tag("active-voice")
    print(make_ai_request(prompt, extra_headers=headers))
