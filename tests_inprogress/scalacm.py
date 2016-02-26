import json
from collections import namedtuple, OrderedDict
import requests
import random


# import time
try:
    from aeontime import DOW
except:
    DOW = ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY")

try:
    from aeonconf import config
except ImportError:
    class FalseAttr:
        def __getattr__(self, attr):
            if attr == "TEST_PRINT_CM":
                return True
            else:
                return False
    config = FalseAttr()


try:
    from aeonutils import ExtendedJSONEncoder as json2
except ImportError:
    from json import JSONEncoder as json2

API_PREFIX = "api/rest/"

API = {"distributions": "distributions",
       "playerMetadata": "playerMetadata",
       "login": "auth/login",
       "media": "media",
       "logout": "auth/logout",
       "players": "players",
       "messages": "messages",
       "templates": "templates",
       "playlists": "playlists",
       "channels": "channels",
       "states": "players/{0[uuid]}/states", 
       "storage": "storage",
       "framesetTemplates": "framesetTemplates",
       "playlistItems": "playlists/{0[id]}/items",
       "schedules": "channels/{0[id]}/schedules",
       "timeslots": "channels/{0[ch_id]}/frames/{0[fs_id]}/timeslots"}


def get_rand_str(leng=4):
    return ("%0"+str(leng)+"x")%random.randint(0, 16**leng)

def _dict2tuple(dic):
    return namedtuple('Scala', dic.keys())(*dic.values())

def prepare_slot_info(pl_id, tempName, days, normal_prio=True):
    return {"playlist": {"id": pl_id},
            "startTime": "00:00:00",
            "endTime": "24:00:00",
            "color": "#"+get_rand_str(6),
            "tempName": tempName,
            "name": tempName,
            "recurrencePattern": "WEEKLY",
            "priorityClass": "NORMAL" if normal_prio else "ALWAYS_UNDERNEATH",
            "startDate": "2015-01-01",
            "weekdays": days}

def slotname_for(ch_id):
    return "%06d-FULLWEEK-%s"%(ch_id,get_rand_str())


def prepare_args_for_schedule(fs_id, name, slots):
    return {"frames":[OrderedDict((("id", fs_id),
                                   ("name", name),
                                   ("timeslots", slots)))]}


class ScalaConnector(object):
    def __init__(self, url):
        # make sure the URL finishes with a /
        if url[-1] != "/":
            url += "/"
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': "application/json"})
        self.token = None
        self.cookie_token = None

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        return self.logout()

    def login(self, user, password):
        creds = {"username":user,
                 "password":password,
                 "networkId":0}
        info = self.post("login", creds)
        self.session.headers.update({"apiToken":info.apiToken})
        self.token = info.token
        # Note - I added the following line
        requests.utils.add_dict_to_cookiejar(self.session.cookies, {'token': self.token})

    def post(self, apiref, args=None, format=None):
        #
        if config.TEST_PRINT_CM:
            print("POST", apiref, args)
        if config.TEST_SIMULATE_CM:
            if apiref != "login":
                print("Simulating CM, nothing POSTED!")
                return
        resp = self.session.post(self.url+API_PREFIX+API[apiref].format(format),
                                 data=json.dumps(args, cls=json2))
        if config.TEST_PRINT_CM:
            print("Result", resp, resp.json())
        resp.raise_for_status()
        return resp.json(object_hook=_dict2tuple)

    def put(self, apiref, args=None, select=None, format=None): # pylint:disable=W0622
        if config.TEST_PRINT_CM:
            print("PUT", apiref, args, select, format, json.dumps(args, cls=json2))
        if config.TEST_SIMULATE_CM:
            return
        postfix = ""
        if select is not None:
            postfix = "/%s"%select
        resp = self.session.put(self.url+API_PREFIX+API[apiref].format(format)+postfix,
                                data=json.dumps(args, cls=json2))
        if config.TEST_PRINT_CM:
            print("Result", resp, resp.json())
        resp.raise_for_status()
        return resp.json(object_hook=_dict2tuple)

    def get(self, apiref, select=None, params=None, format=None):
        if config.TEST_PRINT_CM:
            print("GET", apiref, select, params)
        postfix = ""
        if select is not None:
            postfix = "/%s"%select
        if params is None:
            params={"token": self.token}
        else:
            params["token"]= self.token
        resp = self.session.get(self.url+API_PREFIX+API[apiref].format(format)+postfix,
                                params=params)
        if config.TEST_PRINT_CM:
            print("Result", resp, resp.json())
        return resp.json(object_hook=_dict2tuple)

    def get_by_id(self, apiref, objid):
        if config.TEST_PRINT_CM:
            print("GET BY ID", apiref, objid)
        resp = self.session.get(self.url+API_PREFIX+API[apiref]+"/%d"%objid)
        if config.TEST_PRINT_CM:
            print("Result", resp, resp.json())
        return resp.json(object_hook=_dict2tuple)

    def find_by_key(self, category, value, key="name", first_only=True):
        """
        find a specific Scala object using value based on passed key
        by default will only retrieve the first element and return it
        if first_only is False, will instead return a "list" of elements
        """
        filters = json.dumps({key:{"values":[value]}, "comparator":"eq"})
        params = {"fields":list(set((key, "name"))),
                  "filters": filters}
        resp = self.get(category, params=params)
        if not first_only:
            return resp.list
        if resp.count > 0:
            return resp.list[0]


    def prepare_template(self, tplname):
        def prepare_fields(fields):
            return [{"id": f.id,
                     "name": f.name,
                     "required": False,
                     "type": f.type} for f in fields]
        resp = self.find_by_key("templates", tplname)
        # find id and pull full template record
        resp = self.get("templates", select=resp.id)
        args = {"id": resp.id,
                "name": resp.name,
                "templateFields": prepare_fields(resp.templateFields)}
        return self.put("templates", select=resp.id, args=args)

    def create_playlist(self, plname):
        """
        Create a Playlist
        """
        args = {"name":plname, "playlistType":"MEDIA_PLAYLIST"}
        resp = self.post("playlists", args)
        return resp

    def find_playlist(self,pl_id):
        """
        Return PL info
        """
        resp = self.get("playlists", select=pl_id, params={"fields": ["name", "playlistItems"]})
        return resp

    def cleanup_playlist(self,pl_id):
        def prepare_remove_list(pl_items):
            items = []
            if pl_items.count>0:
                for elt in pl_items.list:
                    items.append({"id": elt.id,
                                  "deleteFlag": True,
                                  "media": {"id": elt.media.id, "mediaType": elt.media.mediaType},
                                  "mediaType": elt.media.mediaType})
            return items
        # find playlist info
        pl_items = self.get("playlistItems", format={"id": pl_id})
        # find name
        resp = self.get("playlists", select=pl_id, params={"fields": ["name"]})
        pl_name = resp.name
        # prepare args
        args = {"id": pl_id,
                "name": pl_name,
                "playlistItems": prepare_remove_list(pl_items)}
        resp = self.put("playlists", select=pl_id, args=args)
        return pl_name


    def update_playlist(self, pl_id, media_ids, is_message=False,
                        header_media=None, footer_media=None):
        """
        Update a playlist
        """
        # clean up the list
        pl_name = self.cleanup_playlist(pl_id)

        mediatype = {False: "MEDIA", True: "MESSAGE"}[is_message]

        def make_pl_item_list(media_ids, header_media=None, footer_media=None):
            items = []
            sort_order = 1
            if header_media:
                items.append({"media": {"id": header_media},
                              "mediaType": "MEDIA",
                              "sortOrder": sort_order})
                sort_order += 1
            for m_id in media_ids:
                items.append({"media": {"id": m_id},
                              "mediaType": mediatype,
                              "sortOrder": sort_order})
                sort_order += 1
            if footer_media:
                items.append({"media": {"id": footer_media},
                              "mediaType": "MEDIA",
                              "sortOrder": sort_order})
            return items

        pl_items = make_pl_item_list(media_ids,
                                     header_media,
                                     footer_media)
        args = {"id": pl_id,
                "name": pl_name,
                "playlistItems": pl_items}

        resp = self.put("playlists", select=pl_id, args=args)
        return resp

    def create_channel(self, name, fs_id, int_vars = None):
        """
        Create an audiovisual channel
        """
        args = {"name": name,
                "type": "AUDIOVISUAL",
                "playDedicatedAudioTrack": False,
                "frameset": {"id": fs_id}}
        
        resp = self.post("channels", args)

        if int_vars:
            varinfos = []
            for varname in int_vars:
                varinfos.append({"name": "Channel."+varname,
                                 "sharedName": varname,
                                 "type": "INTEGER",
                                 "controlScript": {"id": -1}})
            args = {"id": resp.id,
                    "type": resp.type,
                    "variables": varinfos}
            self.put("channels", select=resp.id, args=args)

        return resp

    def set_channel_var(self, ch_id, varname, vartype="INTEGER", control_script=-1):
        resp = self.get("channels", select=ch_id)
        args = {"id": ch_id,
                "type": resp.type,
                "variables": [{"name": "Channel."+varname,
                               "sharedName": varname,
                               "type":vartype,
                               "controlScript": {"id": control_script}}]}
        return self.put("channels", select= ch_id, args=args)

    def set_non_scheduled_playlist(self, ch_id, future_pl_id):
        args = {"nonScheduledPlaylist": {"id": future_pl_id}}
        return self.put("schedules", args=args, format={"id": ch_id})

    def create_main_timeslots(self, ch_id, fs_id,
                              dow_pl_ids_dict, nosched_id):
        slots = []
        for day in DOW:
            # create all the playlists for the player
            # create a slot and set the playlist
            day_id_info = dow_pl_ids_dict[day]
            slot = prepare_slot_info(day_id_info["id"],
                                     day_id_info["name"],
                                     [day])
            slots.append(slot)
        fullweekslot = prepare_slot_info(nosched_id,
                                         slotname_for(ch_id),
                                         DOW,
                                         False)
        slots.append(fullweekslot)

        args = prepare_args_for_schedule(fs_id, "Main", slots)
        return self.put("schedules", args=args, format={"id": ch_id})

    def create_control_timeslot(self, ch_id, fs_id, ctrl_pl_id):
        slot = [{"playlist": {"id": ctrl_pl_id},
                 "startTime": "00:00:00",
                 "endTime": "24:00:00",
                 "color": "#"+get_rand_str(6),
                 "tempName": "CONTROL"+get_rand_str(),
                 "recurrencePattern": "WEEKLY",
                 "priorityClass": "NORMAL",
                 "startDate": "2015-01-01",
                 "weekdays": DOW}]
        args = prepare_args_for_schedule(fs_id, "CONTROL", slot)
        resp = self.put("schedules", args=args, format={"id": ch_id})
        return resp

    def read_back_timeslots(self,ch_id,fs_id):
        params = { "fromDate": "2015-01-01" }
        resp = self.get("timeslots",
                        params=params,
                        format={"ch_id": ch_id, "fs_id": fs_id})
        return resp

    def update_timeslot_time(self, ch_id, fs_id,
                             timeslot_id, pl_id, day_name,
                             time_in, time_out):
        slot = [{ "id": timeslot_id,
#                  "playlist": {"id": pl_id},
                  "startTime": time_in,
                  "endTime": time_out,
                  "recurrencePattern": "WEEKLY",
                  "startDate": "2015-01-01",
                  "weekdays": [day_name] }]
        args = prepare_args_for_schedule(fs_id, "Main", slot)
        resp = self.put("schedules", args=args, format={"id": ch_id})
        return resp

    def create_player(self,name,ch_id, power_onoff=None, polling_time=1):
        """
        power_onoff expected to be of ((power_on_metadata_id, power_on_time string),
                                        (power_off etc...))
        """
        resp=self.find_by_key("distributions","Main")
        dist_id = resp.id
        args = {"name": name,
                "distributionServer": {"id": dist_id},
                "type": "SCALA"}
        player=self.post("players",args )
        # get a player id
        if power_onoff is None:            
            powerargs = []
        else:
            powerargs=[{ "playerMetadata": {"id": mid, "name": mname, "valueType": "ANY", "datatype": "STRING"}, "value": mvalue} for mid,mname,mvalue in power_onoff]

        # (was fun while it lasted)
        displayargs = {"channel": {"id": ch_id},
                       "screenCounter":1 }
        player_args = {"id": player.id, "name": name,
                       "playerDisplays": displayargs,
                       "metadataValue": powerargs,
                       "pollingInterval" : 15,
                       "pollingUnit" : "MINUTES"}

        resp = self.put("players", args=player_args, select=player.id)
        return player

    def create_message(self, name, tpl_id, fields):
        """
        Creates a message with name "name" using the template "tpl_id"
        and setting the "fields"
        """
        msg_args = {"name": name, "template": {"id": tpl_id}, "fields": [{"name":x, "value": y} for x,y in fields.items()]}
        resp = self.post("messages", msg_args)
        return resp

    def player_status(self):
        args = {"fields": {}}
        players = self.get("players", params=args)
        if not players.count:
            return None
        ids = [pl_info.id for pl_info in players.list]
        args = {"ids": ids}
        resp = self.post("storage", args=args)
        return self.get("states", format={"uuid": resp.value})

    def logout(self):
        if self.token:
            self.get("logout", params={"token": self.token})

    