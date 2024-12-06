import json
import os
def read(fs):
    with open(fs,'r') as f:
        return json.load(f)

def write(fs, data):
    with open(fs,'w') as f:
        json.dump(data,f)

def create(fs, data):
    with open(fs,'x') as f:
        json.dump(data,f)

def delete(fs):
    if os.path.exists(fs):
        os.remove(fs)
