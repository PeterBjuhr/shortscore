from pathlib import Path

# Define the grammar of a single note
# classname (?=optional, !=derived) | from token | ends on token
NOTEDEF = """
    NoteStart|
    Chord¡|chord_start|chord_end
    Rest?|rest
    PitchStart?|pitchstep
    PitchStep?|pitchstep
    PitchAlter?|pitchalter
    Octave?|octave
    PitchEnd?|pitchstep
    Duration!|duration
    TimeModificationStart!|tuplet_ratio|tuplet_end
    TimeModificationEnd!|tuplet_ratio|tuplet_end
    NotationStart?|tuplet_start,tuplet_end,slur_start,slur_end
    Slur?|slur_start,slur_end
    Tuplet?|tuplet_start,tuplet_end
    NotationEnd?|tuplet_start,tuplet_end,slur_start,slur_end
    NoteEnd|
    """
# Define which tokens could start a new note
NOTESTART = """
    pitchstep
    rest
    tuplet_ratio
    chord_start
    slur_start
    """
# Define which tokens could end a note
NOTEEND = """
    octave
    duration
    tuplet_end
    rest
    chord_end
    slur_end
    """

# Define non-note elements
NON_NOTES = """
    BarAttrStart|barattr
    BarAttrEnd|barattr
    """

# Define which function to run on the newly created parser obj
# classname | function name | parser attribute
OBJ_FUNC = """
    Duration|set_timemod|TimeModificationStart
    """

class GrammarDef:
    """Reading the grammar file and keeping track of the grammar definition"""

    def __init__(self):
        self.grammar_def = self.parse_notedef()

    def parse_notedef(self):
        txtdef = [d.strip() for d in NOTEDEF.split() if d]
        for grammar_elem in txtdef:
            yield self.create_def_obj(*grammar_elem.split('|'))

    def create_def_obj(self, classname, lexername, endtoken=None):
        if classname.endswith('?'):
            optional = 'yes'
            classname = classname[:-1]
        elif classname.endswith('!'):
            optional = 'derived'
            classname = classname[:-1]
        elif classname.endswith('¡'):
            optional = 'shadowed'
            classname = classname[:-1]
        else:
            optional = 'no'
        lexernames = lexername.split(',')
        return GrammarElement(classname, optional, lexernames, endtoken)

    def get_grammar_def(self):
        return list(self.grammar_def)

    def get_lexer_note_endpoints(self):
        starting= [n.strip() for n in NOTESTART.split() if n]
        ending = [n.strip() for n in NOTEEND.split() if n]
        return starting, ending

    def get_non_notes(self):
        non_notes = (nn for nn in NON_NOTES.split() if nn)
        non_notes_dict = {}
        for nn in non_notes:
            classname, lexername = nn.split('|')
            non_notes_dict.setdefault(lexername, []).append(classname)
        return non_notes_dict

    def get_obj_functions(self):
        for obj_func in (o.strip() for o in OBJ_FUNC.split() if o):
            classname, func, attr = obj_func.split('|')
            yield classname, func, attr.lower()


class GrammarElement:
    def __init__(self, classname, optional, lexernames, endtoken):
        self.classname = classname
        self.optional = optional
        self.lexernames = list(filter(None, lexernames))
        self.endtoken = endtoken

    def __repr__(self):
        return self.classname + '|optional:' + str(self.optional) + '|' + str(self.lexernames) + '|' + str(self.endtoken)
