# ReSTify
# A simple lightweight barebone ReST framework for appengine
#
# Copyright 2013 Mevin Babu Chirayath <mevinbabuc@gmail.com>
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

__author__ = 'mevinbabuc@gmail.com (Mevin Babu Chirayath)'
__version__ = "0.1"

import httplib2
import logging
import os

import webapp2
import json

import model

def CSOR_Jsonify(func):
    """ decorator to make all requests CSOR compatible and jsonfy the output """

    def wrapper(*args, **kw):

        dataOject=func(*args, **kw)

        try:
            _origin = args[0].request.headers['Origin']
        except:
            _origin = "http://gcdc2013-keeptabson.appspot.com/"

        args[0].response.headers.add_header("Access-Control-Allow-Origin", _origin)
        args[0].response.headers.add_header("Access-Control-Allow-Credentials", "true")
        args[0].response.headers.add_header("Access-Control-Allow-Headers",
         "origin, x-requested-with, content-type, accept")
        args[0].response.headers.add_header('Content-Type', 'application/json')

        args[0].response.write(json.dumps(dataOject))
    return wrapper

class ResT(webapp2.RequestHandler):
    """ Class to handle requests (GET, POST, DELETE) to the route /api/ . """


    @CSOR_Jsonify
    @decorator.oauth_aware
    def post(self,query=""):
        """Post Request handler to add data to the HashStore

        Args:

        return:
            A status object which contains the data added and error messages if any.
            status['object']
            status['success']
            status['error']

        Exceptions/response status codes :
            201 -> Created   -> When a new object was saved in HashStore
            404 -> Not Found -> When the post variables title and hashtags was
                                blank or NULL

        """

        status={}
        status["error"]=None
        status["success"]=True
        key=False

        NoteTitle = self.request.get("title")
        NoteHashtags = self.request.get("hashtags")

        if NoteHashtags and NoteTitle:
            HashEntry=model.HashStore(author=users.get_current_user(),
                hashtag=NoteHashtags,title=NoteTitle)
            key=HashEntry.put()
            self.response.set_status(201,"Created")
            status['Object']={"title":NoteTitle,"hashtag":NoteHashtags}

        if not key:
            status["success"]=False
            status["error"]="Unable to Add your Tab.Try again"
            self.response.set_status(404,"Not Found")

        return status

    @CSOR_Jsonify
    @decorator.oauth_aware
    def get(self,query=""):
        """Get request handler to retrieve the list of Tabs saved in the HashStore

        Args:

        Return:
            An object containing all the Tabs of the logged in user.Each tab 
            contains title, hashtag and the date it was created.

        Response status codes :
            404 -> Not Found -> When there's no data in the HashStore for the
                                particular user
            400 -> Bad Request->When the program is unable to search db etc.
                                Try again later.
            200 -> Ok -> When data is found and proper data is returned.

        """

        node = self.request.path_info.split('/')
        _model = getattr(model, node[1])

        print self.request.path_info

        if node[2]:
            qry = _model.query().filter(_model.author == users.get_current_user(), _model.get_by_id(node[2]))
        else:
            qry = _model.query().filter(_model.author == users.get_current_user())

        dataList=[]

        if qry :
            for temp in qry:
                dataObject={}
                dataObject["title"]=temp.title
                dataObject["hashtag"]=temp.hashtag
                dataObject["viewDate"]=temp.viewDate.strftime("%Y/%m/%d %H:%M")

                dataList.append(dataObject)

        if len(dataList)==0:
            self.response.set_status(404,"Not Found")
        elif not qry :
            self.response.set_status(400,"Bad Request")
        else :
            self.response.set_status(200,"Ok")


        return dataList
'''
    @CSOR_Jsonify
    @decorator.oauth_aware
    def delete(self,query):
        """Delete request handler to delete a Tab from HashStore

        Args:
            query: Accepts tabs(Hashtag) that has to be deleted for the 
            particular user

        Return:
            Delete request is not supposed to return any value

        Response status codes :
            404 -> Not Found -> When the data to be deleted is not found in the 
                                HashStore
            204 -> No Content-> When data is found in the HashStore and deleted,
                                so there's no content to return
            400 -> Bad Request->When invalid query( Hashtag) was passed to the 
                                delete request

        """

        status={}
        hashtags = query.strip()

        if hashtags:
            qry = HashStore.query().filter(
                HashStore.author==users.get_current_user(),
                HashStore.hashtag==hashtags).fetch(keys_only=True)

            ndb.delete_multi(qry)

            if not qry:
                self.response.set_status(404,"Not Found")
            else :
                self.response.set_status(204,"No Content")

        if not hashtags:
            self.response.set_status(400,"Bad Request")

        return status
'''
    def options(self,query=""):

        try:
            _origin = self.request.headers['Origin']
        except:
            _origin = "http://gcdc2013-keeptabson.appspot.com/"

        self.response.set_status(200,"Ok")
        self.response.headers.add_header("Access-Control-Allow-Origin", _origin)
        self.response.headers.add_header("Access-Control-Allow-Methods",
         "GET, POST, OPTIONS, PUT, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Credentials", "true")
        self.response.headers.add_header("Access-Control-Allow-Headers",
         "origin, x-requested-with, content-type, accept")

application = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/api/.*>', ResT),
        webapp2.Route(decorator.callback_path, decorator.callback_handler()),
        ],
    debug=True)