import re
import yaml
import random
import string
import validators

from Misc import Misc
from Logger import Logger




class Settings():

    SettingsDict = None

    # Settings variables
    Api_Endpoint = None
    Auth_Email = None
    Auth_Key = None
    Zone_ID = None
    Domain = None
    Proxied = None
    Mqtt_Enabled = None

    Mqtt_Broker_Address = None
    Mqtt_Broker_Port = None

    Mqtt_Client_ID = None
    Mqtt_Username = None
    Mqtt_Password = None
    Checking_Interval = None
    Record_Caching_Interval = None
    
    # For mqtt toggle
    # should be in misc?
    DDNS_Enabled = True


    @classmethod
    def Load(cls):
        Logger.Log.info("Loading settings")

        try:
            with open(Misc.SettingsFilename, 'r') as SettingsFileContent:
                cls.SettingsDict = yaml.load(SettingsFileContent.read(), Loader=yaml.FullLoader)
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                Logger.Log.critical("Unable to find settings file")
            else:
                Logger.Log.critical("Unable to read settings file")
                
            raise Exception()

        # Throws exceptions on its own.
        # Also Checks and generates an mqtt client id if one doesnt exist.
        cls.Validate()

        # turn minutes into seconds for rest of codebase
        cls.SettingsDict['Checking_Interval'] = cls.SettingsDict['Checking_Interval'] * 60
        cls.SettingsDict['Record_Caching_Interval'] = cls.SettingsDict['Record_Caching_Interval'] * 60

        # Load into name friendly variables
        cls.Api_Endpoint = cls.SettingsDict['Api_Endpoint']
        cls.Auth_Email = cls.SettingsDict['Auth_Email']
        cls.Auth_Key = cls.SettingsDict['Auth_Key']
        cls.Zone_ID = cls.SettingsDict['Zone_ID']
        cls.Domain = cls.SettingsDict['Domain']
        cls.Proxied = cls.SettingsDict['Proxied']
        cls.Mqtt_Enabled = cls.SettingsDict['Mqtt_Enabled']

        cls.Mqtt_Broker_Address = cls.SettingsDict['Mqtt_Broker_Address']
        cls.Mqtt_Broker_Port = cls.SettingsDict['Mqtt_Broker_Port']

        cls.Mqtt_Client_ID = cls.SettingsDict['Mqtt_Client_ID']
        cls.Mqtt_Username = cls.SettingsDict['Mqtt_Username']
        cls.Mqtt_Password = cls.SettingsDict['Mqtt_Password']
        cls.Checking_Interval = cls.SettingsDict['Checking_Interval']
        cls.Record_Caching_Interval = cls.SettingsDict['Record_Caching_Interval']

        # Is public for conveniance, which means we manually dispose
        del cls.SettingsDict

        Logger.Log.info("Settings loaded")

    @staticmethod
    def Validate():

        Logger.Log.info("Validating settings")

        SettingsYamlKeys = {
            'Api_Endpoint': str,
            'Auth_Email': str,
            'Auth_Key': str,
            'Zone_ID': str,
            'Domain': str,
            'Proxied': bool,
            'Mqtt_Enabled': bool,
            'Mqtt_Broker_Address': str,
            'Mqtt_Broker_Port': int,
            'Mqtt_Client_ID': str,
            'Mqtt_Username': str,
            'Mqtt_Password': str,
            'Checking_Interval': int,
            'Record_Caching_Interval': int
        }

        for key, type in SettingsYamlKeys.items():
            try:
                # Check if key exists
                Settings.SettingsDict[key]
            except:
                Settings.LogRaise(key)

            # Check if key value type is correct
            if isinstance(Settings.SettingsDict[key], (type)) == False:
                Settings.LogRaise(key)
            
            # Check if string based key value is empty.
            # No need to do any further checks for the other value types as the only type
            # that can be bypass the prior checks and still be problematic (e.g empty) limited to strings.
            # No need for further validation of none strings either.
            if isinstance(Settings.SettingsDict[key], (str)) and not Settings.SettingsDict[key]:
                Settings.LogRaise(key)
        
    
        # ---- Api_Endpoint validation ----
        if not validators.url(Settings.SettingsDict['Api_Endpoint'], public=True):
            Settings.LogRaise("Api_Endpoint")

        # ---- Auth_Email validation ----
        if not validators.email(Settings.SettingsDict['Auth_Email']):
            Settings.LogRaise("Auth_Email")

        # ---- Auth_Key validation ----
        if len(Settings.SettingsDict['Auth_Key']) != 37:
            Settings.LogRaise

        if re.match("^[a-z0-9]*$", Settings.SettingsDict['Auth_Key']) is None:
            Settings.LogRaise("Auth_Key")

        # ---- Zone_ID validation ----
        if len(Settings.SettingsDict['Zone_ID']) != 32:
            Settings.LogRaise("Zone_ID")

        if re.match("^[a-z0-9]*$", Settings.SettingsDict['Zone_ID']) is None:
            Settings.LogRaise("Zone_ID")
        
        # ---- Domain validation ----
        # Adding protocol identifier to make validator happy.
        if not validators.url(f"https://{Settings.SettingsDict['Domain']}/", public=True):
            Settings.LogRaise("Domain")

        # ---- Mqtt_Broker_Address validation ----
        if not validators.ipv4(Settings.SettingsDict['Mqtt_Broker_Address']):
            Settings.LogRaise("Mqtt_Broker_Address")

        # ---- Mqtt_Broker_Port validation ----
        if not validators.between(Settings.SettingsDict['Mqtt_Broker_Port'], min=0, max=65535):
            Settings.LogRaise("Mqtt_Broker_Port")
        
        # ---- Mqtt_Client_ID validation ----
        if Settings.SettingsDict['Mqtt_Client_ID'] == "GEN":
            Settings.GenerateNewMqttID()
        else:
            if len(Settings.SettingsDict['Mqtt_Client_ID']) > 64:
                Settings.LogRaise("Mqtt_Client_ID")

            if re.match("^[A-Za-z0-9]*$", Settings.SettingsDict['Mqtt_Client_ID']) is None:
                Settings.LogRaise("Mqtt_Client_ID")
        
        # ---- Mqtt_Username validation ----
        if len(Settings.SettingsDict['Mqtt_Username']) > 64:
            Settings.LogRaise("Mqtt_Username")

        if re.match("^[A-Za-z0-9]*$", Settings.SettingsDict['Mqtt_Username']) is None:
            Settings.LogRaise("Mqtt_Username")

        # ---- Mqtt_Password validation ----
        if len(Settings.SettingsDict['Mqtt_Password']) > 64:
            Settings.LogRaise("Mqtt_Password")
        
        # ---- Checking_Interval validation ----
        if not validators.between(Settings.SettingsDict['Checking_Interval'], min=1, max=1440):
            Settings.LogRaise("Checking_Interval")
        
        # ---- Record_Caching_Interval validation ----
        CacheingMultiple = Settings.SettingsDict['Record_Caching_Interval'] / Settings.SettingsDict['Checking_Interval']

        if not validators.between(CacheingMultiple, min=2.85, max=100):
            Settings.LogRaise("Record_Caching_Interval")
        
        Logger.Log.info("Settings validated")
    
    @staticmethod
    def LogRaise(string):
        Logger.Log.critical(f"Invalid setting: {string}")
        raise Exception()

    @staticmethod
    def GenerateNewMqttID():
        Logger.Log.info("No Mqtt client ID found, Generating one")

        NewMqttID = Settings.GenerateRandomString(32)
        
        try:
            with open(Misc.SettingsFilename, "r+") as SettingsFile:
                Lines = SettingsFile.readlines()

                # Manually interate through lines and replace with new ID because updating using the yaml
                # key would erase the spacing and comments in the settings.
                for index, Line in enumerate(Lines):
                    if 'Mqtt_Client_ID' in Line:
                        Lines[index] = Lines[index].replace("'GEN'", f"'{NewMqttID}'", 1)
                        break
                
                # Seek and truncate" important for erasing the old data in the file
                SettingsFile.seek(0)
                SettingsFile.writelines(Lines)
                SettingsFile.truncate()

        except Exception as e:
            # Just making sure each time we open a file.
            if isinstance(e, FileNotFoundError):
                Logger.Log.critical("Unable to find settings file")
            else:
                Logger.Log.critical("Unable to read/write to settings file")
            
            raise Exception()
        
        # Update with new MqttID
        Settings.SettingsDict['Mqtt_Client_ID'] = NewMqttID
        Logger.Log.info("New Mqtt ID generated")


    @staticmethod
    def GenerateRandomString(Length):
        return ''.join((
            random.choice(string.ascii_lowercase + string.digits)
            for i in range(Length)))




