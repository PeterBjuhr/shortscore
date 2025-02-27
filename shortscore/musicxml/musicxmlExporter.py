import xml.etree.ElementTree as ET
from xml.dom import minidom

from shortscore.shortScoreLexer import ShortScoreLexer
from shortscore.shortScoreParser import ShortScoreParser
from shortscore.parseTreeClasses import BarAttrStart, Duration, TimeModificationStart, Tuplet

from .cleftypes import cleftypes
from .general_midi import main
from .instrument_sounds import get_dict

class MusicXMLExporter():

    naming = {
            'pitchstep': 'step',
            'pitchalter': 'alter',
            'unpitchedstep': 'display-step',
            'unpitchedoctave': 'display-octave',
            'unpitchedinstrument': 'instrument',
            'rest': 'rest',
            'timemodification': 'time-modification',
            'notation': 'notations',
            'articulation': 'articulations',
            'ornament': 'ornaments',
            'barattr': 'attributes',
            'staffbackup': 'backup'
        }

    replaces = ['Start', 'End']

    attributes = {
            'UnpitchedInstrument': ['id'],
            'Tuplet': ['type'],
            'Slur': ['type'],
            'Tie': ['type'],
            'Tied': ['type'],
            'Grace': ['slash'],
            'Glissando': ['line_type', 'type'],
            'NoteStart': ['print_object'],
            'Notehead': ['filled']
        }

    def __init__(self, language='default'):
        self.ssc_lexer = ShortScoreLexer(language)
        self.ssc_parser = ShortScoreParser(language)
        self.root = ET.Element("score-partwise")
        self.root.set('version', "4.0")
        self.tree = ET.ElementTree(self.root)
        self.partlist = ET.SubElement(self.root, 'part-list')
        self.num = 1
        self.divisions = None

    def set_partdef(self, partdef, percdef):
        def remove_prefix(name):
            for i, char in enumerate(name):
                if char.isupper():
                    return name[i:]

        def convert_camel_case(name):
            return ''.join(' ' + n if n.isupper() else n for n in name).strip()

        def remove_roman_numerals(name):
            return " ".join(n for n in name.split() if n not in ['I', 'V', 'X'])

        replaces = ['Lh', 'Rh', 'Solo']
        self.partnames = {k: convert_camel_case(self.do_replaces(remove_prefix(v), replaces)) for k, v in partdef.items()}
        self.instrument_names = {k: [(k, remove_roman_numerals(v), None, False)] for k, v in self.partnames.items()}
        for key, additional_instruments in percdef.items():
           self.instrument_names[key] = [t + (True,) for t in additional_instruments]
        self.midi_instruments = main()
        self.instrument_sounds = get_dict()

    def setup_part(self, part):
        num = self.num
        self.current_percussion = {}
        partname, instr_names = self.partnames.get(part), self.instrument_names.get(part)
        self.part = ET.SubElement(self.root, 'part')
        self.part.set('id', 'P' + str(num))
        score_part = ET.SubElement(self.partlist, 'score-part')
        score_part.set('id', 'P' + str(num))
        part_name = ET.SubElement(score_part, 'part-name')
        part_name.text = partname
        for _, longname, _, is_percussion in instr_names:
            self.setup_score_instrument(score_part, longname, is_percussion)
        self.num = num
        for display_note, longname, _, is_percussion in instr_names:
            if is_percussion:
                self.current_percussion[display_note] = f'P{self.num}-X{self.num}'
            self.setup_midi_instrument(score_part, longname, is_percussion)
        return partname

    def setup_score_instrument(self, score_part, instr_name, is_percussion):
        num = self.num
        instrument = ET.SubElement(score_part, 'score-instrument')
        instrument_id = f'P{num}-X{num}' if is_percussion else f'P{num}-I{num}'
        instrument.set('id', instrument_id)
        instrument_name = ET.SubElement(instrument, 'instrument-name')
        instrument_name.text = instr_name
        sound_key = "-".join(instr_name.split()).lower()
        sound_name = self.instrument_sounds.get(sound_key)
        self.num += 1

    def setup_midi_instrument(self, score_part, instr_name, is_percussion):
        num = self.num
        midi_instrument = ET.SubElement(score_part, 'midi-instrument')
        midi_instrument_id = f'P{num}-X{num}' if is_percussion else f'P{num}-I{num}'
        midi_instrument.set('id', midi_instrument_id)
        midi_channel = ET.SubElement(midi_instrument, 'midi-channel')
        midi_channel.text = "10" if is_percussion else str(num)
        midi_program = ET.SubElement(midi_instrument, 'midi-program')
        midiname = instr_name
        if is_percussion:
            midi_program.text = "1"
            midi_unpitched = ET.SubElement(midi_instrument, 'midi-unpitched')
            midi_unpitched.text = str(int(self.midi_instruments.get(midiname, '35')) + 1)
        else:
            midi_program.text = self.midi_instruments.get(midiname, '1')
        self.num += 1

    def do_replaces(self, input_str, replaces=None):
        if not replaces:
            replaces = self.replaces
        for repl in replaces:
            input_str = input_str.replace(repl, '')
        return input_str

    def pre_parse_bar(self, bar):
        parse_result = {}
        lexerlist = list(self.ssc_lexer.lex(bar))
        pre_parser = self.ssc_parser.parse(iter(lexerlist), bar)
        obj = next(pre_parser)
        if isinstance(obj, BarAttrStart):
            parse_result['glob'] = next(pre_parser).lookup
            lexerlist.pop(0)
        duration = None
        while True:
            try:
                if isinstance(obj, Duration):
                    duration = obj
                obj = next(pre_parser)
            except StopIteration:
                break
        if duration:
            duration.calculate_mxml_divisions()
            parse_result['divisions'] = duration.divisions
        return iter(lexerlist), parse_result

    def export_bar(self, glob, bar, bar_number=1):
        lexer, preparsed = self.pre_parse_bar(bar)
        add_glob = preparsed.get('glob')
        if add_glob:
            if not glob:
                glob = {}
            glob = {**glob, **add_glob}
        divisions = preparsed.get('divisions')
        if not divisions:
            return self.make_multi_rest(bar_number, glob)
        self.bar_parent = ET.SubElement(self.part, 'measure')
        self.bar_parent.set('number', str(bar_number))
        self.divisions = divisions
        attr = ET.SubElement(self.bar_parent, 'attributes')
        divs = ET.SubElement(attr, 'divisions')
        divs.text = str(divisions)
        if glob:
            self.create_time_node(attr, glob.get('m'))
            self.create_tempomark(glob.get('t'), glob.get('tt'))
            self.create_clef(attr, glob.get('c'))
        self.parser_tree = self.ssc_parser.parse(lexer, bar)
        self.create_nodes_from_parser_objects(self.bar_parent)

    def create_time_node(self, attrnode, timesign):
        if timesign:
            timenode = ET.SubElement(attrnode, 'time')
            beats, beat_type = timesign.split('/')
            beatsnode = ET.SubElement(timenode, 'beats')
            beatsnode.text = str(beats)
            beat_typenode = ET.SubElement(timenode, 'beat-type')
            beat_typenode.text = str(beat_type)

    def create_clef(self, attrnode, cleftype):
        if cleftype:
            clefnode = ET.SubElement(attrnode, 'clef')
            sign, line, octave_change = cleftypes.get(cleftype)
            signnode = ET.SubElement(clefnode, 'sign')
            signnode.text = sign
            if line:
                linenode = ET.SubElement(clefnode, 'line')
                linenode.text = str(line)
            if octave_change:
                ocnode = ET.SubElement(clefnode, 'clef-octave-change')
                ocnode.text = str(octave_change)

    def add_attr_id(self, note_value):
        return self.current_percussion.get(note_value)

    def create_direction(self, placement='above'):
        direction = ET.SubElement(self.bar_parent, 'direction')
        direction.set('placement', placement)
        direction_type = ET.SubElement(direction, 'direction-type')
        return direction_type

    def create_tempomark(self, tempo, tempotext=None):
        if tempo:
            beat_unit_dot = False
            beat_unit, per_minute = tempo.split('=')
            if '.' in beat_unit:
                beat_unit_dot = True
                beat_unit = beat_unit.replace('.', '')
            beat_unit = Duration.duration_names.get(int(beat_unit)) or 'quarter'
            direction_type = self.create_direction()
            if tempotext:
                words = ET.SubElement(direction_type, 'words')
                words.text = tempotext
            metronome = ET.SubElement(direction_type, 'metronome')
            bunode = ET.SubElement(metronome, 'beat-unit')
            bunode.text = beat_unit
            if beat_unit_dot:
                ET.SubElement(metronome, 'beat-unit-dot')
            pmnode = ET.SubElement(metronome, 'per-minute')
            pmnode.text = per_minute

    def create_dynamics(self, parent, dynamic):
        if dynamic == '<':
            direction_type = self.create_direction('below')
            crescendo = ET.SubElement(direction_type, 'wedge')
            crescendo.set('type', 'crescendo')
        elif dynamic == '>':
            direction_type = self.create_direction('below')
            crescendo = ET.SubElement(direction_type, 'wedge')
            crescendo.set('type', 'diminuendo')
        elif dynamic == '!':
            direction_type = self.create_direction('below')
            crescendo = ET.SubElement(direction_type, 'wedge')
            crescendo.set('type', 'stop')
        elif dynamic:
            direction_type = self.create_direction('below')
            dynamic_node = ET.SubElement(direction_type, 'dynamics')
            ET.SubElement(dynamic_node, dynamic)

    def create_words(self, parent, text):
        if text:
            direction_type = self.create_direction()
            text_node = ET.SubElement(direction_type, 'words')
            text_node.text = text

    def create_duration(self, parent, duration):
        if duration:
            duration_node = ET.SubElement(parent, 'duration')
            duration_node.text = duration

    def create_nodes_from_parser_objects(self, parent):
        parser_object = next(self.parser_tree, None)
        if parser_object is not None:
            classname = parser_object.__class__.__name__
            element_name = self.do_replaces(classname).lower()
            if element_name in self.naming:
                element_name = self.naming.get(element_name)
            if 'End' in classname:
                self.check_add_on(parser_object, parent)
                return
            node = ET.SubElement(parent, element_name)
            if 'Start' in classname:
                self.create_nodes_from_parser_objects(node)
            value = parser_object.get_mxml_value()
            if value:
                node.text = value
            self.check_add_on(parser_object, parent)
            if classname in self.attributes:
                for attr in self.attributes[classname]:
                    attr_method = getattr(parser_object, 'attr_' + attr, None)
                    attr_value = attr_method()
                    if hasattr(self, 'add_attr_' + attr):
                        attr_value = getattr(self, 'add_attr_' + attr)(attr_value)
                    if attr_value:
                        node.set(attr.replace('_', '-'), attr_value)
            self.create_nodes_from_parser_objects(parent)

    def check_add_on(self, parser_object, parent):
        for add_on in parser_object.add_onfuncs:
            extra_method = getattr(parser_object, 'get_' + add_on, None)
            extra_value = extra_method()
            if hasattr(self, 'create_' + add_on):
                getattr(self, 'create_' + add_on)(parent, extra_value)
            elif extra_value or extra_value is None:
                extra_node = ET.SubElement(parent, add_on.replace('_', '-'))
                extra_node.text = extra_value

    def make_full_bar_rest(self, bar_number, glob, timesign):
        def calculate_duration(divisions, timesign):
            num, den = timesign.split('/')
            timesign_ratio = int(num) / int(den)
            return timesign_ratio * 4 * divisions

        divisions = self.divisions
        if not divisions:
            self.divisions = divisions = 4
        self.bar_parent = ET.SubElement(self.part, 'measure')
        self.bar_parent.set('number', str(bar_number))
        attr = ET.SubElement(self.bar_parent, 'attributes')
        divs = ET.SubElement(attr, 'divisions')
        divs.text = str(divisions)
        if glob:
            self.create_time_node(attr, glob.get('m'))
            self.create_tempomark(glob.get('t'), glob.get('tt'))
            self.create_clef(attr, glob.get('c'))
        note = ET.SubElement(self.bar_parent, 'note')
        rest = ET.SubElement(note, 'rest')
        rest.set('measure', 'yes')
        duration_num = calculate_duration(divisions, timesign)
        duration = ET.SubElement(note, 'duration')
        duration.text = str(int(duration_num))

    def make_multi_rest(self, bar_number, glob, num_bars=1):
        self.bar_parent = ET.SubElement(self.part, 'measure')
        self.bar_parent.set('number', str(bar_number))
        attr = ET.SubElement(self.bar_parent, 'attributes')
        if glob:
            self.create_time_node(attr, glob.get('m'))
            self.create_clef(attr, glob.get('c'))
        measure_style = ET.SubElement(attr, 'measure-style')
        multiple_rest = ET.SubElement(measure_style, 'multiple-rest')
        multiple_rest.text = str(num_bars)

    def debug_bar(self):
        ET.dump(self.bar_parent)

    def write_to_str(self):
        return ET.tostring(self.root)

    def write_to_file(self, filename):
        with open(filename, 'w') as file_obj:
            decl = '<?xml version="1.0" encoding="UTF-8"?>'
            doctype = '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">'
            rough_string = ET.tostring(self.root, encoding='unicode')
            reparsed = minidom.parseString(decl + doctype + rough_string)
            file_obj.write(reparsed.toprettyxml(indent="  "))
