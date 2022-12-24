from time import sleep
from Wan import Wan
from Settings import Settings
from Cloudflare import Cloudflare
from sys import exit

from Mqtt import Mqtt
from Logger import Logger



# TODO ON PI WHEN RETURNING

# 1. remove service
# 2. check rc.local
# 3. check crontab

# 4. Delete DDNS folder

# 5. uninstall
    # validators: decorator-5.1.1, validators-0.20.0
    # coloredlogs: coloredlogs-15.0.1, humanfriendly-10.0
    # paho-mqtt: paho-mqtt-1.6.1





# BETA V2.1



# settings features and validation
    # with if(mqttenabled = true): validatemqtt
    # add credential validation (cloudflare, mqtt)
    # add Cloudflare prefix to settings variables
    # make error messages as streight forward as possible
    # add warnings?


# fix disconnected keeps running loop bcuz checking interval and reconnect interval
# check if internet connection is up?
# add "last successful run"
# add assert exception message
# display what ip its getting/setting
# add a proper enabling/disabling
# print out that mqtt stuff will be queued until connection is back when connection is unavailable

if __name__ == "__main__":

    try:
        Logger.Initialize()
        Settings.Load()

        if Settings.Mqtt_Enabled == True:
            Mqtt.Connect()
    except Exception as e:
        if len(str(e)) != 0:
            Logger.Log.warning(f"None empty exception raised:\n{e}")
        quit()



    

    while True:

        try:
            if Settings.DDNS_Enabled == True:

                WanIp = Wan.GetWanIp()
                DomainIp = Cloudflare.GetDomainRecord()

                Logger.Log.info("Checking for domain/ip missmatch")

                if WanIp != DomainIp:
                    Logger.Log.info("Domain/ip missmatch found")
                    Cloudflare.SetDomainRecord(WanIp)
                else:
                    Logger.Log.info("No domain/ip missmatch found")

                if Settings.Mqtt_Enabled == True:
                    # another try/except to avoid attempting to publish outside of the main try/except.
                    try:
                        Mqtt.PublishData(WanIp)
                    except:
                        pass

            else:
                #Logger.Log.info("ddns not enabled")
                pass

        except:
            if len(str(e)) != 0:
                Logger.Log.warning(f"None empty exception raised:\n{e}")

        sleep(Settings.Checking_Interval)
        #sleep(10)









