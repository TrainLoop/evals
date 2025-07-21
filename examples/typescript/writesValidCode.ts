// Notice that trainloop logging should be setup via --require flag in package.json script
import { trainloopTag } from 'trainloop-llm-logging';
import { makeAiRequest } from './aiRequest';

// Example usage
async function main() {
    const promptText = `Write a Python function that calculates the factorial of a number recursively. 
The function should be named 'factorial' and take one parameter 'n'. 
It should return 1 if n is 0 or 1, and n * factorial(n-1) otherwise.
Include proper error handling for negative numbers.
Output only the code in a single code block, no explanations.`;

    // Tag this request for the code generation evaluation suite
    const headers = trainloopTag("code-generation");
    const response = await makeAiRequest(promptText, "gpt-4o-mini", 500, headers);
    
    if (response) {
        console.log("AI Response:", response);
    }
}

if (require.main === module) {
    main().catch(console.error);
}