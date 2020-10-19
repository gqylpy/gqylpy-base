from collections.abc import Iterable


class SingletonMode:
    """Inherit me, you will
    become a singleton class."""
    _instance = None

    def __new__(cls, *a, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance


class DictMode:
    """Inherit me, You will have
    the grammar of the 'dict'."""

    def __getitem__(self, name):
        return self.__getattribute__(name)

    def __setitem__(self, name, value):
        self.__setattr__(name, value)

    def __delitem__(self, name):
        self.__delattr__(name)


class IterMode:
    """Inherit me, your object can be iterated,
    and can be called by the 'if in' statement."""

    def __iter__(self):
        yield from self


class GQYLPYDict(dict):
    """GQYLPYDict == dict
    I inherited 'dict', my main function is to
    allow the dict to get or set values by `d.key`.

    Warning:
        After testing, 'GQYLPYDict' gets values about
        2-6 times slower than the native `dict`.
    """

    def __init__(self, _data=None, **kw):
        for name, value in (_data or kw).items():
            self[name] = GQYLPYDict(value)

    def __new__(cls, _data={}, **kw):
        if isinstance(_data, dict):
            return dict.__new__(cls)

        if isinstance(_data, Iterable) and not isinstance(_data, str):
            return [GQYLPYDict(v) for v in _data]

        return _data

    def __getattribute__(self, name):
        """`self.name` to `self[name]`"""
        try:
            return super().__getitem__(name)
        except KeyError:
            try:
                return super().__getattribute__(name)
            except AttributeError:
                raise KeyError(name)

    def __setattr__(self, name, value):
        """`self.name = value` to `self[name] = value`"""
        self.__setitem__(name, value)

    def __delattr__(self, name):
        """`del self.name` to `del self[name]`"""
        self.__delitem__(name)

    def __deepcopy__(self, memo):
        """
        This method must be implemented,  otherwise
        `KeyError: '__deepcopy__'` will appear when
        `copy.deepcopy (Dict obj)` is called.
        """
        return GQYLPYDict(self)

    def __getstate__(self):
        return True

    def __setstate__(self, name):
        return True


gdict = GQYLPYDict
