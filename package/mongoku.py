from pymongo import MongoClient, MongoReplicaSetClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId

status_queued = {"status": "queued"}
status_working = {"status": "working"}
status_error = {"status": "error"}
status_done = {"status": "done"}

class QueueMaster():
    def __init__(self, client="localhost", db="MongoQueue", queue="anonymous"):
        try:
            self.client = MongoClient(client)
        except ConnectionFailure:
            raise Exception("Please provide client information.")
        self.db = self.client[db]
        self.queues = self.db.collection_names
    
class MongoConnection():
    # TODO add support for MongoReplicaSetClient
    def __init__(self, client, db, queue):
        if isinstance(client, MongoClient) or isinstance(client, MongoReplicaSetClient):
            self.client = client
        else:
            try:
                self.client = MongoClient(client)
            except ConnectionFailure:
                raise Exception("Please provide client information.")
        self.db = self.client[db]
        _id = str(ObjectId())
        self.queue = self.db["%s-%s" % (queue, _id)]

class MongoQueue():
    def __init__(self, client="localhost", db="MongoQueue", queue="anonymous", qtype="fifo"):
        self.mongo = MongoConnection(client, db, queue)
        self.queue = self.mongo.queue
        
    def put(self, item):
        commit = dict(status_queued.items() + item.items())
        rec = self.queue.insert(commit)
        
    def puts(self, items):
        commit = [{"meta": status_queued, "item": item} for item in items]
        self.queue.insert(commit, {"ordered": True})
        
    def get(self, query=status_queued):
        # Returns one single work item, oldest first.
        # Watch out if you are just trying to view the record; use .find instead.
        # .get will always set status to working
        return self.queue.find_and_modify(query=query,
                                          update={"$set": status_working},
                                          new=True)
             
    def gets(self, query=status_queued):
        # Returns a generator to loop through work.
        while True:
            item = self.get(query)
            if item:
                yield item
            else:
                raise StopIteration
                
    def done(self, item):
        item["status"] = "done"
        self.queue.save(item)
                
    def find_one(self, query={}):
        return self.queue.find_one(query)
    
    def find(self, query={}):
        return self.queue.find(query)
    
    def find_done(self):
        return self.queue.find(status_done)
    
    def find_working(self):
        return self.queue.find(status_working)
    
    def find_queued(self):
        return self.queue.find(status_queued)
