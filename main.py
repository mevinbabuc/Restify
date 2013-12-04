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

# import httplib2
# import logging
import os

from google.appengine.api import users

import webapp2
import json

import model

def CSOR_Jsonify(func):
    """ decorator to make all requests CSOR compatible and jsonfy the output """

    def wrapper(*args, **kw):

        def datetimeconvert(obj):
            """datetimeconvert JSON serializer."""
            import datetime

            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y/%m/%d %H:%M")

            return str(obj)

        dataObject=func(*args, **kw)

        try:
            _origin = args[0].request.headers['Origin']
        except:
            _origin = "http://gcdc2013-keeptabson.appspot.com/"

        args[0].response.headers.add_header("Access-Control-Allow-Origin", _origin)
        args[0].response.headers.add_header("Access-Control-Allow-Credentials", "true")
        args[0].response.headers.add_header("Access-Control-Allow-Headers",
         "origin, x-requested-with, content-type, accept")
        args[0].response.headers.add_header('Content-Type', 'application/json')

        if dataObject:
            args[0].response.write(json.dumps(dataObject, default = datetimeconvert))

    return wrapper

class ResT(webapp2.RequestHandler):
    """ Class to handle requests (GET, POST, DELETE) to the route /api/ . """


    @CSOR_Jsonify
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
        json_args_dic = None

        # NoteTitle = self.request.get("title")
        # NoteHashtags = self.request.get("hashtags")

        node = self.request.path_info.split('/')
        if node[-1] == '':
            node.pop(-1)

        _model = getattr(model, node[2])

        _json = self.request.body.encode("utf-8")

        try:
            json_args_dic = json.loads(_json,encoding="utf-8")
        except:
            json_args_dic = None

        if json_args_dic:
            HashEntry=_model(author=users.get_current_user(), **json_args_dic)
            key=HashEntry.put()
            self.response.set_status(201,"Created")

            json_args_dic['id'] = key.id()
            status['object'] = json_args_dic

        if not key:
            status["success"] = False
            status["error"] = "Unable to Add your Tab.Try again"
            self.abort(404)

        return status

    @CSOR_Jsonify
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
        qry = None
        Object_by_id = None
        _model = None

        node = self.request.path_info.split('/')
        if node[-1] == '':
            node.pop(-1)

        if len(node) - 1 >= 2:
            if node[2]:
                try:
                    _model = getattr(model, node[2])
                except:
                    _model = None

            if len(node) -1 > 2 and _model:
                Object_by_id = _model.get_by_id(int(node[3]))
            elif node[2] and _model:
                qry = _model.query().filter(_model.author == users.get_current_user())

        dataList=[]

        if qry :
            for temp in qry:
                dataObject=temp.to_dict()
                dataObject["id"] = temp.key.id()
                dataList.append(dataObject)

        elif Object_by_id:
            dataObject=Object_by_id.to_dict()
            dataList.append(dataObject)

        if len(dataList)==0:
            self.abort(404)
            dataList = None
        elif not qry and not Object_by_id:
            self.abort(400)
        else :
            self.response.set_status(200,"Ok")

        return dataList

    @CSOR_Jsonify
    def delete(self,query=""):
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

        Object_by_id = None
        _model = None

        node = self.request.path_info.split('/')
        if node[-1] == '':
            node.pop(-1)

        if len(node) - 1 > 2:
            if node[2]:
                try:
                    _model = getattr(model, node[2])
                except:
                    _model = None

            if _model:
                Object_by_id = _model.get_by_id(int(node[3]))

        if Object_by_id:
            Object_by_id.key.delete()
            self.response.set_status(204,"No Content")
        elif not _model:
            self.abort(400)
        else:
            self.abort(404)

        return {}

    @CSOR_Jsonify
    def put(self,query=""):
        """PUT request handler to edit a Tab from HashStore

        Args:
            query: Accepts tabs(Hashtag) that has to be deleted for the 
            particular user

        Return:
            returns the edited object

        Response status codes :
            404 -> Not Found -> When the data to be deleted is not found in the 
                                HashStore
            200 -> Ok        -> When data is found in the HashStore and edited
            400 -> Bad Request->When invalid query( Hashtag) was passed to the 
                                put request

        """
        status={}
        status["error"]=None
        status["success"]=True
        Object_by_id = None
        _model = None
        _json = None
        json_args_dic = None
        HashEntry = None

        node = self.request.path_info.split('/')
        if node[-1] == '':
            node.pop(-1)

        if len(node) - 1 > 2:
            if node[2]:
                try:
                    _model = getattr(model, node[2])
                except:
                    _model = None

            #check if the id is a valid one
            if _model:
                Object_by_id = _model.get_by_id(int(node[3]))

            # if data already present in server, then modify
            if Object_by_id:
                _json = self.request.body.encode("utf-8")

                try:
                    json_args_dic = json.loads(_json,encoding="utf-8")
                except:
                    json_args_dic = None

                if json_args_dic :
                    json_args_dic["id"]=int(node[3])
                    status['object'] = json_args_dic
                    HashEntry=_model(author=users.get_current_user(), **json_args_dic)
                    key=HashEntry.put()
        else:
            self.abort(400)

        if HashEntry:
            self.response.set_status(200,"Ok")
            return status
        else:
            self.abort(404)

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
        ('/api/.*', ResT),
        ],
    debug=True)