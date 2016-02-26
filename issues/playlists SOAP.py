import scws, time
time1 = time.time()
urlProt = 'https://'
urlRoot = 'hrgcm.pixelinspiration.co.uk/ContentManager/'
urlAPI = '/api/v1.3/media?wsdl'

cm = scws.ConManager(urlProt+urlRoot,'argos_api:y884ptf')

playlist_filter = scws.TObj()
playlist_filter.column       = u'name'
playlist_filter.restriction  = u'LIKE'
playlist_filter.value        = u''
pl = cm.PlaylistRS.list(searchCriteria=playlist_filter)

time2 = time.time()
print (time2 - time1) * 1000

print len(pl)
for item in pl:
    print item.name#[0]#['name']
