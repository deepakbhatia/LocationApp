#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#!/usr/bin/env python
#
#
import webapp2
import json
from models import *
import datetime
from google.appengine.api import taskqueue
from google.appengine.api import search

documents_counter=0
total_docs_counter=0
documents_list=[]
TRUE = 1
FALSE = 0
DEBUG = TRUE
geopoints = []
JOB_LIMIT_DOCUMENT = 1
def geocalc(lat1, lon1, lat2, lon2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon1 - lon2

    EARTH_R = 6372.8

    y = sqrt(
        (cos(lat2) * sin(dlon)) ** 2
        + (cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)) ** 2
        )
    x = sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(dlon)
    c = atan2(y, x)
    return EARTH_R * c
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def query_result(self, index, query_string):
    try:
        # val = 2
        # val_1 = 15.7979
        # result_string="{'results':["
        # result_string +="{"
        # result_string+="'location':{ 'lat': '%s' , 'lon': '%s' }, " % (38.76817681, -9.864823)
        # #result_string+="'water_level':'%s', " % val

        # result_string+="'water_level':'%s'," % val
        # result_string+="'car_parked':'%s'," % "yes"
        # result_string+="'wiper_speed':'%s'," % val_1
        # result_string +="}"
        # result_string+="]}"

        results = index.search(query_string)
        self.response.write('In local 2')
        total_matches = results.number_found
        print total_matches
        self.response.write(total_matches)
        #document;
        # Iterate over the documents in the results
        result_string="{'results':[";
        counter=0;
        for scored_document in results:
          # handle results
          #document = scored_document
          if counter > 0:
            result_string +=","
          result_string +="{"
          if index == "job_index":
            result_string+="'location':{ 'lat': '%s' , 'lon': '%s' }, " % (scored_document.field('job_location').value.latitude, scored_document.field('job_location').value.longitude)
            result_string+="'job_id':'%s', " % (scored_document.field('job_id').value)
            result_string+="'address':'%s', " % (scored_document.field('address').value)
            result_string+="'skill':'%s', " % (scored_document.field('skill').value)
            result_string+="'description':'%s', " % (scored_document.field('description').value)
            result_string+="'job_date':'%s', " % (scored_document.field('job_date').value)
          else:
            result_string+="'location':{ 'lat': '%s' , 'lon': '%s' }, " % (scored_document.field('worker_location').value.latitude, scored_document.field('worker_location').value.longitude)
            result_string+="'worker_id':'%s', " % (scored_document.field('worker_id').value)
            result_string+="'address':'%s', " % (scored_document.field('address').value)
            result_string+="'skill':'%s', " % (scored_document.field('skill').value)
            result_string+="'worker_name':'%s', " % (scored_document.field('description').value)          
          result_string +="}"
          counter = counter+1

        result_string="]}"
        self.response.write(json.dumps(result_string))

        #   self.response.write(scored_document.field('wlocation').value.latitude)
    except search.Error:
        self.response.write('Search failed')
class QueryHandler(webapp2.RequestHandler):
    def get(self):
        query_type = self.request.get('query_type')
        latitude = self.request.get('lat')
        longitude = self.request.get('lon')
        geostring = "geopoint(%s,%s)" % (latitude,longitude)
        
        if query_type == "JOBS":
            index = search.Index(name="job_index")
            query_string = "distance(job_location, %s) < 5000" % geostring
            query = search.Query(query_string = query_string)
            query_result(self,index, query)         
        else:
            index = search.Index(name="worker_index")
            query_string = "distance(worker_location, %s) < 5000" % geostring
            query = search.Query(query_string = query_string)
            query_result(self,index, query)
            #self.response.write('NEAR_BY = %s' % geostring)
class CarDataHandler(webapp2.RequestHandler):
    def post(self):
        routes_list=[]
        water_level_list=[]
        car_id = self.request.get('car_id')
        job_id = self.request.get('job_id')
        car_speed = self.request.get('speed')
        start_time = self.request.get('start_time')
        stop_time = self.request.get('stop_time')
        start_time_val = float(long(start_time))
        stop_time_val = float(long(stop_time))
        route = self.request.get('route')
        json_route = json.loads(route)
        routes = json_route['routes']
        for each_route in routes:
            position = each_route['position']
            #lon = each_route['lon']
            #position = ndb.GeoPt(float(lat), float(lon))
            routes_list.extend([position])

        aroute = ARoute(id = job_id, job_id  = job_id, speed = car_speed, location = routes_list, 
          start_time = datetime.datetime.fromtimestamp(start_time_val),
          stop_time = datetime.datetime.fromtimestamp(stop_time_val),
          )
        aroute.put()
        
        car_data_trip = CarData(id = car_id, route = aroute)
        car_data_trip.put()
        #car_key = ndb.Key(CarData, car_id)
        #car = car_key.get()

        #car_vals = car.fetch()
        #json.dumps()
        # for eachcar in car_vals:
        #   val_dict = eachcar.route.to_dict(exclude=[start_time,stop_time])
        #   self.response.write(json.dumps(val_dict))
class GetMyCarHandler(webapp2.RequestHandler):
    def get(self):
        car_key = ndb.Key(CarData, self.request.get('car_id'))
        #date_requested = self.request.get('date')

        query = "select * from CarData order by AJob.date desc limit 10"
        worker_key = ndb.Key(AWorker, self.request.get('car_id'))

        worker = worker_key.get()
        result_string="{'worker_name':'%s', 'jobs':[" % worker.worker_name
        counter=0

        for each_job in worker.list_jobs:
          cardatasets_key = ndb.Key(ARoute, each_job.job_id)
          everydata = cardatasets_key.get()
          counter_locations = 0
          if counter > 0:
            result_string +=","
          #self.response.headers['Content-Type'] = 'application/json'
          #result_string+="'jobs':[" % (each_job.job_id)

          result_string+="{'job_id':'%s', " % (each_job.job_id)

          
          result_string+="'locations':["
          for everyloc in everydata.location:
            if counter_locations > 0:
              result_string +=","
            result_string+="{'location': '%s'}" % everyloc
            counter_locations = counter_locations+1
          result_string+="],"
          result_string+="'speed':'%s', " % (everydata.speed)
          result_string+="'start_time':'%s', " % (date_handler(everydata.start_time))
          result_string+="'stop_time':'%s'" % (date_handler(everydata.stop_time))

          result_string +="}"
          counter = counter+1

        result_string+="]}"
        self.response.headers.set_status(200)
        self.response.write(json.dumps(result_string))
def add_job_docments(self):
    global documents_counter
    global total_docs_counter
    documents_counter+=1    
    total_docs_counter+=1
    job_doc(self, documents_counter)
    if documents_counter >= JOB_LIMIT_DOCUMENT:
        try:
            documents_counter = 0
            index = search.Index(name="job_index")
            index.put(documents_list)
            documents_list=[] 
                self.response.write("CAR DATA location objects")
                self.response.headers.set_status(200)             
                #query_string = "distance(job_location, geopoint(38.7234211,-9.1873166)) < 10" 
        except:
                    #self.response.set_status(500)
                    self.response.write('Put Job failed')
def job_doc(self,counter):     
    latitude = self.request.get('lat')
    
    longitude = self.request.get('lon')
    job_id = self.request.get('job_id')
    address = self.request.get('address')
    description = self.request.get('description')
    skill = self.request.get('skill')
    job_date = self.request.get('job_date')
    job_document = search.Document(
        # Setting the doc_id is optional. If omitted, the search service will create an identifier.
        doc_id = str(counter),
        fields=[
            search.TextField(name='job_id', value=str(job_id)),
            search.TextField(name='address', value=str(address)),
            search.TextField(name='description', value=str(description)),
            search.TextField(name='skill', value=str(skill)),
            search.DateField(name='job_date', value=datetime.datetime.fromtimestamp(float(long(str(job_date))))),
            search.GeoField(name='job_location', value=search.GeoPoint(float(latitude),float(longitude)))                
            ])
    documents_list.extend([job_document])
    job = AJob(id = job_id, job_id = job_id, assigned = False, address = address,
      description = description, skill = skill, job_date = datetime.datetime.fromtimestamp(float(long(str(job_date)))), date_posted = datetime.datetime.today())
    job.put()
    self.response.write(len(documents_list))
class AssignJobHandler(webapp2.RequestHandler):
  @ndb.transactional(xg=True)
  def post(self):
    job_id = self.request.get('job_id')
    worker_id = self.request.get('worker_id')
    job_key = ndb.Key(AJob, job_id)
        #date_requested = self.request.get('date')
    thejob = job_key.get()
    self.response.write(thejob.assigned)
    if not thejob.assigned:
      thejob.assigned = True
      thejob.put()

      worker_key = ndb.Key(AWorker, worker_id)
      theworker = worker_key.get()
      
      theworker.list_jobs.extend([thejob])
      theworker.put()

    
      for everyjob in theworker.list_jobs:
        self.response.write(everyjob.job_id)

class AddJobHandler(webapp2.RequestHandler):
    def post(self):
        # Handle the post to create a new job entry.
        add_job_docments(self)
        self.redirect("/")
def add_worker_docments(self):
    global documents_counter
    global total_docs_counter
    documents_counter+=1    
    total_docs_counter+=1
    worker_doc(self, documents_counter)
    if documents_counter >= JOB_LIMIT_DOCUMENT:
        try:
            documents_counter = 0
            index = search.Index(name="worker_index")
            index.put(documents_list)
            documents_list=[]
            if DEBUG == TRUE:
                self.response.write("WORKER objects")                   
        except:
          if DEBUG == TRUE:
                self.response.write('Put Worker failed')
        #query_string = "distance(job_location, geopoint(38.7234211,-9.1873166)) < 10" 

        #index = search.Index(name="index_monsoon")
def worker_doc(self,counter):     
    latitude = self.request.get('lat')
    
    longitude = self.request.get('lon')
    worker_id = self.request.get('worker_id')
    address = self.request.get('address')
    skill = self.request.get('skill')
    name = self.request.get('name')
    job_document = search.Document(
        # Setting the doc_id is optional. If omitted, the search service will create an identifier.
        doc_id = str(counter),
        fields=[
            search.TextField(name='worker_id', value=str(worker_id)),
            search.TextField(name='worker_name', value=str(name)),
            search.TextField(name='address', value=str(address)),     
            search.TextField(name='skill', value=str(skill)),
            search.GeoField(name='home_location', value=search.GeoPoint(float(latitude),float(longitude)))                
            ])
    documents_list.extend([job_document])
    worker = AWorker(id = worker_id, worker_id = worker_id, worker_name = name,address = address, skill = skill, list_jobs=[])
    worker.put()
    self.response.write(len(documents_list))
class AddWorkerHandler(webapp2.RequestHandler):
    def post(self):
        # Handle the post to create a new job entry.
        add_worker_docments(self)
        self.redirect("/")

class LocationHandler(webapp2.RequestHandler):
    def get(self):
      retrieve(self)
    def post(self):
      add(self, self.request.get('lat'),self.request.get('lon') )
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('In main')
class DistanceHandler(webapp2.RequestHandler):
    def get(self):
        distance = geocalc(38.7234211,-9.1873166,38.7209078,-9.1826026)
        self.response.write('In Distance\n')
        self.response.write(distance)
    


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/nearby', QueryHandler),
    ('/addcardata', CarDataHandler),
    ('/addworkerdata', AddWorkerHandler),
    ('/addjobdata', AddJobHandler),
    ('/assignjob', AssignJobHandler),
    ('/getcardata', GetMyCarHandler)

], debug=True)
