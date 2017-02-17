#!/usr/bin/env python
import os
import webapp2
import jinja2
import time
#import logging

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self,template, **kw):
        self.write(self.render_str(template, **kw))


class Entry(db.Model): #represents submission from user
    title = db.StringProperty(required = True) #define types of this entity
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainHandler(Handler):
    def get(self):
        self.redirect('/blog')

#####blog stuff

class MainBlog(Handler):  #main front page
    def render_front_page(self,title="", content=""):
        contents = db.GqlQuery("SELECT * from Entry ORDER BY created DESC ")#run a query
        self.render("front.html", title= title, content=content,  contents=contents )

    def get(self):
        self.render_front_page()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        self.response.write(title, content)


class Newpost(Handler):  #new post page
    def render_newpostform(self, title="",content= "",error=""): #passing "" into template
        self.render("newpost.html", title=title, content=content, error=error) #render it from templates

    def get(self):
        self.render_newpostform()

    def post(self):
        title = self.request.get("title")  #creating variables
        content = self.request.get("content")

        if title and content:  #creates a new instance of Content, called a
            a = Entry(title=title, content=content)
            a.put() #stores new Entry object in database
            time.sleep(1)  #Nick's solution to not have to refresh
            new_route = "/blog/" + str(a.key().id()) #comes later
            self.redirect(new_route)

        else:
            error = "We need both a title and some content"
            self.render_newpostform(title, content, error) #pass in from line 23-24


class ViewPostHandler(webapp2.RequestHandler):  #what's the purpose of this class?
    def get(self, id):
        blog_id = Entry.get_by_id(int(id)) #get_by_id of user input, query of database, find it by id
        # logging.info("test")
        # logging.info(title)
        if blog_id == None: #find blog_id; if not there, return error
            error = "No post associated with id."
            self.response.write(error)
        else:
            self.response.write(blog_id.title)
            self.response.write("<html><body><br><br></body></html>")
            self.response.write(blog_id.content)

    #add something with blog_id
    # def single_new_post(self, title="",content=""):
    #     self.render("single_new_post.html", title=title, content=content)
    #     self.single_new_post()
    #
    # def post(self):
    #     title = self.request.get("title")
    #     content = self.request.get("content")
    #     self.response.write(title, content)

app = webapp2.WSGIApplication([
    ('/', MainHandler), #redirects to mainpage
    ('/blog', MainBlog),
    ('/newpost',Newpost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler) #says our route expects URLpath that starts
], debug=True)                                #with /blog/ & ends with one or more digits
