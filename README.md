Restify
=======
A ReST interface for appengine datastore.

Restify accepts and returns data in JSON format.Restify is CSOR compatible. Restify was built as a tool to aid front-end development in the absence of a proper backend. Restify helps us in setting up a backend rest server in minimal time. All you have to do is define your database model in ReSTify/model.py file and write the small snippet of code below.


## Get Started

	import webapp2

	import ReSTify

	application = webapp2.WSGIApplication(
	    [
	        ('/api/.*', ReSTify.ReST),
	        ],
	    debug=True)

## Files

#### ReSTify/model.py:

Define your datastore models over here.

#### ReSTify/settings.py:

###### ORIGIN_SITE_NAME

Define the URL for the site where the Requests originate (Server URL where the front-end is hosted)

###### MODEL_NAME_ALIAS

Define alias names for DataStore models for neater looking URL's and if you dont want to make your model names public

## Request syntax

#### GET:

Retrieve all the entities in the particular datastore `/api/<model_name>/`

Gets information about an entity `/api/<model_name>/<id>/`


#### POST:

Create an entity in the particular datastore `/api/<model_name>/`


#### DELETE:

Delete a particular entity `/api/<model_name>/<id>/`


#### PUT:

Edit a particular entity `/api/<model_name>/<id>/`


## Response status codes

* *200* -> Ok          -> When the requested data is retrieved successfully
* *201* -> Created     -> When a new object is created
* *404* -> Not Found   -> When the requested data was not found in the server.
* *400* -> Bad request -> When the request id or model name is incorrect
* *204* -> No Content  -> When data is deleted successfully from the server and there is no data to retrieve
