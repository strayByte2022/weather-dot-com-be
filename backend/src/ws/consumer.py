from aiokafka import AIOKafkaConsumer
import asyncio
import json


class KafkaWeatherConsumer:
    def __init__(self, topic: str, bootstrap_servers: str = "localhost:9092"):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="frontend-fastapi-group"
        )
        self.listeners = []

    async def start(self):
        await self.consumer.start()
        asyncio.create_task(self.consume_loop())

    async def stop(self):
        await self.consumer.stop()

    async def consume_loop(self):
        async for msg in self.consumer:
            for cb in self.listeners:
                await cb(msg.value)

    def register_listener(self, callback):
        self.listeners.append(callback)
