# vyomcloudbridge/queue_worker.py
import base64
import threading
import time
import copy
from typing import Dict, Any
from vyomcloudbridge.services.vyom_sender import VyomSender
from vyomcloudbridge.services.rabbit_queue.queue_main import RabbitMQ
from vyomcloudbridge.services.rabbit_queue.queue_main_thread import ThreadedRabbitMQ
from vyomcloudbridge.utils.common import ServiceAbstract, parse_bool
from vyomcloudbridge.utils.configs import Configs
from vyomcloudbridge.services.mission_stats import MissionStats
from vyomcloudbridge.constants.constants import data_buffer_key


class QueueWorker(ServiceAbstract):
    """
    Worker class that handles rabbit_mq consumption and message publishing.
    Inherits from ServiceAbstract for consistent service management.
    """

    def __init__(self, multi_thread: bool = False):
        try:
            super().__init__(multi_thread=multi_thread)
            self.logger.info("QueueWorker initializing...")
            self.rabbit_mq = (
                ThreadedRabbitMQ() if parse_bool(multi_thread) else RabbitMQ()
            )
            self.mission_stats = MissionStats()
            self.vyom_sender = None
            self.fail_client_pausetime = 3
            self.logger.info("QueueWorker initialized successfully!")
            self.upload_stats = {}
            self._upload_stats_lock = threading.Lock()
            self.upload_stats_publish_interval = 120
            self.upload_stats_error_delay = 300
        except Exception as e:
            self.logger.error(f"Error initializing QueueWorker: {str(e)}")
            raise

    def _setup_connection(self) -> None:
        """Setup connection and channel with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info("QueueWorker setting VyomSender...")
                self.vyom_sender = VyomSender()
                self.logger.info("VyomSender connection established")
                return  # Exit the method on success
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.fail_client_pausetime)
                else:
                    self.logger.error(
                        "Failed to establish VyomSender connection after 3 attempts"
                    )
                    raise

    def proccess_deque_message(self, message: Dict[str, Any]) -> bool:
        """
        Returns:
            bool: True if publishing successful, False otherwise
        """
        try:
            self.logger.info("proccess_deque_message called")
            message_type = message["message_type"] or False
            topic = message["topic"]
            data_source = message["data_source"]
            destination_ids = message["destination_ids"]

            data = message.get("data", None)
            data = base64.b64decode(data) if message_type == "binary" else data
            self.logger.info(f"found data-{topic}")
            result = self.vyom_sender.send_message(
                data, message_type, destination_ids, data_source, topic
            )
            if result:
                try:
                    buffer_key = message.get("buffer_key", None)
                    upload_size = message.get("buffer_size", 0)
                    data_type = message.get("data_type", 0)
                    if buffer_key and upload_size:
                        with self._upload_stats_lock:
                            if buffer_key not in self.upload_stats:
                                self.upload_stats[buffer_key] = {
                                    "size": upload_size,
                                    "file_count": 1,
                                    "data_type": data_type,
                                    "data_source": data_source,
                                }
                            else:
                                self.upload_stats[buffer_key]["size"] += upload_size
                                self.upload_stats[buffer_key]["file_count"] += 1
                                self.upload_stats[buffer_key]["data_type"] = data_type
                                self.upload_stats[buffer_key][
                                    "data_source"
                                ] = data_source

                except Exception as e:
                    self.logger.warning(f"Error updating upload stats: {e}")
                    pass
                # if message.get("buffer_key", None) != data_buffer_key:
                #     try:
                #         mission_id = int(message.get("buffer_key", None))
                #         buffer_size = message.get("buffer_size", 0)
                #         data_type = message.get("data_type", 0)
                #         if buffer_size:
                #             self.mission_stats.on_mission_data_publish(
                #                 mission_id=mission_id,
                #                 size=buffer_size,
                #                 file_count=1,
                #                 data_type=data_type,
                #                 data_source=data_source,
                #             )
                #     except Exception as e:
                #         pass
            else:
                self.logger.error(f"Message proccesing failed")
            return result

        except Exception as e:
            self.logger.error(f"error in publishing message: {e}")
            return False

    def _ensure_connection(self) -> bool:
        try:
            self.logger.info("Starting QueueWorker _ensure_connection called")
            if not self.vyom_sender:
                self._setup_connection()
            self.logger.info("Starting QueueWorker _ensure_connection completed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to ensure vyom sender connection: {e}")
            return False

    def _publish_upload_stats(self):
        """
        Publish upload stats to the vyom sender.
        """
        try:
            if not self.upload_stats:
                self.logger.info("No upload stats to publish")
                return
            with self._upload_stats_lock:
                upload_stats_copy = copy.deepcopy(self.upload_stats)
                self.upload_stats.clear()

            self.logger.info("Publishing upload stats to vyom sender")
            for buffer_key, stats in upload_stats_copy.items():
                size = stats["size"]
                file_count = stats["file_count"]
                data_type = stats["data_type"]
                data_source = stats["data_source"]
                self.mission_stats.on_mission_data_publish(
                    mission_id=buffer_key,
                    size=size,
                    file_count=file_count,
                    data_type=data_type,
                    data_source=data_source,
                )
        except Exception as e:
            self.logger.error(f"Error publishing upload stats: {e}")

    def start(self):
        """Start publishing messages from the rabbit_mq."""
        try:
            self.logger.info("Starting QueueWorker service...")
            if not self._ensure_connection():
                raise Exception("Could not establish vyom sender connection")
            self.is_running = True

            def upload_publisher_loop():
                while self.is_running:
                    try:
                        self._publish_upload_stats()
                        time.sleep(self.upload_stats_publish_interval)
                    except Exception as e:
                        self.logger.error(f"Error in stats publisher loop: {str(e)}")
                        time.sleep(self.upload_stats_error_delay)

            self.data_listing_thread = threading.Thread(
                target=upload_publisher_loop, daemon=True
            )
            self.data_listing_thread.start()

            self.logger.info("Started QueueWorker service!")
            self.rabbit_mq.start_consume(self.proccess_deque_message)

            while self.is_running:
                time.sleep(10)

        except Exception as e:
            self.logger.error(f"Error in starting QueueWorker: {e}")
            raise
        finally:
            self.stop()

    def stop(self):
        """Stop resources and connections."""
        try:
            self.logger.info("Stopping QueueWorker service...")
            if self.is_running:
                self.is_running = False
                if self.rabbit_mq:
                    self.rabbit_mq.close()
                if self.vyom_sender:
                    self.vyom_sender.cleanup()
                if self.mission_stats:
                    self.mission_stats.cleanup()
                self.logger.info("Stopped QueueWorker service!")
            else:
                self.logger.info("QueueWorker service already stopped, skipped..")
        except Exception as e:
            self.logger.error(f"Error during stop: {e}")

    def cleanup(self):
        """cleaning resources and connections."""
        try:
            self.logger.info("cleaning QueueWorker service...")
            self.is_running = False
            if self.rabbit_mq:
                self.rabbit_mq.stop_consume()
                self.rabbit_mq.close()
            if self.vyom_sender:
                self.vyom_sender.cleanup()
            if self.mission_stats:
                self.mission_stats.cleanup()
            self.logger.info("Cleaned QueueWorker service!")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def is_healthy(self):
        """
        Override health check to add additional service-specific checks.
        """
        return self.is_running and self.vyom_sender is not None

    def __del__(self):
        """Destructor called by garbage collector to ensure resources are cleaned up, when object is about to be destroyed"""
        try:
            self.logger.error(
                "Destructor called by garbage collector to cleanup QueueWorker"
            )
            self.cleanup()
        except Exception as e:
            pass


def main():
    """
    Main entry point for the queue worker service.
    """
    service = QueueWorker()
    try:
        service.start()

        # Keep the main thread running
        while service.is_running:
            time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        service.stop()


if __name__ == "__main__":
    main()
