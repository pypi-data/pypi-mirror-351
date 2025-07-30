# Mixgarden Python SDK

```bash
pip install mixgarden
```

- Use `get_models()` to get a list of available models.
- Use `get_plugins()` to get a list of available plugins.
- Use `get_conversations()` to get a list of available conversations.
- Use `get_conversation(id)` to get a specific conversation.
- Use `chat(model, messages)` when you’re building a conversational UI, or want the platform to maintain context for you.
- Use `get_completion(model, messages)` when you need a quick, stateless generation and want absolute control over the prompt and token usage. 

```python
import os
from mixgarden import MixgardenSDK

sdk = MixgardenSDK(api_key=os.getenv("MIXGARDEN_API_KEY"))

# List available models
models = sdk.get_models()

# Stateful chat (conversation is stored server-side)
chat = sdk.chat(
    model="gpt-4o-mini",
    content="Hello mixgarden!",
    pluginId="tone-pro",
    pluginSettings={
        "emotion-type": "neutral",
        "emotion-intensity": 6,
        "personality-type": "friendly",
    },
)

# Other helper calls
plugins = sdk.get_plugins()
conversations = sdk.get_conversations()
conversation = sdk.get_conversation(conversations[0]["id"])

# Stateless, one-shot completion (OpenAI-style)
completion = sdk.get_completion(
    model= models[0]["id"],
    messages=[{"role": "user", "content": "Hi there!"}],
    maxTokens=100,
    temperature=0.7,
)

print(chat)
print(completion)
```
