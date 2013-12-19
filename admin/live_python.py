# -*- coding: utf-8 -*-
import webapp2
from boilerplate import models
from boilerplate import forms
from boilerplate.handlers import BaseHandler
from boilerplate.lib.decorators import user_required
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb
from google.appengine.api import users
from collections import OrderedDict, Counter
from wtforms import fields
import logging
from google.appengine.api import memcache
import uuid
from google.appengine.api import app_identity

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

class LivePythonEditForm(forms.ScriptEditForm):
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
        codes_name = self.form.codes_name.data
        codes_content = self.form.codes_content.data
        save_to_datastore = self.form.save_to_datastore.data
        script_url_ext = self.form.script_url_ext.data
        show_source = self.form.show_source.data
        html_output = self.form.html_output.data 
        if save_to_datastore and codes_name != "":
            script_key = ndb.Key('PyScript', codes_name)
            ent = PyScript(key=script_key,codes_name=codes_name,codes_content=codes_content,script_url_ext=script_url_ext,show_source=show_source,html_output=html_output)
            ent.put()
        console_output = execwrapper(str(codes_content))
        if html_output==False:
            console_output = console_output.replace("\n","<BR>").replace(" ","&nbsp;").replace("\t","&nbsp;&nbsp;&nbsp;&nbsp;")
        codes_content = '<textarea rows="10" cols="50">' + codes_content + '</textarea>'
        params = {
            "codes_name": codes_name,
            "codes_content": codes_content,
            "console_output": console_output,
            "save_to_datastore": save_to_datastore,
            "pub_url": 'http://' + str(app_identity.get_application_id()) + ".appspot.com/pub/" + script_url_ext
        }
        return self.render_template('admin/live_python.html', **params)


    @webapp2.cached_property
    def form(self):
        f = LivePythonForm(self)
        return f

class PythonScriptManagerHandler(BaseHandler):
    def get(self):

        scripts = PyScript.query().fetch(1000)

        params = {
            "list_columns": [('codes_name', 'Script Name'),
#                             ('codes_content', 'Script Content'),
                             ('script_url_ext', 'Script URL  - <b>http://' + str(app_identity.get_application_id()) + ".appspot.com/pub/</b>")],
            "scripts": scripts
            
        }
        return self.render_template('admin/listscripts.html', **params)

class AdminScriptEditHandler(BaseHandler):
    def get_or_404(self, codes_name):
        try:
            script = PyScript.get_by_id(codes_name)
            if script:
                return script
        except ValueError:
            pass
        self.abort(404)

    def edit(self, codes_name):
        if self.request.POST:
            script = self.get_or_404(codes_name)
            if self.form.validate():
                self.form.populate_obj(script)
                script.put()
                self.add_message("Changes saved!", 'success')
                return self.redirect_to("script-edit", codes_name=codes_name)
            else:
                self.add_message("Could not save changes!", 'error')
        else:
            script = self.get_or_404(codes_name)
            self.form.process(obj=script)

        params = {
            'script': script
        }
        return self.render_template('admin/editscript.html', **params)

    @webapp2.cached_property
    def form(self):
        f = LivePythonEditForm(self)
        return f


class PyScript(ndb.Model):
    codes_name = ndb.StringProperty()
    codes_content = ndb.TextProperty()
    script_url_ext = ndb.StringProperty()
    show_source = ndb.BooleanProperty()
    html_output = ndb.BooleanProperty()

class PublicPythonScriptRun(BaseHandler):
    """
    Only accessible to users that are logged in
    """
    def get_or_404(self, url):
        try:
            script = PyScript.query(PyScript.script_url_ext == url).fetch(1)
            if len(script)==1:
                return script[0]
        except ValueError:
            pass
        self.abort(404)
        
    def get(self, url):
        script = self.get_or_404(url)
        console_output = execwrapper(str(script.codes_content))
        if script.html_output==False:
            console_output = console_output.replace("\n","<BR>").replace(" ","&nbsp;").replace("\t","&nbsp;&nbsp;&nbsp;&nbsp;")
        if script.show_source == True:
            source = '<textarea rows="10" cols="50">' + script.codes_content + '</textarea>'
        else:
            source = ""
        try:
            params = {
                "console_output" : console_output,
                "script_source" : source
                }
            return self.render_template('run_script.html', **params)
        except (AttributeError, KeyError), e:
            return "run script error:" + " %s." % e
