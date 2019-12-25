import os

import xml.etree.ElementTree as ET

from shortscore.parseTreeClasses import *

class MusicXMLImporter():

    convertable_tags = {
            'notestart': NoteStart,
            'noteend': NoteEnd,
            'pitchstart': PitchStart,
            'pitchend': PitchEnd,
            'step': PitchStep,
            'alter': PitchAlter,
            'octave': Octave,
            'type': Duration
        }

    modifier_tags = {
            'dot': Duration
        }

    ignore = [
            'divisions',
            'duration',
            'accidental',
            'stem'
        ]

    def __init__(self, xml):
        if os.path.isfile(xml):
            xml_tree = ET.parse(xml)
            self.root = xml_tree.getroot()
        else:
            self.root = ET.fromstring(xml)

    def do_import(self):
        for bar in self.root.iter('measure'):
            for item in bar:
                for item in self.import_bar_items(item):
                    if item is not None:
                        yield item

    def has_children(self, node):
        return len(node)

    def convert_tag_to_parse_object(self, tag):
        if tag in self.convertable_tags:
            classname = self.convertable_tags[tag]
            return classname()

    def import_bar_items(self, parent_item):
        parent_tag = parent_item.tag + 'start'
        yield self.convert_tag_to_parse_object(parent_tag)
        for item in parent_item:
            if self.has_children(item):
                for child in self.import_bar_items(item):
                    yield child
            else:
                if item.tag in self.ignore:
                    continue
                if item.tag in self.modifier_tags:
                    if isinstance(parse_object, self.modifier_tags[item.tag]):
                        modify_method = getattr(parse_object, "modify_" + item.tag, None)
                        modify_method(item.text)
                    continue
                parse_object = self.convert_tag_to_parse_object(item.tag)
                if parse_object is not None:
                    parse_object.set_token_from_mxml(item.text)
                    yield parse_object
        parent_tag = parent_item.tag + 'end'
        yield self.convert_tag_to_parse_object(parent_tag)
