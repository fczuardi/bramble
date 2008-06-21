#!/usr/bin/env python

""" A simple task/bug tracking system. """

__author__ = "Drew Newberry <drew@revision1.net>"

import os, time, sys, logging
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users


from google.appengine.api import urlfetch

_DEBUG = True

class Ticket(db.Model):
	summary = db.StringProperty()
	description = db.TextProperty()
	labels = db.ListProperty(db.Category)
	created = db.DateTimeProperty(auto_now_add=True)
	updated = db.DateTimeProperty(auto_now=True)
	author_email = db.EmailProperty()
	status = db.StringProperty(default="new")
	type = db.StringProperty(default="ticket")
	
	def get_labels(self):
		"""returns a dictionary of all labels in the ticket"""
		ld = {}
		for label in self.labels:
			tokens = label.split(":")
			ld[tokens[0]] = tokens[1]
		return ld

class Comment(db.Model):
    author_email = db.EmailProperty(required=True)
    description = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    ticket = db.ReferenceProperty(Ticket)

class SystemPair(db.Model):
	lookup = db.StringProperty()
	data = db.TextProperty()


class BaseRequestHandler(webapp.RequestHandler):
    """Supplies a common template generation function.

    When you call generate(), we augment the template variables supplied with
    the current user in the 'user' variable and the current webapp request
    in the 'request' variable.
    """
    def generate(self, template_name, template_values={}):
        values = {
            'request': self.request,
            'user': users.GetCurrentUser(),
			'admin': users.is_current_user_admin(),
            'login_url': users.CreateLoginURL(self.request.uri),
            'logout_url': users.CreateLogoutURL('http://' + self.request.host + '/'),
            'debug': self.request.get('deb'),
            'application_name': 'my pool'
        }
        values.update(template_values)
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, os.path.join('templates', template_name))
        self.response.out.write(template.render(path, values, debug=_DEBUG))

class DefaultPage(BaseRequestHandler):
	def get(self):
		tickets = Ticket.all()
		test = {"one": "with some content", "two":"with some more"}
		self.generate('dashboard.html', {'tickets':tickets, 'test':test})
	    
class CreateTicket(BaseRequestHandler):
	def get(self):
		self.generate('create.html')
	
	def post(self):
		t = Ticket(description=self.request.get('description'),
		    summary = self.request.get('summary'),
		    author_email = self.request.get('email'))
		t.put()

		self.redirect('/ticket/' + str(t.key().id()))

class ViewTicket(BaseRequestHandler):
	def get(self, ticket_id):
		ticket = Ticket.get_by_id(int(ticket_id))
		comments = db.GqlQuery("SELECT * FROM Comment WHERE ticket = :ticket ORDER BY created ASC",
			ticket=ticket)

		labels = []
		label_value = []
		#lets get the labels into two lists
		# we should be using a dictionary but django doesn't let us
		# easily loop through a dictionary
		for label in ticket.labels:
			tokens = label.split(":")
			labels.append(tokens[0])
			label_value.append(tokens[1])

		self.generate('ticket.html', {'ticket':ticket,'comments':comments, 'labels':labels, 'label_value':label_value})

class TicketChangeSet(BaseRequestHandler):
	def post(self, ticket_id):
		c = Comment(author_email=self.request.get('comment_email'),
			description=self.request.get('new_comment'),
			ticket=db.Key(self.request.get('ticket_key')))
		c.put()
		t = Ticket.get(db.Key(self.request.get('ticket_key')))
		labels = [db.Category('type:feature-request'), db.Category('priority:high'), db.Category('access:public')]
		t.labels = labels
		t.put()

		self.redirect('/ticket/' + ticket_id)
		
class ControlDashboard(BaseRequestHandler):
	def get(self):
		self.generate('control.html')

def main():
  application = webapp.WSGIApplication([
		('/', DefaultPage),
		('/ticket/create', CreateTicket),
		('/ticket/(\d+)/changeset', TicketChangeSet),
		('/ticket/(\d+)', ViewTicket),
		('/control/', ControlDashboard)
	], debug=_DEBUG)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
		
