import os


def log(data):
    with open(curr_directory() + '/logs.log', 'a') as fl:
        fl.write(str(data) + '\n')


def curr_directory():
    return os.path.dirname(os.path.realpath(__file__))


class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if 'Bot' in str(cls):
           print("bot sinifi")
        if cls.obj is None:
            cls.obj = Singleton()
        return cls._instance

   
