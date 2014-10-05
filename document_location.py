from datetime import datetime
from google.appengine.api import search
def add():

	my_document = search.Document(
    # Setting the doc_id is optional. If omitted, the search service will create an identifier.
    doc_id = 'PA6-5000',
    fields=[
          search.GeoField(name='job_location', value=search.GeoPoint(38.7234211,-9.1873166 39.093031,-9.2629842)),
                    search.GeoField(name='job_location', value=search.GeoPoint(39.093031,-9.2629842))
       ])
	try:
    	index = search.Index(name="job_index")
    	if	index.get(doc_id):
    		index.put(document)
		except search.Error:
  		    logging.exception('Put failed')