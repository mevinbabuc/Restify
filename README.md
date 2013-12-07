Restify
=======

A ReST interface for appengine datastore.Restify accepts and returns data only in JSON format.Restify is CSOR compatible.


## Get Started

	import webapp2

	import ReSTify

	application = webapp2.WSGIApplication(
	    [
	        ('/api/.*', ReSTify.ReST),
	        ],
	    debug=True)


## Request syntax

#### GET:

Retrieve all the entities in the particular datastore


/api/**model_name**/

Gets information about an entity


/api/**model_name**/**id**/


#### POST:

Create an entity in the particular datastore


/api/**model_name**/


#### DELETE:

Delete a particular entity


/api/**model_name**/**id**/


#### PUT:

Edit a particular entity


/api/**model_name**/**id**/


## Response status codes

* *200* -> Ok          -> When the requested data is retrieved successfully
* *201* -> Created     -> When a new object is created
* *404* -> Not Found   -> When the requested data was not found in the server.
* *400* -> Bad request -> When the request id or model name is incorrect
* *204* -> No Content  -> When data is deleted successfully from the server and there is no data to retrieve