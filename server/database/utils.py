import uuid

class Value:
    def __init__(self, data):
        self.index = str(uuid.uuid4())
        self.data = data
    
    def __repr__(self):
        return f"Value(data={self.data})"
    
    def dot(self, other):
        out = (self.data).dot(other.data)
        return out
        
    def decrypt(self):
        out = (self.data).decrypt()
        return out