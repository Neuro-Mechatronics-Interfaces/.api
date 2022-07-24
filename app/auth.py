import tornado
from tornado.web import RequestHandler
import requests
import json
import os

DATA_API_URL = "https://data.mongodb-api.com/app/data-xpaqj/endpoint/data/v1/action/findOne"
API_KEY = os.getenv('NML_MONGODB_LOGIN_API_KEY') 

# could define get_user_async instead
def get_user(request_handler):
    return request_handler.get_cookie("user")

# could also define get_login_url function (but must give up LoginHandler)
login_url = "/login"

# optional login page for login_url
class LoginHandler(RequestHandler):

    def get(self):
        try:
            errormessage = self.get_argument("error")
        except Exception:
            errormessage = ""
        self.render("login.html", errormessage=errormessage)

    def check_permission(self, username, password):
        payload = json.dumps({
            "collection": "credentials",
            "database": "login",
            "dataSource": "dev0",
            "filter": {"user": username}
        })
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Request-Headers': '*',
            'api-key': API_KEY
        }
        response = requests.request("POST", DATA_API_URL, headers=headers, data=payload)
        data = response.json()
        credentials = data['document']
        if credentials is None:
            print(f'Bad combination ({username}::{password})')
            return False
        if password == credentials['pass']:
            return True
        return False

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self.check_permission(username, password)
        if auth:
            self.set_current_user(username)
            self.redirect("/")
        else:
            error_msg = "?error=" + tornado.escape.url_escape("Login incorrect")
            self.redirect(login_url + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

# optional logout_url, available as curdoc().session_context.logout_url
logout_url = "/logout"

# optional logout handler for logout_url
class LogoutHandler(RequestHandler):

    def get(self):
        self.clear_cookie("user")
        self.redirect("/")
