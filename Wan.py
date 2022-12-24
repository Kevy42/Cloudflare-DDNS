import requests
from ipaddress import IPv4Address
import validators
from Logger import Logger


class Wan():

    # using error instead of critical for logging because program still continiues.
    # api could start working again, so exiting would potentially reduce robustness of script.
    @staticmethod
    def GetWanIp():

        Logger.Log.info("Getting wan ip")

        Ips = []

        # Each seperate so that all three will run regardless of any exceptions.
        # nothing done uppon exception as thats done further down.
        try:
            Ips.append(Wan.Api1())
        except:
            pass

        try:
            Ips.append(Wan.Api2())
        except:
            pass

        try:
            Ips.append(Wan.Api3())
        except:
            pass


        # Check if there are duplicates. if not, raise exception as more than one api has failed
        assert len(Ips) != len(set(Ips)), Logger.Log.error("Unable to get WAN ip (multi Api Faliure?)") # Change message


        # Get ip, overrule any (single) faulty api.
        Ip = max(set(Ips), key = Ips.count)


        # print which api has failed.
        for Index, ip in enumerate(Ips):
            if ip != Ip:
                Logger.Log.warning("Wan ip api faliure, using fallback api")
                # Logger.Log.info(str(Index + 1)) to get failed api


        # Check if ip is valid
        assert validators.ipv4(Ip) == True, Logger.Log.error("Unable to get WAN ip (multi Api Faliure?)")

        # Check if ip is public (it shouldn't be)
        assert IPv4Address(Ip).is_private == False, Logger.Log.error("Unable to get WAN ip (multi Api Faliure?)")


        # ADD MORE CHECKS

        Logger.Log.info("Got wan ip")

        return Ip


    # Change to include try/catch??
    @staticmethod
    def Api1():
        Response = requests.get('https://ip4.seeip.org', timeout=30).text
        return Response


    @staticmethod
    def Api2():
        Response = requests.get("https://api.ipify.org", timeout=30).text
        return Response


    @staticmethod
    def Api3():
        JsonResponse = requests.get('https://api.myip.com', timeout=30).json()
        return JsonResponse['ip']
