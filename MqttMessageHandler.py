from Settings import Settings
from Logger import Logger

class MqttMessageHandler():

    @staticmethod
    def Handle(Message, Topic):
        if Topic == "CloudflareDDNS/Toggle":
        
            if Message == "ON":
                Logger.Log.info("Enabling ddns")
                Settings.DDNS_Enabled = True

            if Message == "OFF":
                Logger.Log.info("Disabling ddns")
                Settings.DDNS_Enabled = False