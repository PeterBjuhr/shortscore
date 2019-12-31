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

    def import_partdef(self):
        def get_abbr(text):
            abbr = []
            for word in text.split():
                for word_part in word.split('-'):
                    abbr.append(word_part[:1])
            if len(abbr) > 1:
                return "".join(abbr).lower()
            else:
                return text[:3].lower()

        for partlist in self.root.iter('part-list'):
            for score_part in partlist:
                part_id = score_part.get('id')
                part_name = part_abbr = ''
                for item in score_part:
                    if item.tag == 'part-name':
                        part_name = item.text
                    elif item.tag == 'part-abbreviation':
                        part_abbr = item.text
                if not part_abbr:
                    part_abbr = get_abbr(part_name)
                else:
                    part_abbr = part_abbr.replace('.', '').lower()
                yield part_id, part_name, part_abbr

    def do_import(self):
        import_dict = {}
        import_dict['partdef'] = self.import_partdef()
        import_dict['parts'] = {}
        for part in self.root.iter('part'):
            part_id = part.get('id')
            import_dict['parts'][part_id] = []
            for bar in part.iter('measure'):
                bar_nr = bar.get('number')
                bar_gen = (item for bar_item in bar for item in self.import_bar_items(bar_item))
                import_dict['parts'][part_id].append((bar_nr, bar_gen))
        return import_dict

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
