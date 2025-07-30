from typing import Any, Optional
from kafka import KafkaProducer
from .connection import KafkaInstance
from ..core.exception import exception_to_dict
from ..log import footprint


class Producer:
    """High-level Kafka producer wrapper."""
    def __init__(self, kafka_instance: KafkaInstance) -> None:
        self._producer: KafkaProducer = kafka_instance.get_producer()

    def send(
        self,
        topic: str,
        value: Any,
        key: Optional[Any] = None,
        timeout: int = 10
    ) -> None:
        """
        Send a message to Kafka, waiting up to `timeout` seconds for confirmation.
        """
        try:
            future = self._producer.send(topic, key=key, value=value)
            future.get(timeout=timeout)
        except Exception as e:
            footprint.leave(
                log_type='error',
                message=f"Failed to send message to topic {topic}",
                controller='kafka.Producer.send',
                subject='Consumer Error',
                payload={
                    'error': exception_to_dict(e),
                },
            )
