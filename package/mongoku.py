from pymongo import MongoClient, MongoReplicaSetClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId

status_queued = {"status": "queued"}
status_working = {"status": "working"}
status_error = {"status": "error"}
status_done = {"status": "done"}


class Item(object):
    def __init__(self, mqueue, _dict):
        self._mqueue = mqueue
        self._dict = _dict
        
    @property
    def meta(self):
        return self._dict["meta"]
    
    @property
    def item(self):
        return self._dict["item"]
    
    def _put(self):
        self._mqueue.put(self._dict)
    
    def queued(self):
        pass
    
    def working(self):
        pass
    
    def exception(self):
        pass
    
    def done(self):
        pass
    
    
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
        rec = self.queue.insert({
                "meta": status_queued,
                "item": item
                })
        
    def puts(self, items):
        commit = [{"meta": status_queued, "item": item} for item in items]
        self.queue.insert(commit, {"ordered": True})
        
    def get(self, query={"meta.status": "queued"}):
        # Returns one single work item, oldest first.
        # Watch out if you are just trying to view the record; use .find instead.
        # .get will always set status to working
        item = self.queue.find_and_modify(query=query,
                                          update={"$set": {"meta.status": "working"}},
                                          new=True)
        return Item(self, item) if item else None
             
    def gets(self):
        # Returns a generator to loop through work.
        while True:
            item = self.get()
            if item:
                yield item
            else:
                raise StopIteration
                
    def find_one(self, query={}):
        return self.queue.find_one(query)
    
    def find(self, query={}):
        return self.queue.find(query)
