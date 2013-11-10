from webapp2_extras.routes import RedirectRoute
import users
import live_python


_routes = [
    RedirectRoute('/admin/logout/', users.AdminLogoutHandler, name='admin-logout', strict_slash=True),
    RedirectRoute('/admin/', live_python.LivePythonHandler, name='live_python', strict_slash=True),
    RedirectRoute('/admin/g/', users.AdminGeoChartHandler, name='geochart', strict_slash=True),
    RedirectRoute('/admin/live_python/', live_python.LivePythonHandler, name='live_python', strict_slash=True),
    RedirectRoute('/admin/script_manage/', live_python.PythonScriptManagerHandler, name='script_manage', strict_slash=True),
    RedirectRoute('/admin/users/', users.AdminUserListHandler, name='user-list', strict_slash=True),
    RedirectRoute('/admin/users/<user_id>/', users.AdminUserEditHandler, name='user-edit', strict_slash=True, handler_method='edit'),
    RedirectRoute('/admin/scriptedit/<codes_name>/', live_python.AdminScriptEditHandler, name='script-edit', strict_slash=True, handler_method='edit')
]

def get_routes():
    return _routes

def add_routes(app):
    for r in _routes:
        app.router.add(r)
