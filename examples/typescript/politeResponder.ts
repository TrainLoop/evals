// Notice that trainloop logging should be setup via --require flag in package.json script
import { trainloopTag, collect } from 'trainloop-llm-logging';
collect(true);

import { makeAiRequest } from './aiRequest';

// Example usage
async function main() {
    const complaint = "Your package arrived two weeks late and the box was damaged!";
    const promptText = `You are a customer-support agent.
Reply to the following customer in ≤120 words.
Requirements:
1. Begin with a sincere apology
2. Acknowledge the specific problem
3. Offer a concrete next step or compensation
Customer: "${complaint}"`;

    // Tag this request for the polite responder evaluation suite
    const headers = trainloopTag("polite-responder");
    const response = await makeAiRequest(promptText, "gpt-4o-mini", 500, headers);
    
    if (response) {
        console.log("AI Response:", response);
    }
    process.exit(0);
}

if (require.main === module) {
    main().catch(console.error);
} 