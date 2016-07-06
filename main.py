#!/usr/bin/env python

"""
main.py - This file contains handlers that are called by taskqueue and/or
cronjobs.
"""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import TicTacToeApi

from models import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """
        Send a reminder email every day to each User that has 
        incomplete games.
        """
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            if user.has_active_games():
                # Only send email reminders to users that have games
                # in progress
                subject = 'Reminder: You have a tic-tac-toe game in progress!'
                body = 'Hello {}, Your tic-tac-toe game needs your attention!'.format(user.name)
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)
        self.response.set_status(200)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        TicTacToeApi._cache_average_moves()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_moves', UpdateAverageMovesRemaining),
], debug=True)
