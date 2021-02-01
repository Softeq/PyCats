import json
import logging

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from common._libs.helpers.singleton import Singleton, delete_singleton_object, get_singleton_instance

logger = logging.getLogger(__name__)


class AWSIotClient(metaclass=Singleton):

    def __init__(self, certs, client_id, endpoint):
        """
        Client to create AWSIot connection and communicate with subscribed topics

        Attributes:
            certs (str): Path to directory with certificates required for TLS authentication:
                rootCA.crt, thing_cert.crt, thing_private.key
            client_id (str): client identifier used to connect to AWS IoT.
            endpoint (str): The URL endpoint of the AWS IoT Gateway to which the client will connect.

        Sample of using:

            def send_aws_message(target_topic, message):
                aws_client = AWSIotClient(certs="path_to_cert_dir",
                                          client_id="999999999_stage",
                                          endpoint="test_endpoint.amazonaws.com")
                aws_client.subscribe(topic)
                aws_client.publish(topic, message)
        """
        self.certs = certs
        self.client_id = client_id
        self.endpoint = endpoint

        self.client = AWSIoTMQTTClient(client_id)
        # @todo: add timeouts to config files
        self.client.configureConnectDisconnectTimeout(10)
        self.client.configureMQTTOperationTimeout(5)
        self.connection()

        self.received_messages = dict()
        self.subscribed_topics = list()

    def __del__(self):
        if get_singleton_instance(AWSIotClient):
            self.disconnect()
            delete_singleton_object(AWSIotClient)

    def connection(self):
        self.client.configureEndpoint(self.endpoint, 443)
        self.client.configureCredentials(CAFilePath=self.certs["rootCA"],
                                         KeyPath=self.certs["thing_private"],
                                         CertificatePath=self.certs["thing_cert"])

        logger.info("Connect AWS client - {}".format(self.client_id))
        self.client.connect(30)

    def disconnect(self):
        logger.info("Disconnect AWS client - {}".format(self.client_id))
        self.client.disconnect()

    # callback to receive message
    def receive_message_callback(self, client, userdata, message):
        logger.debug("AWSIot: ['{0}'] Received a new message: '{1}'".format(message.topic, message.payload))
        if message.topic in self.received_messages.keys():
            self.received_messages[message.topic].append(json.loads(message.payload.decode('utf-8')))
        else:
            self.received_messages.update({message.topic: [json.loads(message.payload.decode('utf-8'))]})

    def clear_history_messages(self, topic=None):
        if topic is None:
            for topic in self.received_messages.keys():
                self.received_messages[topic] = []
        else:
            self.received_messages[topic] = []

    def get_history_messages(self, topic):
        return self.received_messages.get(topic)

    def get_last_message(self, topic):
        if topic in self.received_messages.keys() and len(self.received_messages[topic]) > 0:
            return self.received_messages.get(topic)[-1]

    def subscribe(self, topic):
        if topic not in self.received_messages.keys():
            logger.info("Subscribe to AWSIot topic - {}".format(topic))
            self.received_messages.update({topic: []})
            result = self.client.subscribe(topic=topic, QoS=1, callback=self.receive_message_callback)
            assert result is True, "failed on subscribe to '{}' topic".format(topic)

    def unsubscribe(self, topic):
        logger.info("Unsubscribe from AWSIot topic - {}".format(topic))
        result = self.client.subscribe(topic=topic, QoS=1, callback=self.receive_message_callback)
        assert result is True, "failed on unsubscribe from '{}' topic".format(topic)

    def publish(self, topic, message):
        command = json.dumps(message)
        logger.info("Publish message '{0}' to AWSIot topic - {1}".format(message, topic))
        result = self.client.publish(topic=topic, payload=command, QoS=1)
        assert result is True, "failed on publishing message '{0}' in '{1}' topic".format(command, topic)
