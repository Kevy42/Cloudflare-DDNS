import requests
import time
from Settings import Settings
from Logger import Logger





class Cloudflare:
    
    # Domain record identifier. Located in the 'id' key.
    RecordIdentifier = None
    
    CachedDomainRecordIp = None
    TimeOfCaching = 514862620


    @staticmethod
    def Epochs():
        return int(time.time())

    @classmethod
    def UpdateCache(cls, NewIp):
        cls.CachedDomainRecordIp = NewIp
        cls.TimeOfCaching = cls.Epochs()

    @classmethod
    def GetDomainRecord(cls):

        Logger.Log.info("Getting domain record ip")

        # Check if the cached ip is stale, if not, return it.
        # if the cached ip is stale, make request to cloudflare and update cache.
        if (cls.Epochs() - cls.TimeOfCaching) < Settings.Record_Caching_Interval:
            Logger.Log.info("Using cached domain record ip")
            return cls.CachedDomainRecordIp


        # Cloudflare auth
        headers = {
            'X-Auth-Email': Settings.Auth_Email,
            'X-Auth-Key': Settings.Auth_Key
        }
        
        try:
            JsonResponse = requests.get(
                Settings.Api_Endpoint +
                Settings.Zone_ID +
                f"/dns_records?name={Settings.Domain}&type=A&proxied={Settings.Proxied}&per_page=10",
                headers=headers, timeout=30).json()


            if JsonResponse['success'] != True:
                raise Exception()

            # It should always find it as you cannot have two identical domains
            if JsonResponse['result_info']['count'] != 1 or JsonResponse['result'][0]['name'] != str.lower(Settings.Domain):
                raise Exception()


            # GetDomainRecord() is always ran before SetDomainRecord(), meaning that we can get away
            # with dynamically loading/updating the RecordIdentifier before GetDomainRecord() is ran.
            cls.RecordIdentifier = JsonResponse['result'][0]['id']

            RecordIp = JsonResponse['result'][0]['content']

            # Check if ip is valid?

        except:
            Logger.Log.error("Unable to get domain record ip")
            raise Exception()

        cls.UpdateCache(RecordIp)

        Logger.Log.info("Got domain record ip")

        return cls.CachedDomainRecordIp


    @classmethod
    def SetDomainRecord(cls, Ip):

        Logger.Log.info("Setting domain record ip")

        headers = {
            'X-Auth-Email': Settings.Auth_Email,
            'X-Auth-Key': Settings.Auth_Key,
        }

        RecordUpdateData = {
            'type': 'A',
            'name': Settings.Domain,
            'content': Ip,
            'ttl': 1,
            'proxied': Settings.Proxied,
        }


        try:
            JsonResponse = requests.put(
                Settings.Api_Endpoint +
                Settings.Zone_ID +
                '/dns_records/' +
                cls.RecordIdentifier,
                
                headers=headers,
                json=RecordUpdateData, timeout=30).json()

            if JsonResponse['success'] != True:
                raise Exception()

        except:
            Logger.Log.info("Unable to set domain record ip")
            raise Exception()

        Logger.Log.info("Domain record ip set")




