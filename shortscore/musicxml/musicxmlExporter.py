import xml.etree.ElementTree as ET

from shortscore.shortScoreLexer import ShortScoreLexer
from shortscore.shortScoreParser import ShortScoreParser
from shortscore.parseTreeClasses import Duration, TimeModificationStart, Tuplet

class MusicXMLExporter():

    naming = {
            'pitchstep': 'step',
            'pitchalter': 'alter',
            'rest': 'rest',
            'timemodification': 'time-modification',
            'notation': 'notations'
        }

    replaces = ['Start', 'End']

    attributes = {
            'Tuplet': ['type']
        }

    add_ons = {
            'Duration': ['type', 'dot'],
            'TimeModificationEnd': ['actual_notes', 'normal_notes']
        }

    def __init__(self, language='default'):
        self.ssc_lexer = ShortScoreLexer(language)
        self.ssc_parser = ShortScoreParser(language)
        self.root = ET.Element("score-partwise")
        self.tree = ET.ElementTree(self.root)
        self.partlist = ET.SubElement(self.root, 'part-list')

    def setup_part(self, part, num):
        self.part = ET.SubElement(self.root, 'part')
        self.part.set('id', 'P' + str(num))
        score_part = ET.SubElement(self.partlist, 'score-part')
        score_part.set('id', 'P' + str(num))
        part_name = ET.SubElement(score_part, 'part-name')
        part_name.text = part

    def do_replaces(self, input_str):
        for repl in self.replaces:
            input_str = input_str.replace(repl, '')
        return input_str

    def calc_divisions(self, bar):
        duration = None
        for obj in self.ssc_parser.parse(self.ssc_lexer.lex(bar)):
            if isinstance(obj, Duration):
                duration = obj
        duration.calculate_mxml_divisions()
        return duration.divisions

    def export_bar(self, glob, bar, bar_number=1):
        self.bar_parent = ET.SubElement(self.part, 'measure')
        self.bar_parent.set('number', str(bar_number))
        attr = ET.SubElement(self.bar_parent, 'attributes')
        divs = ET.SubElement(attr, 'divisions')
        divisions = self.divisions = self.calc_divisions(bar)
        divs.text = str(divisions)
        if glob:
            self.create_time_node(attr, glob.get('m'))
        self.parser_tree = self.ssc_parser.parse(self.ssc_lexer.lex(bar))
        self.create_nodes_from_parser_objects(self.bar_parent)

    def create_time_node(self, parent, timesign):
        timenode = ET.SubElement(parent, 'time')
        beats, beat_type = timesign.split('/')
        beatsnode = ET.SubElement(timenode, 'beats')
        beatsnode.text = str(beats)
        beat_typenode = ET.SubElement(timenode, 'beat-type')
        beat_typenode.text = str(beat_type)

    def create_nodes_from_parser_objects(self, parent):
        parser_object = next(self.parser_tree, None)
        if parser_object is not None:
            classname = parser_object.__class__.__name__
            element_name = self.do_replaces(classname).lower()
            if element_name in self.naming:
                element_name = self.naming.get(element_name)
            if 'End' in classname:
                self.check_add_on(parser_object, classname, parent)
                return
            node = ET.SubElement(parent, element_name)
            if 'Start' in classname:
                self.create_nodes_from_parser_objects(node)
            value = parser_object.get_mxml_value()
            if value:
                node.text = value
            self.check_add_on(parser_object, classname, parent)
            if classname in self.attributes:
                for attr in self.attributes[classname]:
                    attr_method = getattr(parser_object, 'attr_' + attr, None)
                    node.set(attr, attr_method())
            self.create_nodes_from_parser_objects(parent)

    def check_add_on(self, parser_object, classname, parent):
        if classname in self.add_ons:
            for add_on in self.add_ons[classname]:
                extra_method = getattr(parser_object, 'get_' + add_on, None)
                extra_value = extra_method()
                if extra_value or extra_value is None:
                    extra_node = ET.SubElement(parent, add_on.replace('_', '-'))
                    extra_node.text = extra_value

    def make_multi_rest(self, bar_number):
        self.bar_parent = ET.SubElement(self.part, 'measure')
        self.bar_parent.set('number', str(bar_number))
        attr = ET.SubElement(self.bar_parent, 'attributes')
        measure_style = ET.SubElement(attr, 'measure-style')
        multiple_rest = ET.SubElement(measure_style, 'multiple-rest')
        multiple_rest.text = '1'

    def debug_bar(self):
        ET.dump(self.bar_parent)

    def write_to_str(self):
        return ET.tostring(self.root)

    def write_to_file(self, filename):
        with open(filename, 'w') as file_obj:
            file_obj.write('<?xml version="1.0" encoding="UTF-8"?>')
            file_obj.write('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">')
            self.tree.write(file_obj, encoding='unicode')
