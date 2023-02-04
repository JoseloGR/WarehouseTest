import json

def serializer(data):
    return json.dumps(data).encode()

def deserializer(serialized):
    return json.loads(serialized)
