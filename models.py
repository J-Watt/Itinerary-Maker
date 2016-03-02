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
    username = ndb.StringProperty(required=True, indexed=False)
    email = ndb.StringProperty(required=True)

    @classmethod
    def new_user(cls, username, email):
        """Creates and returns a new user"""
        u_key = ndb.Key(User, email)
        user = User(username=username, email=email, key=u_key)
        user.put()
        return user

    def update_user(self, form):
        """Updates user object"""
        if form.username:
            self.username = form.username
            self.put()
        return self

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
    public = ndb.BooleanProperty(default=False)
    transports = ndb.KeyProperty(repeated=True, kind='TransportItem', indexed=False)
    sharedLists = ndb.KeyProperty(repeated=True, kind='Checklist', indexed=False)

    @classmethod
    def new_itinerary(cls, form):
        """Creates and returns a new itinerary"""
        itinerary = Itinerary(name=form.name, creator=ndb.Key(User, form.creator))
        return itinerary.update_itinerary(form)

    def update_itinerary(self, form):
        """updates an itinerary with new values"""
        if form.name:
            self.name = form.name
        if form.startDate:
            self.startDate = form.startDate
        if form.endDate:
            self.endDate = form.endDate
        if form.emailReminder:
            self.emailReminder = form.emailReminder
        if form.public:
            self.public = form.public
        self.put()
        return self

    def update_lists(self, form):
        """Updates an itinerary's lists with new values"""
        if form.sharedLists:
            new_lists = []
            for li in form.sharedLists:
                new = ndb.Key(urlsafe=li)
                new_lists.append(new)
            self.sharedLists = new_lists
            self.put()

    def update_transports(self, form):
        """Updates an itinerary's transports with new values"""
        if form.transports:
            new_tp = []
            for tp in form.transports:
                new = ndb.Key(urlsafe=tp)
                new_tp.append(new)
            self.transports = new_tp
            self.put()

    def to_form(self):
        """Returns a ItineraryForm representation of the Itinerary"""
        form = ItineraryForm(name=self.name,
                             creator=self.creator.id(),
                             emailReminder=self.emailReminder,
                             public=self.public)
        if self.startDate:
            form.startDate = str(self.startDate)
        if self.endDate:
            form.endDate = str(self.endDate)
        if self.transports:
            form.transports = [t.key.urlsafe() for t in self.transports]
        if self.sharedLists:
            form.sharedLists = [s.key.urlsafe() for s in self.sharedLists]
        form.urlsafe_key = self.key.urlsafe()
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

    @classmethod
    def new_transport(cls, form):
        """Creates and returns a new transport item"""
        transport = TransportItem(name=form.name, creator=ndb.Key(User, form.creator))
        return transport.update_transport(form)

    def update_transport(self, form):
        """updates a transport item with new values"""
        if form.name:
            self.name = form.name
        if form.seats:
            self.seats = form.seats
            self.seatsAvailable = form.seats
        if form.depart:
            self.depart = form.depart
        if form.arrive:
            self.arrive = form.arrive
        if form.notes:
            self.notes = form.notes
        if form.template:
            self.template = form.template
        self.put()
        return self

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
        form.urlsafe_key = self.key.urlsafe()
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

class Checklist(ndb.Model):
    """Checklist object"""
    name = ndb.StringProperty(required=True)
    creator = ndb.KeyProperty(required=True, kind='User')
    items = ndb.StructuredProperty(ListItem, repeated=True)
    template = ndb.BooleanProperty(default=False)

    @classmethod
    def new_list(cls, form):
        """Creates and returns a new checklist"""
        checklist = Checklist(name=form.name, creator=ndb.Key(User, form.creator))
        return checklist.update_list(form)

    def update_list(self, form):
        """updates a checklist with new values"""
        if form.name:
            self.name = form.name
        if form.items:
            new_items = []
            for item in form.items:
                new = ListItem(name=item.name)
                if item.notes:
                    new.notes = item.notes
                if item.image:
                    new.image = item.image
                if item.due:
                    new.due = item.due
                if item.check:
                    new.check = item.check
                new_items.append(new)
            self.items = new_items
        if form.template:
            self.template = form.template
        self.put()
        return self

    def to_form(self):
        """Returns ChecklistForm representation of Checklist"""
        form = ChecklistForm(name=self.name,
                             creator=self.creator.id(),
                             template=self.template)
        if self.items:
            form.items = [i.to_form() for i in self.items]
        form.urlsafe_key = self.key.urlsafe()
        return form

        #if items:
         #   for item in items:
          #      checklist.items.append(ndb.Key(urlsafe=item).get())



class UserForm(messages.Message):
    """UserForm for outbound form message"""
    username = messages.StringField(1)
    email = messages.StringField(2)

class ItineraryForm(messages.Message):
    """ItineraryForm for outbound form message"""
    name = messages.StringField(1, required=True)
    creator = messages.StringField(2)
    startDate = messages.StringField(3)
    endDate = messages.StringField(4)
    emailReminder = messages.BooleanField(5)
    public = messages.BooleanField(6)
    transports = messages.StringField(7, repeated=True)
    sharedLists = messages.StringField(8, repeated=True)
    urlsafe_key = messages.StringField(9)

class TransportForm(messages.Message):
    """TransportForm for outbound form message"""
    name = messages.StringField(1, required=True)
    creator = messages.StringField(2)
    seats = messages.IntegerField(3)
    seatsAvailable = messages.IntegerField(4)
    depart = messages.StringField(5)
    arrive = messages.StringField(6)
    notes = messages.StringField(7)
    template = messages.BooleanField(8)
    urlsafe_key = messages.StringField(9)

class ListItemForm(messages.Message):
    """ListItemForm for outbound form message"""
    name = messages.StringField(1, required=True)
    notes = messages.StringField(2)
    image = messages.StringField(3)
    due = messages.StringField(4)
    check = messages.IntegerField(5)

class ChecklistForm(messages.Message):
    """ChecklistForm for outbound form message"""
    name = messages.StringField(1, required=True)
    creator = messages.StringField(2)
    items = messages.MessageField(ListItemForm, 3, repeated=True)
    template = messages.BooleanField(4)
    urlsafe_key = messages.StringField(5)

class ListItemForms(messages.Message):
    """ListItemForms for multiple outbound form messages"""
    items = messages.MessageField(ListItemForm, 1, repeated=True)