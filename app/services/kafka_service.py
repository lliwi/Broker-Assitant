"""
Kafka Service for real-time data streaming.
Handles high-throughput, low-latency price data distribution.
"""
import json
import threading
from typing import Callable, Dict, Optional
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from flask import current_app


class KafkaService:
    """
    Service for managing Kafka producers and consumers.
    Ensures data integrity and durability for real-time price streams.
    """

    def __init__(self):
        self.producer: Optional[KafkaProducer] = None
        self.consumers: Dict[str, KafkaConsumer] = {}
        self.consumer_threads: Dict[str, threading.Thread] = {}
        self._init_producer()

    def _init_producer(self):
        """Initialize Kafka producer."""
        try:
            bootstrap_servers = current_app.config['KAFKA_BOOTSTRAP_SERVERS']
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas
                retries=3,
                max_in_flight_requests_per_connection=1  # Ensure ordering
            )
            current_app.logger.info("Kafka producer initialized")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            self.producer = None

    def publish_price_update(self, symbol: str, price_data: Dict) -> bool:
        """
        Publish real-time price update to Kafka.

        Args:
            symbol: Asset symbol
            price_data: Price data dictionary (OHLCV + timestamp)

        Returns:
            True if successful, False otherwise
        """
        if not self.producer:
            current_app.logger.warning("Kafka producer not available")
            return False

        try:
            topic = current_app.config['KAFKA_TOPIC_PRICES']

            # Add metadata
            message = {
                'symbol': symbol,
                'timestamp': price_data.get('timestamp'),
                'open': price_data.get('open'),
                'high': price_data.get('high'),
                'low': price_data.get('low'),
                'close': price_data.get('close'),
                'volume': price_data.get('volume')
            }

            future = self.producer.send(
                topic,
                key=symbol,
                value=message
            )

            # Block for 'synchronous' send
            record_metadata = future.get(timeout=10)

            current_app.logger.debug(
                f"Published price for {symbol} to partition {record_metadata.partition} "
                f"at offset {record_metadata.offset}"
            )

            return True

        except KafkaError as e:
            current_app.logger.error(f"Kafka publish error for {symbol}: {str(e)}")
            return False

    def publish_news_event(self, symbol: str, news_data: Dict) -> bool:
        """
        Publish news event to Kafka.

        Args:
            symbol: Asset symbol
            news_data: News data dictionary

        Returns:
            True if successful, False otherwise
        """
        if not self.producer:
            return False

        try:
            topic = current_app.config['KAFKA_TOPIC_NEWS']

            message = {
                'symbol': symbol,
                'timestamp': news_data.get('timestamp'),
                'title': news_data.get('title'),
                'sentiment': news_data.get('sentiment'),
                'source': news_data.get('source')
            }

            future = self.producer.send(
                topic,
                key=symbol,
                value=message
            )

            future.get(timeout=10)
            return True

        except KafkaError as e:
            current_app.logger.error(f"Kafka news publish error: {str(e)}")
            return False

    def subscribe_to_prices(self, callback: Callable[[Dict], None], symbols: Optional[list] = None):
        """
        Subscribe to price updates from Kafka.

        Args:
            callback: Function to call when message received
            symbols: Optional list of symbols to filter (None for all)
        """
        consumer_id = f"prices_{id(callback)}"

        if consumer_id in self.consumers:
            current_app.logger.warning(f"Consumer {consumer_id} already exists")
            return

        try:
            bootstrap_servers = current_app.config['KAFKA_BOOTSTRAP_SERVERS']
            topic = current_app.config['KAFKA_TOPIC_PRICES']

            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers.split(','),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                group_id='brokerassistant-price-consumers',
                auto_offset_reset='latest',
                enable_auto_commit=True
            )

            self.consumers[consumer_id] = consumer

            # Start consumer thread
            def consume():
                try:
                    for message in consumer:
                        price_data = message.value

                        # Filter by symbols if specified
                        if symbols and price_data.get('symbol') not in symbols:
                            continue

                        callback(price_data)
                except Exception as e:
                    current_app.logger.error(f"Consumer error: {str(e)}")
                finally:
                    consumer.close()

            thread = threading.Thread(target=consume, daemon=True)
            thread.start()
            self.consumer_threads[consumer_id] = thread

            current_app.logger.info(f"Started Kafka consumer {consumer_id}")

        except Exception as e:
            current_app.logger.error(f"Failed to subscribe to Kafka: {str(e)}")

    def close(self):
        """Close all Kafka connections."""
        if self.producer:
            self.producer.close()

        for consumer_id, consumer in self.consumers.items():
            consumer.close()
            current_app.logger.info(f"Closed Kafka consumer {consumer_id}")

        self.consumers.clear()
        self.consumer_threads.clear()


# Global Kafka service instance
_kafka_service: Optional[KafkaService] = None


def get_kafka_service() -> KafkaService:
    """Get or create Kafka service instance."""
    global _kafka_service
    if _kafka_service is None:
        _kafka_service = KafkaService()
    return _kafka_service
