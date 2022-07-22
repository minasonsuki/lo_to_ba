#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


if __name__ == '__main__':
    class MyClass1(metaclass=Singleton):
        def __init__(self):
            print("MyClass1 init. id: " + str(id(self)))

    class MyClass2(metaclass=Singleton):
        def __init__(self):
            print("MyClass2 init. id: " + str(id(self)))

    myClass1_1 = MyClass1()
    myClass1_2 = MyClass1()
    myClass2 = MyClass2()
    print("check id")
    print("myClass1_1s id: " + str(id(myClass1_1)))
    print("myClass1_2s id: " + str(id(myClass1_2)))
    print("myClass2s id: " + str(id(myClass2)))
