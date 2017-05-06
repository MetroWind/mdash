#!/usr/bin/env python3

import sys, os
import urwid
import yaml

import InfoSource
import InfoSourceManager

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

class TreeNode(object):
    i = 0
    def __init__(self, data=None):
        self.Data = data
        self.Children = []
        self.Parent = None

    def addChild(self, node):
        self.Children.append(node)
        node.Parent = self
        return self

    def isRoot(self):
        return self.Parent is None

    def isLeaf(self):
        return len(self.Children) == 0

    def _uniqName(self):
        return "Node" + str(id(self))

    def _dotLabel(self):
        return self.Data

    def _toDot(self):
        Lines = []
        if self.Children:
            for Child in self.Children:
                Lines.append("{} -> {};".format(self._uniqName(), Child._uniqName()))
        Lines.append('{}[label="{}"];'.format(self._uniqName(), self._dotLabel()))
        return Lines

    def _toDotAll(self):
        Lines = self._toDot()
        for Child in self.Children:
            Lines += Child._toDotAll()
        return Lines

    def toDot(self):
        Lines = ["digraph G {",] + self._toDotAll() + ["}",]
        return '\n'.join(Lines)

    def findRoot(self):
        if self.isRoot():
            return self
        else:
            return self.Parent.findRoot()

    def leaves(self):
        if self.isLeaf():
            yield self
        else:
            for Child in self.Children:
                for Leaf in Child.leaves():
                    yield Leaf

class WidgetNode(TreeNode):
    def __init__(self):
        super(WidgetNode, self).__init__()
        self.WidgetType = None  # Either "columns", "rows", or "text".
        self._Widget = None
        self.Data = dict()

    def _dotLabel(self):
        if self.WidgetType == "text":
            return self.Data["text"]
        else:
            return self.WidgetType

    def build(self):
        for Child in self.Children:
            Child.build()

        if self.WidgetType == "columns":
            self._Widget = urwid.Columns([])
            self._Widget.contents = tuple((n._Widget, self._Widget.options())
                                         for n in self.Children)
        elif self.WidgetType == "rows":
            self._Widget = urwid.Pile([])
            self._Widget.contents = tuple((n._Widget, self._Widget.options())
                                         for n in self.Children)

        elif self.WidgetType == "text":
            Text = urwid.Text(self.Data["text"])
            if self.Parent.WidgetType == "list":
                # Text in a list does not have line box.
                self._Widget = Text
                if "title" in self.Data:
                    Text.set_text("{}: {}".format(
                        self.Data["title"], self.Data["text"]))
            else:
                Filler = urwid.Filler(Text, "middle")
                if "title" in self.Data:
                    self._Widget = urwid.LineBox(Filler, title=self.Data["title"])
                else:
                    self._Widget = urwid.LineBox(Filler)

        elif self.WidgetType == "list":
            Content = urwid.Pile([son._Widget for son in self.Children])
            Filler = urwid.Filler(Content, "middle")
            if isinstance(self.Data, dict) and "title" in self.Data:
                self._Widget = urwid.LineBox(Filler, title=self.Data["title"])
            else:
                self._Widget = urwid.LineBox(Filler)

        elif self.WidgetType == "big_text":
            Content = urwid.Text(self.Data["text"], wrap="clip", align="center")
            Filler = urwid.Filler(Content, "middle")
            self._Widget = Filler

    @classmethod
    def _fromKeyValue(cls, key, widget_dict_list):
        Node = cls()
        Node.WidgetType = key

        WidgetContent = widget_dict_list

        if key in ("columns", "rows", "list"):
            # In the YAML, a widget’s sub-widgets can be written as a list of
            # single-key dicts directly under the current widget’s node, or can
            # be included in a dictionary with key “Widgets” under the current
            # widget’s node.  The latter case is useful for the list widget,
            # whose sub-widgets are a bunch of texts, each with its own name.
            # This way the list widget can have its own name and be displayed as
            # the title of the line box.
            if isinstance(widget_dict_list, dict):
                WidgetContent = widget_dict_list["Widgets"]
                if "Name" in widget_dict_list:
                    Node.Data["title"] = widget_dict_list["Name"]

            for SubWidget in WidgetContent:
                SubKey = tuple(SubWidget.keys())[0]
                Node.addChild(cls._fromKeyValue(SubKey, SubWidget[SubKey]))
        elif key == "text":
            if isinstance(WidgetContent, dict):
                Node.Data = InfoSourceManager.buildInfoSource(
                    WidgetContent["InfoSource"])
            else:
                # Assume the content of widget is just a static text.
                Node.Data = {"text": WidgetContent}
        elif key == "big_text":
            # WidgetContent should be a dict.
            Node.Data = InfoSourceManager.buildInfoSource(dict(BigText=WidgetContent))

        return Node

    @classmethod
    def fromYaml(cls, yaml_file):
        Struct = yaml.load(yaml_file)["Widgets"][0]
        RootKey = list(Struct.keys())[0]
        return cls._fromKeyValue(RootKey, Struct[RootKey])

def executeInfoSources(widget_tree):
    for Leaf in widget_tree.leaves():
        if Leaf.WidgetType == "text" and isinstance(Leaf.Data, InfoSource.InfoSource):
            # Right now Leaf.Data is a InfoSource object
            Leaf.Data = {"text": Leaf.Data(),
                         "title": Leaf.Data.Name}
        elif Leaf.WidgetType == "big_text":
            Leaf.Data = {"text": Leaf.Data()}

if __name__ == "__main__":
    with open("widgets.yaml", 'r') as File:
        Root = WidgetNode.fromYaml(File) # type: WidgetNode
    executeInfoSources(Root)
    Root.build()

    with open("/tmp/test.dot", 'w') as File:
        File.write(Root.toDot())

    Loop = urwid.MainLoop(Root._Widget, unhandled_input=show_or_exit)
    Loop.run()
