from PythonAPIClientBase import LoginSession
import json

login_method = "m.login.password"

class MatrixLoginSession(LoginSession):
    logged_in_data = None
    def get_user_id(self):
        return self.logged_in_data["user_id"]

    def injectHeaders(self, headers):
        headers["Authorization"] = "Bearer " + self.logged_in_data["access_token"]

    def refresh(self):
        return False

    def get_login_session(self):
        #of the form
        #self.logged_in_data={'user_id': '@admin:chat.metcarob.com', 'access_token': 'xxxx', 'device_id': 'yyyy'}
        # not sure if I should force the fields
        #self.logged_in_data={'user_id': '@admin:chat.metcarob.com', 'access_token': 'xxxx', 'device_id': 'yyyy'}
        return self.logged_in_data


class MatrixLoginSessionFromAccessToken(MatrixLoginSession):
    def __init__(self, client, user_id, access_token, device_id):
        self.logged_in_data = {
            "user_id": user_id,
            "access_token": access_token,
            "device_id": device_id
        }

class MatrixLoginSessionFromUsernameAndPassword(MatrixLoginSession):
    client = None
    username = None
    password = None

    def __init__(self, client, username, password):
        self.client = client
        self.username = username
        self.password = password

        response = client.sendGetRequest("/_matrix/client/r0/login", loginSession=None, origin=None, injectHeadersFn=None, params=None)
        if (response.status_code != 200):
            print(response.status_code)
            print(response.text)
            raise Exception("Bad response from server")

        login_info = json.loads(response.text)
        login_method_to_use = None
        for flow in login_info["flows"]:
            if flow["type"] == login_method:
                login_method_to_use = flow

        if login_method_to_use is None:
            raise Exception("Login method not supported on server")

        login_data = {
            "type": login_method_to_use["type"],
            "user": self.username,
            "password": self.password
        }

        login_response = client.sendPostRequest("/_matrix/client/r0/login", loginSession=None, data=json.dumps(login_data))
        if login_response.status_code != 200:
            print(login_response.status_code)
            print(login_response.text)
            raise Exception("Failed to log on")

        self.logged_in_data = json.loads(login_response.text)
        #self.logged_in_data={'user_id': '@admin:chat.metcarob.com', 'access_token': 'xxxx', 'device_id': 'yyyy'}

