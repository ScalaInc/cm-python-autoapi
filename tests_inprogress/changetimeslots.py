# Defect test

import scalacm

#cms = scalacm.ScalaConnector("http://ium-lab001.cloudapp.net:8081/CM/")
#cms.login("apiuser", "apiuser123:")

cms = scalacm.ScalaConnector("http://192.168.10.245:8080/ContentManager/")
cms.login("administrator", "scala123")


try:
    resp = cms.find_by_key("channels", "TEST TIMESLOT ISSUE CHANNEL")
    ch_id = resp.id
except Exception as e:
    resp = cms.find_by_key("framesetTemplates", "Fullscreen 1920x1080")
    fs_id = resp.id
    resp = cms.create_channel("TEST TIMESLOT ISSUE CHANNEL", fs_id)
    ch_id = resp.id

# get the channel
channel = cms.get("channels", select=ch_id)
fs = channel.frameset.frames[0]
fs_name = fs.name
fs_id = fs.id


try:
    resp = cms.find_by_key("playlists", "TEST TIMESLOT ISSUE PLAYLIST")
    pl_id = resp.id
except Exception as e:
    resp = cms.create_playlist("TEST TIMESLOT ISSUE PLAYLIST")
    pl_id = resp.id

slots = []
DOW =  ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY")
for day in DOW:
    # create all the playlists for the player
    # create a slot and set the playlist
    slot = scalacm.prepare_slot_info(pl_id, day, [day])
    slots.append(slot)
args = scalacm.prepare_args_for_schedule(fs_id, fs_name, slots)

try:
    cms.put("schedules", args=args, format={"id": ch_id})
except:
    pass

frameslots = cms.read_back_timeslots(ch_id, fs_id)

for day, slot in zip(DOW, frameslots.timeslots):
    for i in range(10):
        print(i)
        cms.update_timeslot_time(ch_id, fs_id,
                                 slot.id, pl_id, day,
                                 "10:00:00", "20:00:00")
    
