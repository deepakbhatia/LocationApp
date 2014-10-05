from google.appengine.ext import ndb
 
class AJob(ndb.Model):
	name = ndb.StringProperty();
	address = ndb.StringProperty();
	service = ndb.StringProperty();
	date = ndb.DateTimeProperty();
	date_posted = ndb.DateTimeProperty(auto_add_now=True);

class AWorker(ndb.Model):
	name = ndb.StringProperty();
	address = ndb.StringProperty();
	list_jobs = ndb.KeyProperty(AJob);
    

class ARoute(ndb.Model):
	latitude = ndb.GeoPtProperty(auto_list=True);
    longitude = ndb.GeoPtProperty(auto_list=True);
    zone = ndb.IntegerProperty();
    max_time = ndb.IntegerProperty();
    time_working_week_day = ndb.TimeProperty();
    time_weekend_or_holiday = ndb.TimeProperty();
    parking_type = ndb.StringProperty();#street or commuter or commercial