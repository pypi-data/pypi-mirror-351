from ed_infrastructure.documentation.message_queue.rabbitmq.rabbitmq_producer import \
    RabbitMQProducer

from ed_auth.application.features.auth.dtos import (CreateUserDto,
                                                    DeleteUserDto,
                                                    UpdateUserDto)
from ed_auth.documentation.message_queue.rabbitmq.abc_auth_rabbitmq_subscriber import (
    ABCAuthRabbitMQSubscriber, AuthQueues)
from ed_auth.documentation.message_queue.rabbitmq.auth_queue_descriptions import \
    AuthQueueDescriptions


class AuthRabbitMQSubscriber(ABCAuthRabbitMQSubscriber):
    def __init__(self, connection_url: str) -> None:
        self._connection_url = connection_url
        self._queues = AuthQueueDescriptions(connection_url)

    def create_user(self, create_user_dto: CreateUserDto) -> None:
        queue = self._queues.get_queue(AuthQueues.CREATE_USER)
        producer = RabbitMQProducer[CreateUserDto](
            queue["connection_parameters"]["url"],
            queue["connection_parameters"]["queue"],
        )
        producer.start()
        producer.publish(create_user_dto)
        producer.stop()

    def delete_user(self, delete_user_dto: DeleteUserDto) -> None:
        queue = self._queues.get_queue(AuthQueues.DELETE_USER)
        producer = RabbitMQProducer[DeleteUserDto](
            queue["connection_parameters"]["url"],
            queue["connection_parameters"]["queue"],
        )
        producer.start()
        producer.publish(delete_user_dto)
        producer.stop()

    def update_user(self, update_user_dto: UpdateUserDto) -> None:
        queue = self._queues.get_queue(AuthQueues.UPDATE_USER)
        producer = RabbitMQProducer[UpdateUserDto](
            queue["connection_parameters"]["url"],
            queue["connection_parameters"]["queue"],
        )
        producer.start()
        producer.publish(update_user_dto)
        producer.stop()
