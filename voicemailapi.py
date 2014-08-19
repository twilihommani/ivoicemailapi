import json

from flask import Flask
from flask.ext.restful import Resource, Api, reqparse, abort
from flask_restful.reqparse import RequestParser
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import loads, dumps

app = Flask(__name__)
api = Api(app)

client = MongoClient("MongoDBUrl") # To replace

db = client.get_default_database()
collection = db.contacts

# parser heritance doesn't work now 
parser = RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('fname', type=str)
parser.add_argument('phone', type=str)
parser.add_argument('speech', type=str, location='form')

parser2 = RequestParser()
parser2.add_argument('name', type=str, required=True)
parser2.add_argument('fname', type=str, required=True)
parser2.add_argument('phone', type=str, required=True)
parser2.add_argument('speech', type=str, required=True, location='form')

parser3 = RequestParser()
parser3.add_argument('phone', type=str)


def abort_if_contact_does_not_exist(contact_id):
    try:
        _id= ObjectId(contact_id)
    except:
        abort(404, message="{} is not a correct bsonId".format(contact_id))
    contact = collection.find_one({'_id': _id})
    if not contact:
        abort(404, message="Contact {} doesn't exist".format(contact_id))

def getContactByPhone(collection, phone):
    contact = collection.find_one({'phone': phone})
    if not contact:
        abort(404, message="No contact has the phone {} associated to.".format(phone))
    return contact
    
def getContacts(collection):
    return collection.find()
    

class ContactList(Resource):
    def get(self):
        arg = parser3.parse_args()
        phone = arg.get('phone')
        if phone:
            contact = getContactByPhone(collection, phone)
            return dumps(contact), 200
        cursor = getContacts(collection)
        return dumps(cursor), 200

    def post(self):
        args = parser2.parse_args()
        objectId = collection.insert({'speech': args.get('speech'), 'name': args.get('name'), 'fname':args.get('fname'), 'phone': args.get('phone')})
        return dumps(objectId), 201


class Contact(Resource):
    def get(self, contact_id):
        abort_if_contact_does_not_exist(contact_id)
        contact = collection.find({'_id': ObjectId(contact_id)})
        return dumps(contact), 200

    def put(self, contact_id):
        abort_if_contact_does_not_exist(contact_id)
        args = parser.parse_args()
        objectId = collection.update({"_id": ObjectId(contact_id)}, {"$set": {'speech': args.get('speech')}})
        return dumps(objectId), 200

    
    def delete(self, contact_id):
        abort_if_contact_does_not_exist(contact_id)
        collection.remove({'_id': ObjectId(contact_id)})
        return '', 204

api.add_resource(ContactList, '/contacts')
api.add_resource(Contact, '/contacts/<string:contact_id>')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
