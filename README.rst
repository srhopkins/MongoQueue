
MongoQueue
==========

Simple queuing using MongoDB backend and a hybrid of Queue and pymongo
syntax.

Install
-------

This package is currently not on PyPI but you can install it with the following command.

.. ::

pip install https://github.com/srhopkins/mongoqueue/zipball/master

Instantiating a Queue
---------------------

.. code:: python

    from MongoQueue import MongoQueue
    q = MongoQueue()
Loading with ``put``
--------------------

.. code:: python

    q.put({"a_list": [1,2]})
    q.put({"a_list": [3,4]})
    q.put({"a_list": [5,6]})
Getting with ``get``
--------------------

``get()`` returns one item from queue, with status set to "working",
using pymongo ``find_and_modify()``. This provides an atomic transaction
while avoiding race conditions.

.. code:: python

    q.get()



.. parsed-literal::

    {u'_id': ObjectId('54da4c213aa23e0052b19c13'),
     u'a_list': [1, 2],
     u'status': u'working'}



Getting with generator (Lazy Method)
------------------------------------

To return a generator ... use ``get_generator()``

.. code:: python

    for item in q.get_generator():
        print item

.. parsed-literal::

    {u'status': u'working', u'a_list': [3, 4], u'_id': ObjectId('54da4c213aa23e0052b19c14')}
    {u'status': u'working', u'a_list': [5, 6], u'_id': ObjectId('54da4c213aa23e0052b19c15')}


Contrived Example
-----------------

.. code:: python

    fruit_queue = MongoQueue()
.. code:: python

    fruit_queue.put({"type": "apple"})
    fruit_queue.put({"type": "apple"})
    fruit_queue.put({"type": "orange"})
.. code:: python

    for fruit in fruit_queue.get_generator():
        if fruit["type"] == "apple":
            fruit["type"] = "sliced apple"
            fruit_queue.queue.save(fruit)
            fruit_queue.done(fruit)
        else:
            # TODO add status_error
            pass
Finding Items in Queue
----------------------

.. code:: python

    print fruit_queue.find_queued().count()
    print fruit_queue.find_done().count()
    print fruit_queue.find_working().count()

.. parsed-literal::

    0
    2
    1


.. code:: python

    for item in fruit_queue.find():
        print item

.. parsed-literal::

    {u'status': u'done', u'_id': ObjectId('54da4c263aa23e0052b19c17'), u'type': u'sliced apple'}
    {u'status': u'done', u'_id': ObjectId('54da4c263aa23e0052b19c18'), u'type': u'sliced apple'}
    {u'status': u'working', u'_id': ObjectId('54da4c263aa23e0052b19c19'), u'type': u'orange'}


Serialized Objects
------------------

You can serialize objects using ``bson`` ``Binary``; below is an example
using ``cPickle``

.. code:: python

    from bson.binary import Binary
    import cPickle as pickle
    
    def say_this(word):
        print word  
.. code:: python

    # Serialize it and .put it in queue
    myfunc = pickle.dumps(say_this)
    q.put({"myfunc": Binary(myfunc),
           "word": "bird"})
.. code:: python

    # .get it back out
    item = q.get({"myfunc": {"$exists": True}})
.. code:: python

    # .loads it and run it
    myfunc = pickle.loads(item["myfunc"])
    myfunc(item["word"])

.. parsed-literal::

    bird


Authentication and Special Client Use Cases
-------------------------------------------

By default MongoQueue trys to be a simple as possible to invoke
``q = MongoQueue`` but you may need to connect to replica sets or
require authentication in you environment.

MongoQueue accepts both ``MongoClient``, ``MongoReplicaSetClient``
instances on invocation as well.

