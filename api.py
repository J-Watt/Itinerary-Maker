#-------------------------------------------------------------------------------
# Name:        api.py
# Purpose:     Itinerary Maker API server exposing resources
#
# Author:      Jordan Alexander Watt
#
# Created:     29-02-2016
# Copyright:   (c) Jordan 2016
#-------------------------------------------------------------------------------

import logging
import endpoints

from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from models import User
from models import Itinerary
from models import TransportItem
from models import Checklist
from models import ListItem
from models import UserForm
from models import ItineraryForm
from models import TransportForm
from models import ChecklistForm
from models import ListItemForm

from settings import WEB_CLIENT_ID
from settings import ANDROID_CLIENT_ID
from settings import IOS_CLIENT_ID
from settings import ANDROID_AUDIENCE

API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

UPDATE_USER_REQUEST = endpoints.ResourceContainer(UserForm)
UPDATE_LIST_REQUEST = endpoints.ResourceContainer(
    ChecklistForm,
    urlsafe_list_key=messages.StringField(1))
UPDATE_ITIN_REQUEST = endpoints.ResourceContainer(
    ItineraryForm,
    urlsafe_itin_key=messages.StringField(1))
UPDATE_TRAN_REQUEST = endpoints.ResourceContainer(
    TransportForm,
    urlsafe_tran_key=messages.StringField(1))

@endpoints.api(name='itineraryMaker', version='v1',
               audiences=[ANDROID_AUDIENCE],
               allowed_client_ids=[WEB_CLIENT_ID, ANDROID_CLIENT_ID,
                                   IOS_CLIENT_ID, API_EXPLORER_CLIENT_ID])
class ItineraryMakerApi(remote.Service):
    """Itinerary Maker Api Server"""

    def _getUser(self):
        """Creates new user"""
        current_user = endpoints.get_current_user()
        if not current_user:
            raise endpoints.UnauthorizedException('Authorization Required')
        user = User.query(User.email == current_user.email()).get()
        if not user:
            user = User.new_user(current_user.nickname(), current_user.email())
        return user


    @endpoints.method(request_message=UserForm,
                      response_message=UserForm,
                      path='user/update',
                      name='update_user',
                      http_method='POST')
    def updateUser(self, request):
        """Updates an existing username"""
        user = self._getUser()
        return user.update_user(request).to_form()


    @endpoints.method(request_message=ChecklistForm,
                      response_message=ChecklistForm,
                      path='list',
                      name='createList',
                      http_method='POST')
    def createList(self, request):
        """Creates new list"""
        user = self._getUser()
        request.creator = user.email
        checklist = Checklist.new_list(request)
        return checklist.to_form()

    @endpoints.method(request_message=UPDATE_LIST_REQUEST,
                      response_message=ChecklistForm,
                      path='list/{urlsafe_list_key}',
                      name='updateList',
                      http_method='PUT')
    def updateList(self, request):
        """Updates an existing list"""
        user = self._getUser()
        checklist = ndb.Key(urlsafe=request.urlsafe_list_key).get()
        return checklist.update_list(request).to_form()

    @endpoints.method(request_message=ItineraryForm,
                      response_message=ItineraryForm,
                      path='itinerary',
                      name='createItinerary',
                      http_method='POST')
    def createItinerary(self, request):
        """Creates new itinerary"""
        user = self._getUser()
        request.creator = user.email
        itinerary = Itinerary.new_itinerary(request)
        return itinerary.to_form()

    @endpoints.method(request_message=UPDATE_ITIN_REQUEST,
                      response_message=ItineraryForm,
                      path='itinerary/{urlsafe_itin_key}',
                      name='updateItinerary',
                      http_method='PUT')
    def updateItinerary(self, request):
        """Updates an existing itinerary"""
        user = self._getUser()
        itinerary = ndb.Key(urlsafe=request.urlsafe_itin_key).get()
        return itinerary.update_itinerary(request).to_form()

    @endpoints.method(request_message=TransportForm,
                      response_message=TransportForm,
                      path='transport',
                      name='createTransport',
                      http_method='POST')
    def createTransport(self, request):
        """Creates new transport"""
        user = self._getUser()
        request.creator = user.email
        transport = TransportItem.new_transport(request)
        return transport.to_form()

    @endpoints.method(request_message=UPDATE_TRAN_REQUEST,
                      response_message=TransportForm,
                      path='transport/{urlsafe_tran_key}',
                      name='updateTransport',
                      http_method='PUT')
    def updateTransport(self, request):
        """Updates an existing transport"""
        user = self._getUser()
        transport = ndb.Key(urlsafe=request.urlsafe_tran_key).get()
        return transport.update_transport(request).to_form()

api = endpoints.api_server([ItineraryMakerApi])