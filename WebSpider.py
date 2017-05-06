#!/usr/bin/env python3

import json

import requests
import lxml.etree

import InfoSource

def xpathClassStr(class_name):
    return "contains(concat(' ', normalize-space(@class), ' '), ' {} ')".format(class_name)

class ResponseSpider(InfoSource.InfoSource):
    def __init__(self):
        super(ResponseSpider, self).__init__()

        self.EntryPoint = ""
        self.Action = "GET"
        self.RequestData = dict()
        self.XPath = ""
        self.Name = "Spider"
        self.Headers = dict()

    def _get_response(self):
        if self.Action == "GET":
            Res = requests.get(self.EntryPoint, params=self.RequestData,
                               headers=self.Headers)
        elif self.Action == "POST":
            Res = requests.post(self.EntryPoint, data=self.RequestData,
                                headers=self.Headers)
        return Res.text

    def _get_data(self):
        Res = self._get_response()
        Parser = lxml.etree.HTMLParser()
        Html = lxml.etree.fromstring(Res, Parser)
        Result = Html.xpath(self.XPath)[0]
        return Result

    def __call__(self):
        self.Result = self._get_data()
        return self.Result

    @classmethod
    def fromDict(cls, src_dict):
        Spider = cls()
        Spider.EntryPoint = src_dict["EntryPoint"]
        if "Action" in src_dict:
            Spider.Action = src_dict["Action"]
        if "RequestData" in src_dict:
            Spider.RequestData = src_dict["RequestData"]
        Spider.XPath = src_dict["XPath"]
        Spider.Name = src_dict["Name"]
        return Spider

class JsonSpider(ResponseSpider):
    def __init__(self):
        super(JsonSpider, self).__init__()

    def _get_data(self):
        def digStruct(struct, path_list):
            if len(path_list) == 0:
                return struct
            if isinstance(struct, dict):
                return digStruct(struct[path_list[0]], path_list[1:])
            return digStruct(struct[int(path_list[0])], path_list[1:])

        Res = self._get_response()
        Data = json.loads(Res)
        XPath = self.XPath  # type: str
        if XPath.startswith('/'):
            XPath = XPath[1:]

        return digStruct(Data, XPath.split('/'))

class AppStorePrice(JsonSpider):
    def __init__(self):
        super(AppStorePrice, self).__init__()
        self.XPath = "/results/0/formattedPrice"
        self.AppID = ""

    @classmethod
    def fromDict(cls, src_dict):
        Spider = cls()
        Spider.AppID = str(src_dict["AppID"])
        Spider.Name = src_dict["Name"]
        Spider.EntryPoint = "https://itunes.apple.com/lookup?id=" + Spider.AppID
        Spider.Action = "GET"
        return Spider
