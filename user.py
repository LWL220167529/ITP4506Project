class User:
    def __init__(self, name, email, id, password):
        self.name = name
        self.email = email
        self.id = id
        self.password = password

    def getName(self):
        return self.name

    def getEmail(self):
        return self.email
    
    def getId(self):
        return self.id
    
    def getPassword(self):
        return self.password