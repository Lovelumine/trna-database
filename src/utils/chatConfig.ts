export type ChatModelConfig = {
  active_provider: string;
  active_model: string;
  model_options: string[];
  ollama_models?: string[];
  deepseek_models?: string[];
};

export async function fetchChatModelConfig(): Promise<ChatModelConfig | null> {
  try {
    const resp = await fetch('/chat/api/models', {
      method: 'GET',
      cache: 'no-store'
    });
    if (!resp.ok) return null;
    return (await resp.json()) as ChatModelConfig;
  } catch {
    return null;
  }
}
