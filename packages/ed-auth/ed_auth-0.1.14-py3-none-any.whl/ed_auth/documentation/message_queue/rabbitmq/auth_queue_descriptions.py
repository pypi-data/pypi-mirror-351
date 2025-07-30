from ed_domain.documentation.message_queue.rabbitmq.abc_queue_descriptions import (
    ABCQueueDescriptions, AuthQueues)
from ed_domain.documentation.message_queue.rabbitmq.definitions.queue_description import \
    QueueDescription

from ed_auth.application.features.auth.dtos import (CreateUserDto,
                                                    DeleteUserDto,
                                                    UpdateUserDto)


class AuthQueueDescriptions(ABCQueueDescriptions):
    def __init__(self, connection_url: str) -> None:
        self._descriptions: list[QueueDescription] = [
            {
                "name": AuthQueues.CREATE_USER,
                "connection_parameters": {
                    "url": connection_url,
                    "queue": AuthQueues.CREATE_USER,
                },
                "durable": True,
                "request_model": CreateUserDto,
            },
            {
                "name": AuthQueues.DELETE_USER,
                "connection_parameters": {
                    "url": connection_url,
                    "queue": AuthQueues.DELETE_USER,
                },
                "durable": True,
                "request_model": DeleteUserDto,
            },
            {
                "name": AuthQueues.UPDATE_USER,
                "connection_parameters": {
                    "url": connection_url,
                    "queue": AuthQueues.UPDATE_USER,
                },
                "durable": True,
                "request_model": UpdateUserDto,
            },
        ]

    @property
    def descriptions(self) -> list[QueueDescription]:
        return self._descriptions
