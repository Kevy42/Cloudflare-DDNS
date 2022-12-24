from datetime import datetime
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from MqttMessageHandler import MqttMessageHandler
from Settings import Settings
from Logger import Logger



class Mqtt():
    Client = None
    TopicBase = "CloudflareDDNS"

    @classmethod
    def Initialize(cls):

        # Initialization log not needed

        cls.Client = mqtt.Client(
            client_id=Settings.Mqtt_Client_ID,
            clean_session=True,
            transport="tcp",
            reconnect_on_failure=True)

        cls.Client.username_pw_set(Settings.Mqtt_Username, Settings.Mqtt_Password)

        # Will for home assistant availability
        cls.Client.will_set(f"{Mqtt.TopicBase}/Availability", "OFFLINE", qos=1, retain=True)


        # Is proportional to the Checking_Interval when its below 10 minutes to ensure
        # that any settings change via mqtt will be acted uppon in a timely manner during times
        # of shitty connection. It might miss one or two windows and use the prior settings,
        # but its not a major issue.

        if Settings.Checking_Interval < 600:
            ReconnectDelay = Settings.Checking_Interval
        else:
            ReconnectDelay = 600

        cls.Client.reconnect_delay_set(60, ReconnectDelay)

        # Events
        cls.Client.on_connect = cls.Connected
        cls.Client.on_disconnect = cls.Disconnected
        cls.Client.on_message = cls.MessageRecived



    @staticmethod
    def Connect():

        # Allows you to skip Initialization in main loop
        if Mqtt.Client is None:
            Mqtt.Initialize()

        # Will throw exception (i.e exit program) if initial connection to broker fails.
        # Persistently attempting to connecting to the broker really isnt needed the same
        # way persistently re-connecting (which is handled by the library itself) is,
        # as you'd want to make sure everything works correctly after firing up the script anyways.
        # Use of Mqtt.Client.on_connect_fail isnt needed either as we, again, arent being persistent.

        Logger.Log.info("Connecting to mqtt broker")
        
        try:
            Mqtt.Client.connect(Settings.Mqtt_Broker_Address, port=Settings.Mqtt_Broker_Port, keepalive=20)
            Mqtt.Client.loop_start()
        except:
            Logger.Log.critical("Unable to connect to Mqtt broker")
            raise Exception()

        # Conformation of connection logging done by the MqttConnected event.




    @staticmethod
    def Connected(client, userdata, flags, rc):

        if rc == 0:
            Logger.Log.info("Connected to Mqtt broker")

            # Subscribing and reporting availability inside the Mqtt thread because even if stuff fails,
            # it wont be critical (limited functionality only).

            Logger.Log.info("subscribing to Mqtt topic")

            # try/except technically not needed (for subscribe), as publish/subscribe (anything that has to do with performing an action)
            # that requires an internet connection) follows a queing scheme and wont throw an exception even if
            # the client wont be able to publish due to not having an internet connection.

            try:
                Mqtt.Client.subscribe(f'{Mqtt.TopicBase}/Toggle', qos=1)
                Logger.Log.info("subscribed to Mqtt topic")
            except:
                Logger.Log.error("Unable to subscribe to Mqtt topic")


            Logger.Log.info("publishing to availability (Mqtt) topic") # FIX

            try:
                Mqtt.Client.publish(f"{Mqtt.TopicBase}/Availability", "ONLINE", qos=1, retain=True)
            except:
                Logger.Log.info("Unable to publish to availability (Mqtt) topic")

            Logger.Log.info("published to availability (Mqtt) topic") # FIX
        else:
            # Logging an error and not exiting the main loop because the Mqtt loop has already started as
            # where already inside the on_connect callback, meaning it'll attempt reconnection by itself.
            Logger.Log.error("Unable to properly connect to mqtt broker")


    @staticmethod
    def Disconnected(client, userdata, rc):
        # should always be "unexpected" as you'd normally stop the script without disconnecting.
        # Treating malformed disconnections the same way as unexpected, nothing else needed as we arent disposing.
        if rc == 0: Logger.Log.error("unexpectedly disconnected from Mqtt broker")
        else: Logger.Log.error("unexpectedly disconnected from MQTT broker")


    @staticmethod
    def MessageRecived(client, userdata, message):
        Logger.Log.info("Message Recived from Mqtt broker")
        MqttMessageHandler.Handle(str(message.payload.decode("utf-8")), message.topic)


    # Custom publish abstraction for simplification
    @staticmethod
    def PublishData(WanIp):

        DateTime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # Not using the dedicated callback to avoid two publish logs. its also generally not needed
        Logger.Log.info("Publishing to Mqtt topic")

        # try/except technically not needed, as publish/subscribe (anything that has to do with performing an action)
        # that requires an internet connection) follows a queing scheme and wont throw an exception even if
        # the client wont be able to publish due to not having an internet connection.
        try:
            Mqtt.Client.publish(f"{Mqtt.TopicBase}/WanIp", WanIp, qos=1, retain=True)
            Mqtt.Client.publish(f"{Mqtt.TopicBase}/LastSuccessfulRun", DateTime, qos=1, retain=True)

            Logger.Log.info("Published to Mqtt topic")
        except:
            Logger.Log.error("Unable to publish to mqtt topic")



        