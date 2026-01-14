import { ChatRequest, StreamEvent } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const streamService = {
    streamChat: async (
        request: ChatRequest,
        onEvent: (event: StreamEvent) => void,
        onComplete: () => void,
        onError: (error: string) => void
    ) => {
        try {
            const response = await fetch(`${API_BASE_URL}/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request),
            });

            if (!response.ok) {
                throw new Error(response.statusText);
            }

            if (!response.body) {
                throw new Error('ReadableStream not supported in this browser.');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // Process buffer for SSE events
                // Format: 
                // event: <type>
                // data: <json>
                // \n\n

                const lines = buffer.split('\n\n');
                // Keep the incomplete last line in the buffer
                buffer = lines.pop() || '';

                for (const line of lines) {
                    const eventMatch = line.match(/event: (.*)\ndata: (.*)/s);
                    if (eventMatch) {
                        try {
                            // event type is match[1], but data includes internal type field
                            const data = JSON.parse(eventMatch[2]);
                            onEvent(data);
                        } catch (e) {
                            console.error("Failed to parse event", e);
                        }
                    }
                }
            }
            onComplete();

        } catch (e: any) {
            onError(e.message || String(e));
        }
    }
};
