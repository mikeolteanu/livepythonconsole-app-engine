"""
Created on June 10, 2012
@author: peta15
"""

from wtforms import fields
from wtforms import Form
from wtforms import validators
from lib import utils
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.i18n import ngettext, gettext

FIELD_MAXLENGTH = 50 # intended to stop maliciously long input


class FormTranslations(object):
    def gettext(self, string):
        return gettext(string)

    def ngettext(self, singular, plural, n):
        return ngettext(singular, plural, n)


class BaseForm(Form):
    def __init__(self, request_handler):
        super(BaseForm, self).__init__(request_handler.request.POST)

    def _get_translations(self):
        return FormTranslations()

# ==== Mixins ====
class PasswordConfirmMixin(BaseForm):
    password = fields.TextField(_('Password'), [validators.Required(),
                                                validators.Length(max=FIELD_MAXLENGTH, message=_(
                                                    "Field cannot be longer than %(max)d characters."))])
    c_password = fields.TextField(_('Confirm Password'),
                                  [validators.Required(), validators.EqualTo('password', _('Passwords must match.')),
                                   validators.Length(max=FIELD_MAXLENGTH,
                                                     message=_("Field cannot be longer than %(max)d characters."))])


class UsernameMixin(BaseForm):
    username = fields.TextField(_('Username'), [validators.Required(),
                                                validators.Length(max=FIELD_MAXLENGTH, message=_(
                                                    "Field cannot be longer than %(max)d characters.")),
                                                validators.regexp(utils.VALID_USERNAME_REGEXP, message=_(
                                                    "Username invalid. Use only letters and numbers."))])


class NameMixin(BaseForm):
    name = fields.TextField(_('Name'), [
        validators.Length(max=FIELD_MAXLENGTH, message=_("Field cannot be longer than %(max)d characters.")),
        validators.regexp(utils.NAME_LASTNAME_REGEXP, message=_(
            "Name invalid. Use only letters and numbers."))])
    last_name = fields.TextField(_('Last Name'), [
        validators.Length(max=FIELD_MAXLENGTH, message=_("Field cannot be longer than %(max)d characters.")),
        validators.regexp(utils.NAME_LASTNAME_REGEXP, message=_(
            "Last Name invalid. Use only letters and numbers."))])


class EmailMixin(BaseForm):
    email = fields.TextField(_('Email'), [validators.Required(),
                                          validators.Length(min=8, max=FIELD_MAXLENGTH, message=_(
                                                    "Field must be between %(min)d and %(max)d characters long.")),
                                          validators.regexp(utils.EMAIL_REGEXP, message=_('Invalid email address.'))])


# ==== Forms ====
class PasswordResetCompleteForm(PasswordConfirmMixin):
    pass


class LoginForm(UsernameMixin):
    password = fields.TextField(_('Password'), [validators.Required(),
                                                validators.Length(max=FIELD_MAXLENGTH, message=_(
                                                    "Field cannot be longer than %(max)d characters."))],
                                id='l_password')
    pass


class ContactForm(EmailMixin):
    name = fields.TextField(_('Name'), [validators.Required(),
                                        validators.Length(max=FIELD_MAXLENGTH, message=_(
                                                    "Field cannot be longer than %(max)d characters.")),
                                        validators.regexp(utils.NAME_LASTNAME_REGEXP, message=_(
                                                    "Name invalid. Use only letters and numbers."))])
    message = fields.TextAreaField(_('Message'), [validators.Required(), validators.Length(max=65536)])
    pass


class RegisterForm(PasswordConfirmMixin, UsernameMixin, NameMixin, EmailMixin):
    country = fields.SelectField(_('Country'), choices=[])
    tz = fields.SelectField(_('Timezone'), choices=[])
    pass


class EditProfileForm(UsernameMixin, NameMixin):
    country = fields.SelectField(_('Country'), choices=[])
    tz = fields.SelectField(_('Timezone'), choices=[])
    pass


class EditPasswordForm(PasswordConfirmMixin):
    current_password = fields.TextField(_('Password'), [validators.Required(),
                                                        validators.Length(max=FIELD_MAXLENGTH, message=_(
                                                            "Field cannot be longer than %(max)d characters."))])
    pass


class EditEmailForm(BaseForm):
    new_email = fields.TextField(_('Email'), [validators.Required(),
                                              validators.Length(min=8, max=FIELD_MAXLENGTH, message=_(
                                                    "Field must be between %(min)d and %(max)d characters long.")),
                                              validators.regexp(utils.EMAIL_REGEXP,
                                                                message=_('Invalid email address.'))])
    password = fields.TextField(_('Password'), [validators.Required(),
                                                validators.Length(max=FIELD_MAXLENGTH, message=_(
                                                    "Field cannot be longer than %(max)d characters."))])
    pass

class ScriptEditForm(BaseForm):
    
    codes_content = fields.TextAreaField(_('Code Content'), [validators.Required(), validators.Length(max=65536)])
    script_url_ext = fields.TextField(_('Host at /pub/'))
    show_source = fields.BooleanField(_('Show source code when run by public'))
    html_output = fields.BooleanField(_('HTML console output'))
    pass


class LivePythonConsoleForm(BaseForm):
    
    codes_name = fields.TextField(_('Code Name'), [validators.Required(), validators.Length(max=255)])
    codes_content = fields.TextAreaField(_('Code Content'), [validators.Required(), validators.Length(max=65536)])
    save_to_datastore = fields.BooleanField(_('Save to datastore'))
    show_source = fields.BooleanField(_('Show source code when run by public'))
    html_output = fields.BooleanField(_('HTML console output'))
    script_url_ext = fields.TextField(_('Host at /pub/'))
    pass

