// Notice that trainloop logging should be setup via --require flag in package.json script
import { trainloopTag } from 'trainloop-llm-logging';
import { makeAiRequest } from './aiRequest';

// Example usage
async function main() {
    const sentence = "I love strawberries";
    const promptText = `
Count the occurrences of each letter in the following sentence: <sentence>${sentence}</sentence>.
Output your answer in a code block with each letter and its count on a separate line.
Use the exact format: <letter> - <count>
Only include letters that appear in the word.
Sort the letters alphabetically.
`;

    // Tag this request for the letter counting evaluation suite
    const headers = trainloopTag("letter-counting");
    const response = await makeAiRequest(promptText, "gpt-4o-mini", 500, headers);
    
    if (response) {
        console.log("AI Response:", response);
    }
    process.exit(0);
}

if (require.main === module) {
    main().catch(console.error);
}