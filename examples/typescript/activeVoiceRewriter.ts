// Notice that trainloop logging should be setup via --require flag in package.json script
import { trainloopTag, collect } from 'trainloop-llm-logging';
collect(true);

import { makeAiRequest } from './aiRequest';

// Example usage
async function main() {
    const passive = "The quarterly report was prepared by the finance team.";
    const promptText = `Rewrite the sentence below in ACTIVE voice, preserving meaning.  
Sentence: "${passive}"
Only output the rewritten sentence.`;

    // Tag this request for the active voice evaluation suite
    const headers = trainloopTag("active-voice");
    const response = await makeAiRequest(promptText, "gpt-4o-mini", 500, headers);
    
    if (response) {
        console.log("AI Response:", response);
    }
    process.exit(0);
}

if (require.main === module) {
    main().catch(console.error);
} 