import json

from random import choice

from locust import (
    HttpUser,
    SequentialTaskSet,
    TaskSet,
    task,
    between
)


HOST = "http://localhost:8000"
VOTING = 1
#VOTING_TYPE: "yesno" || "classic" || "comment" || "preference" || "choices"
VOTING_TYPE = "preference" 


class DefVisualizer(TaskSet):

    @task
    def index(self):
        self.client.get("/visualizer/{0}/".format(VOTING))


class DefVoters(SequentialTaskSet):

    def on_start(self):
        with open('voters.json') as f:
            self.voters = json.loads(f.read())
        self.voter = choice(list(self.voters.items()))

    @task
    def login(self):
        username, pwd = self.voter
        self.token = self.client.post("/authentication/login/", {
            "username": username,
            "password": pwd,
        }).json()

    @task
    def getuser(self):
        self.usr= self.client.post("/authentication/getuser/", self.token).json()
        print( str(self.usr))

    @task
    def booth(self):
        headers = {
            'Authorization': 'Token ' + self.token.get('token'),
            'content-type': 'text/html'
        }
        self.client.get("/booth/{0}/".format(VOTING), headers=headers)

    @task
    def voting(self):
        headers = {
            'Authorization': 'Token ' + self.token.get('token'),
            'content-type': 'application/json'
        }
        if VOTING_TYPE != "choices":
            self.client.post("/store/", json.dumps({
                "token": self.token.get('token'),
                "vote": {
                    "a": "12",
                    "b": "64"
                },
                "voter": self.usr.get('id'),
                "voting": VOTING,
                "voting_type": VOTING_TYPE
            }), headers=headers)
        else:
            self.client.post("/store/", json.dumps({
                "token": self.token.get('token'),
                "votes": [{
                    "a": "12",
                    "b": "64"
                },
                {
                    "a": "24",
                    "b": "38"
                }],
                "voter": self.usr.get('id'),
                "voting": VOTING,
                "voting_type": VOTING_TYPE
            }), headers=headers)


    def on_quit(self):
        self.voter = None

class DefBooth(TaskSet):
    @task
    def index(self):
        self.client.get("/booth/{0}/".format(VOTING))

class DefHome(SequentialTaskSet):
    
    def on_start(self):
        with open('voters.json') as f:
            self.voters = json.loads(f.read())
        self.voter = choice(list(self.voters.items()))
    
    @task
    def index(self):
        self.client.get("/")

    @task
    def login_view(self):
        self.client.get("/authentication/login-view/")

    @task
    def login(self):
        username, pwd = self.voter
        self.token = self.client.post("/authentication/login/", {
            "username": username,
            "password": pwd,
        }).json()

class Visualizer(HttpUser):
    host = HOST
    tasks = [DefVisualizer]
    wait_time = between(3,5)



class Voters(HttpUser):
    host = HOST
    tasks = [DefVoters]
    wait_time= between(3,5)

class Booth(HttpUser):
    host = HOST
    tasks = [DefBooth]
    wait_time = between(3,5)    

class Home(HttpUser):
    host = HOST
    tasks = [DefHome]
    wait_time = between(3,5)    
