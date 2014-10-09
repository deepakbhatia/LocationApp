from google.appengine.ext import ndb
 
class AJob(ndb.Model):
	job_id = ndb.StringProperty()
	assigned = ndb.BooleanProperty()
	address = ndb.StringProperty()
	description = ndb.StringProperty()
	skill = ndb.StringProperty()
	job_date = ndb.DateTimeProperty()
	date_posted = ndb.DateTimeProperty(auto_now_add=True)

class AWorker(ndb.Model):
	worker_id = ndb.StringProperty()
	worker_name = ndb.StringProperty()
	address = ndb.StringProperty()
	skill = ndb.StringProperty()
	list_jobs = ndb.StructuredProperty(AJob, repeated=True)

class ARoute(ndb.Model):
	job_id = ndb.StringProperty()
	speed = ndb.StringProperty()
	location = ndb.StringProperty(repeated=True)
	start_time = ndb.DateTimeProperty()
	stop_time = ndb.DateTimeProperty()
	skill = ndb.StringProperty()
class CarData(ndb.Model):
	route = ndb.StructuredProperty(ARoute)