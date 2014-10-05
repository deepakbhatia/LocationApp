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
import webapp2
from datetime import datetime
from google.appengine.api import search
from math import radians, sqrt, sin, cos, atan2
#import MySQLdb
# Define your production Cloud SQL instance information.
_INSTANCE_NAME = 'joblocationidentifier:eachjobs'

def add(self):
  document_id = 'PA6-50'
  doc_id_1 = "PA6-51"
  doc_id_2 = "PA6-52"
  doc_id_3 = "PA6-53"
  doc_id_4 = "PA6-54"
  x = "38.7234211"
  y = "-9.1873166"
  z = '{lat}'.format(lat=x)
  z1 = 'lon'.format(lon=y)
  self.response.write(float(y))

  doclist=[]
  my_document = search.Document(
    # Setting the doc_id is optional. If omitted, the search service will create an identifier.
    doc_id = document_id,
    fields=[
          search.GeoField(name='job_location', value=search.GeoPoint(float(x),float(y)))                 
       ])
  self.response.write(my_document.field('job_location').value)
  doclist.extend([my_document])
  my_document_1 = search.Document(
    # Setting the doc_id is optional. If omitted, the search service will create an identifier.
    doc_id  = doc_id_1,
    fields=[
          search.GeoField(name='job_location', value=search.GeoPoint(38.7234211,-9.1873166))                 
       ])
  doclist.extend([my_document_1])
  my_document_2 = search.Document(
    doc_id  = doc_id_2,
    fields=[
          search.GeoField(name='job_location', value=search.GeoPoint(38.7260522,-9.150556))                
       ])
  doclist.extend([my_document_2])
  my_document_3  = search.Document(
    doc_id = doc_id_3,
    fields=[
          search.GeoField(name='job_location', value=search.GeoPoint(38.7309904,-9.1497192))                  
       ])
  doclist.extend([my_document_3])
  my_document_4 = search.Document(
    doc_id  = doc_id_4,
    fields=[
          search.GeoField(name='job_location', value=search.GeoPoint(38.7296178,-9.1518006))                
       ]) 
  doclist.extend([my_document_4])
                    
  try:
        index = search.Index(name="index_jobs_2")
        index.put(doclist)
        #if  index.get(document_id):
        #  index.put(my_document)
        #if  index.get(doc_id_1):
        #  index.put(my_document_1)
        #if  index.get(doc_id_2):
        #  index.put(my_document_2)
        #if  index.get(doc_id_3):
        #  index.put(my_document_3)
        #if  index.get(doc_id_4):
        #  index.put(my_document_4)
        self.response.write("posted location objects")
  except search.Error:
        self.response.write('Put failed')

def retrieve(self):
  index = search.Index(name="index_jobs_2")
  query_string = "distance(job_location, geopoint(38.7234211,-9.1873166)) < 10" 
  try:
        self.response.write('In local')
        results = index.search(query_string)
        self.response.write('In local 2')
        total_matches = results.number_found
        print total_matches
        self.response.write(total_matches)
        #document;
        # Iterate over the documents in the results
        for scored_document in results:
          # handle results
          #document = scored_document
          self.response.write(scored_document.field('job_location').value.latitude)
  except search.Error:
        self.response.write('Search failed')
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
class AddJobHandler(webapp2.RequestHandler):
    def post(self):
        # Handle the post to create a new job entry.
        job_id = self.request.get('job')
        creator = self.request.get('creator')
        address = self.request.get('address')
        lat = self.request.get('lat')
        lon = self.request.get('lon')
        description = self.request.get('description')
        skill = self.request.get('skill')

        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='joblist', user='root')
        else:
            db = MySQLdb.connect(host='127.0.0.1', port=3306, db='joblist', user='root')
            # Alternatively, connect to a Google Cloud SQL instance using:
            # db = MySQLdb.connect(host='ip-address-of-google-cloud-sql-instance', port=3306, db='guestbook', user='root')

        cursor = db.cursor()
        # Note that the only format string supported is %s
        cursor.execute('INSERT INTO entries (job, creator, address, lat, lon, decription, skill) VALUES (%s, %s, %s, 10.3f, 10.3f, %s, %s)'
          , (job_id, creator, address, lat, lon, description, skill))
        db.commit()
        db.close()

        self.redirect("/")

class LocationHandler(webapp2.RequestHandler):
    def get(self):
      retrieve(self)
    def post(self):
      add(self)
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
    ('/local', LocationHandler),
    ('/distance', DistanceHandler)

], debug=True)
