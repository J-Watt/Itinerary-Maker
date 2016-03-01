#-------------------------------------------------------------------------------
# Name:        models.py
# Purpose:     Server-side App Engine & ProtoRPC models for Itenerary Maker
#
# Author:      Jordan Alexander Watt
#
# Created:     29-02-2016
# Copyright:   (c) Jordan 2016
#-------------------------------------------------------------------------------

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb

class User(ndb.Model):
    """User profile object"""
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)

    def to_form(self):
        """Returns a UserForm representation of the User"""
        return UserForm(username=self.username,
                        email=self.email)

class Itinerary(ndb.Model):
    """Itinerary object"""
    name = ndb.StringProperty(required=True)
    creator = ndb.KeyProperty(required=True, kind='User')
    startDate = ndb.DateProperty()
    endDate = ndb.DateProperty()
    emailReminder = ndb.BooleanProperty(default=False)
    transports = ndb.KeyProperty(repeated=True, kind='TransportItem', indexed=False)
    sharedLists = ndb.KeyProperty(repeated=True, kind='Checklist', indexed=False)

    def to_form(self):
        """Returns a ItineraryForm representation of the Itinerary"""
        form = ItineraryForm(name=self.name,
                             creator=self.creator.id(),
                             emailReminder=self.emailReminder)
        if self.startDate:
            form.startDate = str(self.startDate)
        if self.endDate:
            form.endDate = str(self.endDate)
        if self.transports:
            form.transports = [t.key.urlsafe() for t in self.transports]
        if self.sharedLists:
            form.sharedLists = [s.key.urlsafe() for s in self.sharedLists]
        return form

class TransportItem(ndb.Model):
    """Transportation object"""
    name = ndb.StringProperty(required=True)
    creator = ndb.KeyProperty(required=True, kind='User')
    seats = ndb.IntegerProperty(indexed=False, default=1)
    seatsAvailable = ndb.IntegerProperty(indexed=False, default=1)
    depart = ndb.DateProperty(indexed=False)
    arrive = ndb.DateProperty(indexed=False)
    notes = ndb.StringProperty(indexed=False)
    template = ndb.BooleanProperty(required=True, default=False)

    def to_form(self):
        """Returns TransportForm representation of Transportation"""
        form = TransportForm(name=self.name,
                             creator=self.creator.id(),
                             seats=self.seats,
                             seatsAvailable=self.seatsAvailable,
                             template=self.template)
        if self.depart:
            form.depart = str(self.depart)
        if self.arrive:
            form.arrive = str(self.arrive)
        if self.notes:
            form.notes = self.notes
        return form

class Checklist(ndb.Model):
    """Checklist object"""
    name = ndb.StringProperty(required=True)
    creator = ndb.KeyProperty(required=True, kind='User')
    items = ndb.KeyProperty(repeated=True, kind='ListItem', indexed=False)
    template = ndb.BooleanProperty(required=True, default=False)

    def to_form(self):
        """Returns ChecklistForm representation of Checklist"""
        form = ChecklistForm(name=self.name,
                             creator=self.creator.id(),
                             template=self.template)
        if self.startDate:
            form.startDate = str(self.startDate)
        if self.endDate:
            form.endDate = str(self.endDate)
        if self.items:
            form.items = [i.key.urlsafe() for i in self.items]
        return form

class ListItem(ndb.Model):
    """List Item object"""
    name = ndb.StringProperty(required=True)
    notes = ndb.StringProperty(indexed=False)
    image = ndb.StringProperty(indexed=False)
    due = ndb.DateProperty()
    check = ndb.IntegerProperty(choices=[0, 1, 2], default=0)


    def to_form(self):
        """Returns ListItemForm representation of ListItem"""
        form = ListItemForm(name=self.name,
                            check=self.check)
        if self.notes:
            form.notes = self.notes
        if self.image:
            form.image = self.image
        if self.due:
            form.due = str(self.due)
        return form

class UserForm(messages.Message):
    """UserForm for outbound form message"""
    username = messages.StringField(1)
    email = messages.StringField(2)

class ItineraryForm(messages.Message):
    """ItineraryForm for outbound form message"""
    name = messages.StringField(1, required=True)
    creator = messages.IntegerField(2, required=True)
    startDate = messages.StringField(3)
    endDate = messages.StringField(4)
    emailReminder = messages.BooleanField(5)
    transports = messages.StringField(6, repeated=True)
    sharedLists = messages.StringField(7, repeated=True)

class TransportForm(messages.Message):
    """TransportForm for outbound form message"""
    name = messages.StringField(1, required=True)
    creator = messages.IntegerField(2, required=True)
    seats = messages.IntegerField(3)
    seatsAvailable = messages.IntegerField(4)
    depart = messages.StringField(5)
    arrive = messages.StringField(6)
    notes = messages.StringField(7)
    template = messages.BooleanField(8)


class ChecklistForm(messages.Message):
    """ChecklistForm for outbound form message"""
    name = messages.StringField(1, required=True)
    creator = messages.IntegerField(2, required=True)
    items = messages.StringField(3, repeated=True)
    template = messages.BooleanField(4)

class ListItemForm(messages.Message):
    """ListItemForm for outbound form message"""
    name = messages.StringField(1, required=True)
    notes = messages.StringField(2)
    image = messages.StringField(3)
    due = messages.StringField(4)
    check = messages.IntegerField(5)