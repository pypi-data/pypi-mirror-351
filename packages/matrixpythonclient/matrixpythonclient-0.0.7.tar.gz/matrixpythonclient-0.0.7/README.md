 # MatrixPythonClient


TODO

- Finsih review of https://spec.matrix.org/v1.14/client-server-api/#standard-error-response
- Create a new user
- Add login endpoint for user providing access token in saas_club
- Endpoint creates a new user OR logs in as existing one




I need some kind of generic room user to be added to all rooms created this way.

Questions 
- can Admin see all the users on server
- can Admin see all the rooms on the server
- should I group rooms in any way? Spaces???
- e2e implications



# Terms
username = username such as admin
userid = with domain etc. @admin:chat.metcarob.com

room_name = room name e.g. TestRoom
room_alais_name = room alais e.g. TestRoom
room_id = Internal ID of room e.g.