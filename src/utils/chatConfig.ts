export type ChatModelConfig = {
  active_provider: string;
  active_model: string;
  model_options: string[];
  ollama_models?: string[];
  deepseek_models?: string[];
  xiaomi_models?: string[];
};

export type ChatModelSelection = {
  activeModel: string;
  modelOptions: string[];
};

export function resolveChatModelSelection(config: ChatModelConfig | null): ChatModelSelection {
  const activeModel = String(config?.active_model || '').trim();
  const modelOptions = (Array.isArray(config?.model_options) ? config.model_options : [])
    .map((model) => String(model || '').trim())
    .filter((model, index, options) => model && options.indexOf(model) === index);

  if (activeModel && !modelOptions.includes(activeModel)) {
    modelOptions.unshift(activeModel);
  }

  return {
    activeModel: activeModel || modelOptions[0] || '',
    modelOptions
  };
}

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
