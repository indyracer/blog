#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def renderError(self, error_code):
        """sends an http error code and a generic "oops!" message to the client."""
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

class BlogDb(db.Model):
    title = db.StringProperty(required = True)
    comment = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class Blog(Handler):
    def get (self):
        comments = db.GqlQuery("SELECT * FROM BlogDb ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("front.html")
        response = t.render(comments = comments)
        self.response.write(response)






#set up blog new post submissions
class NewPost(Handler):
    def get(self):
        t = jinja_env.get_template("blogform.html")
        response = t.render(title = "", comment = "", error = "")
        self.response.write(response)



    def post(self):
        title = self.request.get("title")
        comment = self.request.get("comment")

        if title and comment:
            c = BlogDb(title = title, comment = comment)
            c.put()

            #self.redirect("/blog/c.key().id()")
            self.redirect("/blog/%s" % c.key().id())
        else:
            error = "we need both a title and a comment"
            t = jinja_env.get_template("blogform.html")
            response = t.render(title = title, comment = comment, error = error)
            self.response.write(response)

class ViewPostHandler(Handler):
    def get(self, id):
        int_id = int(id)
        idnum = BlogDb.get_by_id(int_id)

        if idnum:

            self.render("viewpost.html", idnum=idnum)

        else:
            error = "<h1>There is no post by that id </h1>"
            self.response.out.write(error)



app = webapp2.WSGIApplication([
    ('/blog', Blog),
    ('/newpost', NewPost),
    #to set our dynamic link for individual blog post
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
