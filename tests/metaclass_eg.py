class MyMeta(type):

    def __init__(cls, name, bases, dic):
        """
        cls:  <class '__main__.Foo'>
        name: Foo
        bases: ()
        dic: {'__module__': '__main__', '__qualname__': 'Foo', '__init__': <function Foo.__init__ at 0x000000000D721D30>, 'func': <function Foo.func at 0x000000000D721DC0>}
        """
        super().__init__(name, bases, dic)
        # print('MyMeta.init')
        # print(cls, name, bases, dic)

    def __new__(mcs, *args, **kwargs):
        """
        mcs: <class '__main__.MyMeta'>
        args: ('Foo', (), {'__module__': '__main__', '__qualname__': 'Foo', '__init__': <function Foo.__init__ at 0x000000000D721D30>})
        kwargs: {}
        """
        # print('MyMeta.new')
        # print(mcs, args, kwargs)
        return type.__new__(mcs, *args, **kwargs)

    def __call__(cls, *args, **kwargs):
        print('MyMeta.call')
        print(cls, args, kwargs)
        obj = cls.__new__(cls)
        cls.__init__(cls, *args, **kwargs)
        # cls.func(obj)
        obj.func()
        return obj


class Foo(metaclass=MyMeta):
    F = 'FIFIFIF'

    def __init__(self, name):
        # print('Foo.init')
        # print(self, name)
        self.name = name

    def func(self, *a, **kw):
        # print('Foo.func')
        # print(self, a, kw)
        pass

f = Foo('zyk')

