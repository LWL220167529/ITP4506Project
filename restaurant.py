from user import User
import json

class Restaurant(User):
    def __init__(self, name, email, id, password, address):
        super().__init__(name, email, id, password)
        self.address = address

    def getAddress(self):
        return self.address
