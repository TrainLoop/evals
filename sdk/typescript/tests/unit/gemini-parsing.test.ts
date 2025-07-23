import { parseRequestBody, parseResponseBody } from '../../src/instrumentation/utils';

describe('Gemini format parsing', () => {
    describe('parseRequestBody', () => {
        it('should parse Gemini request format correctly', () => {
            const geminiRequest = JSON.stringify({
                contents: [
                    {
                        role: 'user',
                        parts: [
                            {
                                text: 'You are a social media expert specializing in Twitter content. Your job is to convert any given text into an engaging, well-crafted tweet.'
                            }
                        ]
                    }
                ],
                generationConfig: {
                    temperature: 0.7,
                    maxOutputTokens: 100,
                    responseMimeType: 'text/plain'
                },
                safetySettings: [],
                tools: []
            });

            const result = parseRequestBody(geminiRequest);
            
            expect(result).toBeDefined();
            expect(result!.messages).toHaveLength(1);
            expect(result!.messages[0]).toEqual({
                role: 'user',
                content: 'You are a social media expert specializing in Twitter content. Your job is to convert any given text into an engaging, well-crafted tweet.'
            });
            expect(result!.model).toBe('gemini/unknown');
            expect(result!.modelParams).toEqual({
                temperature: 0.7,
                maxOutputTokens: 100,
                responseMimeType: 'text/plain',
                safetySettings: [],
                tools: []
            });
        });

        it('should parse Gemini request with multiple parts', () => {
            const geminiRequest = JSON.stringify({
                contents: [
                    {
                        role: 'user',
                        parts: [
                            { text: 'First part: ' },
                            { text: 'Second part' }
                        ]
                    }
                ],
                generationConfig: {
                    model: 'gemini-2.0-flash-exp',
                    temperature: 0.5
                }
            });

            const result = parseRequestBody(geminiRequest);
            
            expect(result).toBeDefined();
            expect(result!.messages[0].content).toBe('First part:  Second part');
            expect(result!.model).toBe('gemini-2.0-flash-exp');
        });

        it('should handle Gemini request without generationConfig', () => {
            const geminiRequest = JSON.stringify({
                contents: [
                    {
                        role: 'user',
                        parts: [{ text: 'Hello world!' }]
                    }
                ]
            });

            const result = parseRequestBody(geminiRequest);
            
            expect(result).toBeDefined();
            expect(result!.model).toBe('gemini/unknown');
            expect(result!.modelParams).toEqual({});
        });
    });

    describe('parseResponseBody', () => {
        it('should parse Gemini response format correctly', () => {
            const geminiResponse = JSON.stringify({
                candidates: [
                    {
                        content: {
                            parts: [
                                {
                                    text: '🌍 Hello world! Ready to connect and make amazing things happen! #HelloWorld #NewBeginnings'
                                }
                            ],
                            role: 'model'
                        },
                        finishReason: 'STOP'
                    }
                ],
                usageMetadata: {
                    promptTokenCount: 50,
                    candidatesTokenCount: 20,
                    totalTokenCount: 70
                }
            });

            const result = parseResponseBody(geminiResponse);
            
            expect(result).toBeDefined();
            expect(result!.content).toBe('🌍 Hello world! Ready to connect and make amazing things happen! #HelloWorld #NewBeginnings');
        });

        it('should parse Gemini direct text response', () => {
            const geminiResponse = JSON.stringify({
                text: 'Direct text response from Gemini'
            });

            const result = parseResponseBody(geminiResponse);
            
            expect(result).toBeDefined();
            expect(result!.content).toBe('Direct text response from Gemini');
        });

        it('should handle Gemini streaming response format', () => {
            const geminiResponse = JSON.stringify({
                candidates: [
                    {
                        text: 'Streamed response content'
                    }
                ]
            });

            const result = parseResponseBody(geminiResponse);
            
            expect(result).toBeDefined();
            expect(result!.content).toBe('Streamed response content');
        });
    });
});