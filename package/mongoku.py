from pymongo import MongoClient, MongoReplicaSetClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId


class Status():
    def __init__(self):
        self._statuses = ["queued", "working", "exception", "done"] 
        for status_type in self._statuses:
            setattr(self, status_type, {"status": status_type})

class Item(object):
    def __init__(self, mqueue, _dict):
        self._mqueue = mqueue
        self._dict = _dict
        for status in self._mqueue._statuses._statuses:
            setattr(self, status, self._put_type(status))

    def __setattr__(self, k, v):
        if k == "item":
            self._dict[k] = v
        else:
            self.__dict__[k] = v
            
    @property
    def meta(self):
        return self._dict["meta"]
    
    @property
    def item(self):
        return self._dict["item"]
    
    def _put_type(self, status):
        def _put(status=status):
            self._dict["meta"]["status"] = status
            old_id = self._dict["_id"]
            del self._dict["_id"]
            new_record = self._mqueue.queue.insert(self._dict)
            self._mqueue.queue.delete_one({"_id": old_id})
            self._dict = self._mqueue.find_one({"_id": new_record})
        return _put
    
    def delete(self):
        self._mqueue.queue.delete_one({"_id": self._dict["_id"]})
    
    
class MongoConnection():
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
        self._statuses = Status()
        self.mongo = MongoConnection(client, db, queue)
        self.queue = self.mongo.queue
        
    def put(self, item):
        return self.queue.insert({
                "meta": self._statuses.queued,
                "item": item
                })
        
    def puts(self, items):
        commit = [{"meta": self._statuses.queued, "item": item} for item in items]
        self.queue.insert(commit, {"ordered": True})
        
    def get(self, query="queued"):
        query = {"meta.status": query}
        # Returns one single work item, oldest first.
        # Watch out if you are just trying to view the record; use .find instead.
        # .get will always set status to working
        item = self.queue.find_and_modify(query=query,
                                          update={"$set": {"meta.status": "working"}},
                                          new=True)
        return Item(self, item) if item else None
             
    def gets(self, query="queued"):
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
