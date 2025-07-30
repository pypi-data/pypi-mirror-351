# ActionTypeConfigs

Types:

```python
from bem.types import (
    ActionType,
    ActionTypeConfig,
    ActionTypeConfigBase,
    ActionTypeConfigCreateBase,
    ActionTypeConfigUpsertBase,
    RouteListItem,
    SplitConfigSemanticPageItemClass,
    UpsertEmailConfig,
    UpsertJoinConfig,
    UpsertRouteConfig,
    UpsertSplitConfig,
    UpsertTransformConfig,
    ActionTypeConfigListResponse,
)
```

Methods:

- <code title="post /v1-alpha/action-type-configs">client.action_type_configs.<a href="./src/bem/resources/action_type_configs.py">create</a>(\*\*<a href="src/bem/types/action_type_config_create_params.py">params</a>) -> <a href="./src/bem/types/action_type_config.py">ActionTypeConfig</a></code>
- <code title="get /v1-alpha/action-type-configs/{actionTypeConfigID}">client.action_type_configs.<a href="./src/bem/resources/action_type_configs.py">retrieve</a>(action_type_config_id) -> <a href="./src/bem/types/action_type_config.py">ActionTypeConfig</a></code>
- <code title="patch /v1-alpha/action-type-configs/{actionTypeConfigID}">client.action_type_configs.<a href="./src/bem/resources/action_type_configs.py">update</a>(action_type_config_id, \*\*<a href="src/bem/types/action_type_config_update_params.py">params</a>) -> <a href="./src/bem/types/action_type_config.py">ActionTypeConfig</a></code>
- <code title="get /v1-alpha/action-type-configs">client.action_type_configs.<a href="./src/bem/resources/action_type_configs.py">list</a>(\*\*<a href="src/bem/types/action_type_config_list_params.py">params</a>) -> <a href="./src/bem/types/action_type_config_list_response.py">ActionTypeConfigListResponse</a></code>
- <code title="delete /v1-alpha/action-type-configs/{actionTypeConfigID}">client.action_type_configs.<a href="./src/bem/resources/action_type_configs.py">delete</a>(action_type_config_id) -> None</code>

# Actions

Types:

```python
from bem.types import (
    ActionBase,
    ActionCreateBase,
    CreateActionBase,
    EmailActionBase,
    GetActionsResponse,
    JoinActionBase,
    RouteActionBase,
    SplitActionBase,
    TransformActionBase,
)
```

Methods:

- <code title="post /v1-alpha/actions">client.actions.<a href="./src/bem/resources/actions.py">create</a>(\*\*<a href="src/bem/types/action_create_params.py">params</a>) -> <a href="./src/bem/types/get_actions_response.py">GetActionsResponse</a></code>
- <code title="get /v1-alpha/actions">client.actions.<a href="./src/bem/resources/actions.py">list</a>(\*\*<a href="src/bem/types/action_list_params.py">params</a>) -> <a href="./src/bem/types/get_actions_response.py">GetActionsResponse</a></code>
- <code title="patch /v1-alpha/actions/route">client.actions.<a href="./src/bem/resources/actions.py">correct_route</a>(\*\*<a href="src/bem/types/action_correct_route_params.py">params</a>) -> None</code>

# Events

Types:

```python
from bem.types import Event, EventBase, EventListResponse
```

Methods:

- <code title="get /v1-alpha/events/{eventID}">client.events.<a href="./src/bem/resources/events.py">retrieve</a>(event_id) -> <a href="./src/bem/types/event.py">Event</a></code>
- <code title="get /v1-alpha/events">client.events.<a href="./src/bem/resources/events.py">list</a>(\*\*<a href="src/bem/types/event_list_params.py">params</a>) -> <a href="./src/bem/types/event_list_response.py">EventListResponse</a></code>

# Tasks

Types:

```python
from bem.types import Task, TaskStatus, TaskListResponse
```

Methods:

- <code title="get /v1-alpha/tasks/{taskID}">client.tasks.<a href="./src/bem/resources/tasks.py">retrieve</a>(task_id) -> <a href="./src/bem/types/task.py">Task</a></code>
- <code title="get /v1-alpha/tasks">client.tasks.<a href="./src/bem/resources/tasks.py">list</a>(\*\*<a href="src/bem/types/task_list_params.py">params</a>) -> <a href="./src/bem/types/task_list_response.py">TaskListResponse</a></code>

# Subscriptions

Types:

```python
from bem.types import Subscription, SubscriptionListResponse
```

Methods:

- <code title="post /v1-alpha/subscriptions">client.subscriptions.<a href="./src/bem/resources/subscriptions.py">create</a>(\*\*<a href="src/bem/types/subscription_create_params.py">params</a>) -> <a href="./src/bem/types/subscription.py">Subscription</a></code>
- <code title="get /v1-alpha/subscriptions/{subscriptionID}">client.subscriptions.<a href="./src/bem/resources/subscriptions.py">retrieve</a>(subscription_id) -> <a href="./src/bem/types/subscription.py">Subscription</a></code>
- <code title="patch /v1-alpha/subscriptions/{subscriptionID}">client.subscriptions.<a href="./src/bem/resources/subscriptions.py">update</a>(subscription_id, \*\*<a href="src/bem/types/subscription_update_params.py">params</a>) -> <a href="./src/bem/types/subscription.py">Subscription</a></code>
- <code title="get /v1-alpha/subscriptions">client.subscriptions.<a href="./src/bem/resources/subscriptions.py">list</a>(\*\*<a href="src/bem/types/subscription_list_params.py">params</a>) -> <a href="./src/bem/types/subscription_list_response.py">SubscriptionListResponse</a></code>
- <code title="delete /v1-alpha/subscriptions/{subscriptionID}">client.subscriptions.<a href="./src/bem/resources/subscriptions.py">delete</a>(subscription_id) -> None</code>

# Pipelines

Types:

```python
from bem.types import Pipeline, PipelineRetrieveResponse, PipelineListResponse
```

Methods:

- <code title="post /v1-beta/pipelines">client.pipelines.<a href="./src/bem/resources/pipelines.py">create</a>(\*\*<a href="src/bem/types/pipeline_create_params.py">params</a>) -> <a href="./src/bem/types/pipeline.py">Pipeline</a></code>
- <code title="get /v1-beta/pipelines/{pipelineID}">client.pipelines.<a href="./src/bem/resources/pipelines.py">retrieve</a>(pipeline_id) -> <a href="./src/bem/types/pipeline_retrieve_response.py">PipelineRetrieveResponse</a></code>
- <code title="patch /v1-beta/pipelines/{pipelineID}">client.pipelines.<a href="./src/bem/resources/pipelines.py">update</a>(pipeline_id, \*\*<a href="src/bem/types/pipeline_update_params.py">params</a>) -> <a href="./src/bem/types/pipeline.py">Pipeline</a></code>
- <code title="get /v1-beta/pipelines">client.pipelines.<a href="./src/bem/resources/pipelines.py">list</a>(\*\*<a href="src/bem/types/pipeline_list_params.py">params</a>) -> <a href="./src/bem/types/pipeline_list_response.py">PipelineListResponse</a></code>
- <code title="delete /v1-beta/pipelines/{pipelineID}">client.pipelines.<a href="./src/bem/resources/pipelines.py">delete</a>(pipeline_id) -> None</code>

# Transformations

Types:

```python
from bem.types import (
    AnyType,
    InputType,
    UpdateTransformation,
    UpdateTransformationResponse,
    TransformationCreateResponse,
    TransformationListResponse,
    TransformationDeleteResponse,
    TransformationListErrorsResponse,
)
```

Methods:

- <code title="post /v1-beta/transformations">client.transformations.<a href="./src/bem/resources/transformations.py">create</a>(\*\*<a href="src/bem/types/transformation_create_params.py">params</a>) -> <a href="./src/bem/types/transformation_create_response.py">TransformationCreateResponse</a></code>
- <code title="put /v1-beta/transformations">client.transformations.<a href="./src/bem/resources/transformations.py">update</a>(\*\*<a href="src/bem/types/transformation_update_params.py">params</a>) -> <a href="./src/bem/types/update_transformation_response.py">UpdateTransformationResponse</a></code>
- <code title="get /v1-beta/transformations">client.transformations.<a href="./src/bem/resources/transformations.py">list</a>(\*\*<a href="src/bem/types/transformation_list_params.py">params</a>) -> <a href="./src/bem/types/transformation_list_response.py">TransformationListResponse</a></code>
- <code title="delete /v1-beta/transformations">client.transformations.<a href="./src/bem/resources/transformations.py">delete</a>(\*\*<a href="src/bem/types/transformation_delete_params.py">params</a>) -> <a href="./src/bem/types/transformation_delete_response.py">TransformationDeleteResponse</a></code>
- <code title="patch /v1-beta/transformations">client.transformations.<a href="./src/bem/resources/transformations.py">deprecated_update</a>(\*\*<a href="src/bem/types/transformation_deprecated_update_params.py">params</a>) -> <a href="./src/bem/types/update_transformation_response.py">UpdateTransformationResponse</a></code>
- <code title="get /v1-beta/transformations/errors">client.transformations.<a href="./src/bem/resources/transformations.py">list_errors</a>(\*\*<a href="src/bem/types/transformation_list_errors_params.py">params</a>) -> <a href="./src/bem/types/transformation_list_errors_response.py">TransformationListErrorsResponse</a></code>

# WebhookSecret

Types:

```python
from bem.types import WebhookSecret
```

Methods:

- <code title="post /v1-beta/webhook-secret">client.webhook_secret.<a href="./src/bem/resources/webhook_secret.py">create</a>() -> <a href="./src/bem/types/webhook_secret.py">WebhookSecret</a></code>
- <code title="get /v1-beta/webhook-secret">client.webhook_secret.<a href="./src/bem/resources/webhook_secret.py">retrieve</a>() -> <a href="./src/bem/types/webhook_secret.py">WebhookSecret</a></code>
