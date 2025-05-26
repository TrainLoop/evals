/* Enable auto‑completion for trainloopTag usage */

declare global {
    interface Headers {
        /** TrainLoop tag header */
        ["X-Trainloop-Tag"]?: string;
    }
}

export { };
