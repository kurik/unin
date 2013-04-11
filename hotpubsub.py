# -*- coding: utf-8 -*-

"""HotPubSub is a Python library that allows you to use Redis as a message queue
within your Python programs.
It is based on HotQueue: git@github.com:richardhenry/hotqueue.git
"""

from functools import wraps
try:
    import cPickle as pickle
except ImportError:
    import pickle

from redis import Redis


__all__ = ['HotPubSub']

__version__ = '0.0.1'

class HotPubSub(object):
    def __init__(self, name, serializer=pickle, **kwargs):
        self.name = name
        self.serializer = serializer
        self.__redis = Redis(**kwargs)
        self.__pub = self.__redis.pubsub()
        self.__sub = self.__redis.pubsub()
        self.__sub.subscribe(self.name)
    
    def clear(self):
        self.__sub.reset()
    
    def consume(self, **kwargs):
        kwargs.setdefault('block', True)
        try:
            while True:
                msg = self.get(**kwargs)
                if msg is None:
                    break
                yield msg
        except KeyboardInterrupt:
            print; return
    
    def get(self, block=False, timeout=None):
        msg = self.__sub.listen()
        if msg != None:
            #msg = self.serializer.loads(self.__sub.listen())
            #msg = self.serializer.loads(self.__sub.parse_response())
            msg = self.__sub.parse_response()[2]
            msg = self.serializer.loads(msg)
        return msg
    
    def put(self, *msgs):
        if self.serializer is not None:
            msgs = map(self.serializer.dumps, msgs)
        self.__pub.execute_command('PUBLISH', self.name, *msgs)
    
    def worker(self, *args, **kwargs):
        def decorator(worker):
            @wraps(worker)
            def wrapper(*args):
                for msg in self.consume(**kwargs):
                    worker(*args + (msg,))
            return wrapper
        if args:
            return decorator(*args)
        return decorator

