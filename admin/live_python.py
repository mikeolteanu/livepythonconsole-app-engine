# -*- coding: utf-8 -*-
import webapp2
from boilerplate import models
from boilerplate import forms
from boilerplate.handlers import BaseHandler
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb
from google.appengine.api import users
from collections import OrderedDict, Counter
from wtforms import fields
import logging
from google.appengine.api import memcache
import uuid

global output_list

def execwrapper(exec_string):
    UID = str(uuid.uuid1())
    cachePrintLog.clear_id(UID)
    exec_line_list=exec_string.split("\n")
    exec_line_list_new = []
    for line in exec_line_list:
        comment_pos=line.find("#")
        if comment_pos>-1:
            line=line[:comment_pos]
        if "print " in line:
            line = line.replace("print ","cachePrintLog.add_to_id(\"" + UID + "\",str(")
            line = line + "))"
        exec_line_list_new.append(line)
    exec("\n".join(exec_line_list_new))
    return str(memcache.get(UID))

class cachePrintLog(object):

    @staticmethod
    def clear_id(idstring):
        memcache.set(key=idstring, value="", time=60)

    @staticmethod
    def add_to_id(idstring,logline):
        memcache_so_far = str(memcache.get(idstring))
        memcache.set(key=idstring, value=memcache_so_far + "\n" + logline, time=60)
        
class LivePythonForm(forms.LivePythonConsoleForm):
    pass

class LivePythonHandler(BaseHandler):
    def get(self):
        users = models.User.query().fetch(projection=['country'])
        users_by_country = Counter()
        for user in users:
            if user.country:
                users_by_country[user.country] += 1
        params = {
        }
        return self.render_template('admin/live_python.html', **params)

    def post(self):
        codes_name = self.form.code_name.data
        codes_content = self.form.code_content.data
        console_output = execwrapper(str(codes_content)).replace("\n","<BR>").replace(" ","&nbsp;").replace("\t","&nbsp;&nbsp;&nbsp;&nbsp;")
        codes_content = codes_content.replace("\n","<BR>").replace(" ","&nbsp;").replace("\t","&nbsp;&nbsp;&nbsp;&nbsp;")
        params = {
            "codes_name": codes_name,
            "codes_content": codes_content,
            "console_output": console_output
        }
        return self.render_template('admin/live_python.html', **params)


    @webapp2.cached_property
    def form(self):
        f = LivePythonForm(self)
        return f

