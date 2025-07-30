# Openint

Types:

```python
from openint.types import (
    CheckConnectionResponse,
    CreateConnectionResponse,
    CreateTokenResponse,
    DeleteConnectionResponse,
    GetConnectionResponse,
    GetCurrentUserResponse,
    GetMessageTemplateResponse,
    ListConnectionConfigsResponse,
    ListConnectionsResponse,
    ListConnectorsResponse,
    ListEventsResponse,
)
```

Methods:

- <code title="post /connection/{id}/check">client.<a href="./src/openint/_client.py">check_connection</a>(id) -> <a href="./src/openint/types/check_connection_response.py">CheckConnectionResponse</a></code>
- <code title="post /connection">client.<a href="./src/openint/_client.py">create_connection</a>(\*\*<a href="src/openint/types/client_create_connection_params.py">params</a>) -> <a href="./src/openint/types/create_connection_response.py">CreateConnectionResponse</a></code>
- <code title="post /customer/{customer_id}/token">client.<a href="./src/openint/_client.py">create_token</a>(customer_id, \*\*<a href="src/openint/types/client_create_token_params.py">params</a>) -> <a href="./src/openint/types/create_token_response.py">CreateTokenResponse</a></code>
- <code title="delete /connection/{id}">client.<a href="./src/openint/_client.py">delete_connection</a>(id) -> <a href="./src/openint/types/delete_connection_response.py">DeleteConnectionResponse</a></code>
- <code title="get /connection/{id}">client.<a href="./src/openint/_client.py">get_connection</a>(id, \*\*<a href="src/openint/types/client_get_connection_params.py">params</a>) -> <a href="./src/openint/types/get_connection_response.py">GetConnectionResponse</a></code>
- <code title="get /viewer">client.<a href="./src/openint/_client.py">get_current_user</a>() -> <a href="./src/openint/types/get_current_user_response.py">GetCurrentUserResponse</a></code>
- <code title="get /ai/message_template">client.<a href="./src/openint/_client.py">get_message_template</a>(\*\*<a href="src/openint/types/client_get_message_template_params.py">params</a>) -> <a href="./src/openint/types/get_message_template_response.py">GetMessageTemplateResponse</a></code>
- <code title="get /connector-config">client.<a href="./src/openint/_client.py">list_connection_configs</a>(\*\*<a href="src/openint/types/client_list_connection_configs_params.py">params</a>) -> <a href="./src/openint/types/list_connection_configs_response.py">SyncOffsetPagination[ListConnectionConfigsResponse]</a></code>
- <code title="get /connection">client.<a href="./src/openint/_client.py">list_connections</a>(\*\*<a href="src/openint/types/client_list_connections_params.py">params</a>) -> <a href="./src/openint/types/list_connections_response.py">SyncOffsetPagination[ListConnectionsResponse]</a></code>
- <code title="get /connector">client.<a href="./src/openint/_client.py">list_connectors</a>(\*\*<a href="src/openint/types/client_list_connectors_params.py">params</a>) -> <a href="./src/openint/types/list_connectors_response.py">SyncOffsetPagination[ListConnectorsResponse]</a></code>
- <code title="get /event">client.<a href="./src/openint/_client.py">list_events</a>(\*\*<a href="src/openint/types/client_list_events_params.py">params</a>) -> <a href="./src/openint/types/list_events_response.py">SyncOffsetPagination[ListEventsResponse]</a></code>
