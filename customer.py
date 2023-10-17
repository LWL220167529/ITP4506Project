from user import User
import json

class Customer(User):
    def __init__(self, name, email, id, password, address):
        super().__init__(name, email, id, password)
        self.address = address

    def User():
        return 'Customer'