#!/usr/bin/env python3

class InfoSource():
    def __init__(self):
        self.Name = ""
        self.Result = None

    @classmethod
    def fromDict(cls, src_dict):
        raise NotImplementedError()

    def __call__(self):
        # Should return the info, and also set self.Result.
        raise NotImplementedError()
