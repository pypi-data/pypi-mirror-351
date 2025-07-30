# Matrix client class
import PythonAPIClientBase
from .MatrixLoginSession import MatrixLoginSessionFromUsernameAndPassword, MatrixLoginSessionFromAccessToken
import json
import uuid
import hmac
import hashlib
import PythonAPIClientBase

usernameInvalidChars=" :@!"

class MatrixClient(PythonAPIClientBase.APIClientBase):
    chat_domain = None
    def __init__(self, chat_domain, mock=None, forceOneRequestAtATime=False, verboseLogging=PythonAPIClientBase.VerboseLoggingNullLogClass()):
        useBaseUrl = chat_domain
        if useBaseUrl != "MOCK":
            useBaseUrl = "https://" + useBaseUrl
        super().__init__(baseURL=useBaseUrl, mock=mock, forceOneRequestAtATime=forceOneRequestAtATime, verboseLogging=verboseLogging)
        self.chat_domain=chat_domain

    def getLoginSessionFromUsernameAndPassword(self, username, password):
        return MatrixLoginSessionFromUsernameAndPassword(client=self, username=username, password=password)

    def getLoginSessionFromAccessToken(self, user_id, access_token, device_id):
        return MatrixLoginSessionFromAccessToken(client=self, user_id=user_id, access_token=access_token, device_id=device_id)

    def get_userid_from_username(self, username):
        if not self.isValidUsername(username):
            raise Exception("Invalid user name")
        return "@" + username + ":" + self.chat_domain

    def get_shared_secret_nonce(self):
        response = self.sendGetRequest(
            url="/_synapse/admin/v1/register",
            loginSession=None
        )
        if response.status_code!=200:
            raise Exception("Error getting registration nonce")
        return json.loads(response.text)["nonce"]

    def registerNewUser(self, username, password, displayname, registration_shared_secret=None):
        if not self.isValidUsername(username):
            raise Exception("Invalid user name")

        nonce = self.get_shared_secret_nonce()
        mac_data = f"{nonce}\0{username}\0{password}\0notadmin"
        mac = hmac.new(
            registration_shared_secret.encode(),
            mac_data.encode(),
            hashlib.sha1
        ).hexdigest()

        postData={
            "nonce": nonce,
            "username": username,
            "displayname": displayname,
            "password": password,
            "admin": False,
            "mac": mac
        }
        response = self.sendPostRequest(
            "/_synapse/admin/v1/register", loginSession=None,
            data=json.dumps(postData)
        )
        if response.status_code != 200:
            # print(response.status_code)
            # print(response.text)
            return (None, None, None)
        resp = json.loads(response.text)
        return (
            resp["user_id"],
            resp["access_token"],
            resp["device_id"]
        )

    def getAllUsers(self, login_session):
        postData={
            "limit": 1
        }
        response = self.sendPostRequest(
            "/_matrix/client/v3/user_directory/search", loginSession=login_session,
            data=json.dumps(postData)
        )

        print("rs", response.text)
        print("h", response.headers)

        return [1,2,3]

    # admin_login_session = admin_login_session,
    # room_topic = room_topic,
    # room_name = room_name,
    # room_alias_name = room_alias_name,
    # invite_list = [admin_login_session.get_user_id(), login_session.get_user_id()]
    def create_room(
        self,
        login_session,
        room_topic,
        room_name,
        room_alias_name,
        invite_list
    ):
        # POST
        create_room_body = {
            "creation_content": {},
            "initial_state": [
                {
                    "type": "m.room.join_rules",
                    "state_key": "",
                    "content": {
                        "join_rule": "invite"
                    }
                },
                {
                    "type": "m.room.history_visibility",
                    "state_key": "",
                    "content": {
                        "history_visibility": "shared"
                    }
                },
                {
                    "type": "m.room.guest_access",
                    "state_key": "",
                    "content": {
                        "guest_access": "forbidden"
                    }
                }
            ],
            "invite": invite_list,
            "invite_3pid": [],
            "is_direct": False,
            "name": room_name,
            "room_alias_name": room_alias_name,
            "room_version": "11",
            "topic": room_topic,
            "visibility": "private"
        }
        response = self.sendPostRequest(
            "/_matrix/client/v3/createRoom",
            loginSession=login_session,
            data=json.dumps(create_room_body)
        )
        if response.status_code != 200:
            print("ERROR")
            print("status", response.status_code)
            print("text", response.text)
            raise Exception("Error failed to create room")
        return json.loads(response.text)["room_id"]

    def invite_user_to_room(
        self,
        login_session,
        room_id,
        user_id,
        reason
    ):
        # POST
        invite_body = {
            "reason": reason,
            "user_id": user_id
        }
        response = self.sendPostRequest(
            "/_matrix/client/v3/rooms/" + room_id + "/invite",
            loginSession=login_session,
            data=json.dumps(invite_body)
        )
        if response.status_code != 200:
            print("ERROR")
            print("status", response.status_code)
            print("text", response.text)
            raise Exception("Error failed to invite user to room")
        return

    def isUsernameAvailiable(self, username):
        response = self.sendGetRequest(
            url="/_matrix/client/v3/register/available?username=" + username,
            loginSession=None
        )
        if response.status_code==200:
            return True
        return False

    def get_own_display_name(self, login_session):
        return self.get_display_name(login_session, userid=login_session.get_user_id())

    def get_display_name(self, login_session, userid):
        response = self.sendGetRequest(
            url="/_matrix/client/v3/profile/" + userid + "/displayname",
            loginSession=login_session,
        )
        if response.status_code==200:
            return json.loads(response.text)["displayname"]
        if response.status_code==404:
            return "" # no profile set or user doesn't exist
        print("Error getting display name")
        print("code:", response.status_code)
        print("text", response.text)
        raise Exception("Error getting display name")

    def update_own_display_name(self, login_session, display_name):
        return self.update_display_name(login_session=login_session, userid=login_session.get_user_id(), display_name=display_name)

    def update_display_name(self, login_session, userid, display_name, skip_not_required_check=False):
        if not skip_not_required_check:
            if display_name == self.get_display_name(login_session=login_session, userid=userid):
                return
        put_body = {
            "displayname": display_name
        }
        response = self.sendPutRequest(
            url="/_matrix/client/v3/profile/" + userid + "/displayname",
            loginSession=login_session,
            data=json.dumps(put_body)
        )
        if response.status_code==200:
            return True
        print("XX", userid)
        print("YY", login_session.get_user_id())
        print("response.status_code", response.status_code)
        print("response.text", response.text)
        raise Exception("FAiled to change display name")

    def auto_register_user(
        self,
        admin_login_session,  # Used for room creation
        registration_shared_secret,
        username,
        displayname,
        user_password_fetch_function,
        user_password_store_function,
    ):
        #auto register a user and return a current login session
        if not self.isValidUsername(username):
            raise Exception("Invalid user name")
        # Doesn't use login_session. it will create a user than log in as that user
        login_session = None
        password = user_password_fetch_function(username=username)
        if self.isUsernameAvailiable(username=username):
            if password != None:
                raise Exception("Error - user is available but a password is stored")
            password = str(uuid.uuid4())
            (user_id, access_token, device_id) = self.registerNewUser(
                username=username,
                password=password,
                displayname=displayname,
                registration_shared_secret=registration_shared_secret
            )
            if access_token is None:
                raise Exception("Failed to register user")
            user_password_store_function(username=username, password=password)
            login_session = self.getLoginSessionFromAccessToken(user_id=user_id, access_token=access_token, device_id=device_id)
        else:
            if password == None:
                raise Exception("Error - user already created but we have no password stored")
            login_session = self.getLoginSessionFromUsernameAndPassword(username=username, password=password)

        # Creation doesn't seem to update display name so do it here
        self.update_display_name(login_session=login_session, userid=self.get_userid_from_username(username), display_name=displayname)

        return login_session

    def auto_invite_user_create_room_if_required(
        self,
        admin_login_session,
        clubchat_room_id,
        user_id,
        room_topic,
        room_name,
        room_alias_name,
        room_fetch_function,  # fetch room id's (key is clubchat_room_id)
        room_store_function,  # Store room id's
        invite_reason
    ):
        room_id = room_fetch_function(clubchat_room_id)
        if room_id is not None:
            self.invite_user_to_room(
                login_session=admin_login_session,
                room_id=room_id,
                user_id=user_id,
                reason=invite_reason
            )
        else:
            room_id = self.create_room(
                login_session=admin_login_session,
                room_topic=room_topic,
                room_name=room_name,
                room_alias_name=room_alias_name,
                invite_list=[user_id] # no need to include admin as that is creator
            )
            room_store_function(clubchat_room_id, room_id)
        return room_id

    def auto_register_user_in_room(
        self,
        admin_login_session, # Used for room creation
        registration_shared_secret,
        username,
        displayname,
        user_password_fetch_function,
        user_password_store_function,
        clubchat_room_id,  #unique identifier of clubchat room
        room_topic,
        room_name,
        room_alias_name,
        room_fetch_function, #fetch room id's (key is clubchat_room_id)
        room_store_function, #Store room id's
        invite_reason="Join the chat"
    ):
        login_session = self.auto_register_user(
            admin_login_session=admin_login_session,  # Used for room creation
            registration_shared_secret=registration_shared_secret,
            username=username,
            displayname=displayname,
            user_password_fetch_function=user_password_fetch_function,
            user_password_store_function=user_password_store_function,
        )

        room_id = self.auto_invite_user_create_room_if_required(
            admin_login_session,
            clubchat_room_id,
            user_id=login_session.get_user_id(),
            room_topic=room_topic,
            room_name=room_name,
            room_alias_name=room_alias_name,
            room_fetch_function=room_fetch_function,
            room_store_function=room_store_function,
            invite_reason=invite_reason
        )

        return {
            "login_session": login_session, # Needed as auth token is extracted
            "room_id": room_id
        }

    def isValidUsername(self, username):
        for char in usernameInvalidChars:
            if char in username:
                return False
        if username != username.lower():
            return False
        return True