# Chat

Types:

```python
from premai.types import ChatCompletionsResponse, ChatListModelsResponse
```

Methods:

- <code title="post /api/v1/chat/completions">client.chat.<a href="./src/premai/resources/chat.py">completions</a>(\*\*<a href="src/premai/types/chat_completions_params.py">params</a>) -> <a href="./src/premai/types/chat_completions_response.py">ChatCompletionsResponse</a></code>
- <code title="get /api/v1/chat/models">client.chat.<a href="./src/premai/resources/chat.py">list_models</a>() -> <a href="./src/premai/types/chat_list_models_response.py">ChatListModelsResponse</a></code>
- <code title="get /api/v1/chat/internalModels">client.chat.<a href="./src/premai/resources/chat.py">list_models_internal</a>() -> object</code>
