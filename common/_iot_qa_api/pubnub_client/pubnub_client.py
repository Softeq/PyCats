import json
import logging
import os

from pubnub.crypto import PubNubCryptodome
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNOperationType, PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration


logger = logging.getLogger(__name__)


class PubnubListener(SubscribeCallback):

    def __init__(self, channel_last_message):
        self.channel_last_message = channel_last_message

    def status(self, pubnub, status):
        if status.operation in (PNOperationType.PNSubscribeOperation, PNOperationType.PNUnsubscribeOperation):
            if status.category == PNStatusCategory.PNConnectedCategory:
                logger.debug("SUBSCRIBE CHANNEL")
            elif status.category == PNStatusCategory.PNReconnectedCategory:
                logger.debug("RECONNECTED TO CHANNEL")
            elif status.category == PNStatusCategory.PNDisconnectedCategory:
                logger.debug("DISCONNECTED FROM CHANNEL")
            elif status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
                logger.debug("UNEXPECTED DISCONNECTED, try to reconnect")
                pubnub.reconnect()
                logger.debug("CHANNELS_AFTER RECCONNECT: {}".format(pubnub.get_subscribed_channels()))
            elif status.category == PNStatusCategory.PNAccessDeniedCategory:
                logger.debug("PAM ACCESS DENIED", level='debug')
        elif status.operation == PNOperationType.PNSubscribeOperation:
            if status.is_error():
                logger.debug("ERROR: {message}".format(message=status))

    def presence(self, pubnub, presence):
        logger.info("{channel} - Presence:\n {message}".format(message=json.dumps(presence.message, indent=2),
                                                               channel=presence.channel))

    def message(self, pubnub, message):
        channel = message.channel.split('.')[0] + '.'
        self.channel_last_message[channel] = message.message
        logger.info("Pubnub: {channel} - Received:\n {message}".format(message=json.dumps(message.message, indent=2),
                                                                       channel=message.channel))


class PubnubClient:
    def __init__(self, auth_key, publish_key, subscribe_key, uuid=None, log_file='temp_pubnub_log.txt'):

        def set_file_logger(file='pubnub.log', level=logging.DEBUG):
            pubnub_logger = logging.getLogger("pubnub")
            pubnub_logger.setLevel(level)
            format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
            formatter = logging.Formatter(format_string)

            handler = logging.FileHandler(file)
            handler.setLevel(level)
            handler.setFormatter(formatter)
            pubnub_logger.addHandler(handler)
            return pubnub_logger

        self.log_file = log_file
        self.logger = set_file_logger(file=self.log_file)
        uuid = auth_key if not uuid else uuid
        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = subscribe_key
        pnconfig.publish_key = publish_key
        pnconfig.auth_key = auth_key
        pnconfig.uuid = uuid
        pnconfig.daemon = True
        self.pubnub_agent = PubNub(pnconfig)

        self.channel_last_message = {
            "history": None
        }

        self.listener = PubnubListener(self.channel_last_message)
        self.pubnub_agent.add_listener(self.listener)

    def __del__(self):
        self.pubnub_agent.unsubscribe_all()
        if self.logger:
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)

    def save_log(self, path):
        if self.logger:
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)
            self.logger = None
        os.rename(self.log_file, path)

    def _callback_history(self, result, status):
        if result and result.start_timetoken:
            self.channel_last_message["history"] = result.messages[0].entry
            logger.info("History messages:\n {message}".format(
                message='\n'.join(str(msg.entry) for msg in result.messages)))

    def send_message(self, channel, message):
        self.pubnub_agent.publish().channel(channel).message(message).should_store(True).sync()

    def get_history_messages(self, channel, count):
        last_timestamp = None

        if isinstance(self.channel_last_message.get("history"), dict):
            last_timestamp = self.channel_last_message.get("history").get("event_time")

        if last_timestamp:
            self.pubnub_agent.history().channel(channel).count(count).end(last_timestamp).pn_async(
                self._callback_history)
        else:
            self.pubnub_agent.history().channel(channel).count(count).pn_async(self._callback_history)

    def subscribe_channel(self, channel):
        """
        Subscribe to pubnub channel
        :param channel: channel name
        """
        self.pubnub_agent.subscribe().channels(channel).execute()

    def unsubscribe_channel(self, channel):
        """
        Unsubscribe from pubnub channel
        :param channel: channel name
        """
        logging.info("unsubscribe channel - {channel}".format(channel=channel))
        self.pubnub_agent.unsubscribe().channels(channel).execute()

    def decrypt_pubnub_message(self, message, key):
        """
        Decrypt pubnub message
        """
        return PubNubCryptodome(self.pubnub_agent.config).decrypt(key=key, msg=message)
