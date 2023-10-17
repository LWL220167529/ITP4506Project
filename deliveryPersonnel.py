from user import User
import json

class DeliveryPersonnel(User):
    def __init__(self, name, email, id, password):
        super().__init__(name, email, id, password)