from .parseTreeClasses import *

class ShortScoreParser:
    """
    Parsing of the tokens identified by the lexer.
    Below is a quasi grammar structure in form of
    dicts with the relation between different elements.
    """
    token_type_to_class_relations = {
            'pitchstep': PitchStep,
            'pitchalter': PitchAlter,
            'octave': Octave,
            'duration': Duration,
            'rest': Rest
        }

    before_classes = {
            PitchStep: PitchStart,
            PitchStart: NoteStart,
            Rest: NoteStart
        }

    after_classes = {
            Octave: PitchEnd,
            Duration: NoteEnd
        }

    implicit_classes = [ # token type before the implicit, Implicit token type
            ('octave', 'duration'),
            ('rest', 'duration')
        ]

    def __init__(self, language = 'default'):
        self.language = language

    def init_bar(self):
        BarTemporals.durations = []
        Pitch.language = self.language

    def search_implicit(self, lex_type, flip=False):
        if flip:
            return [(itype, ltype) for ltype, itype in self.implicit_classes if itype == lex_type]
        return ((ltype, itype) for ltype, itype in self.implicit_classes if ltype == lex_type)

    def generate_all_tokens(self, item_class, token_str = None):
        if item_class in self.before_classes:
            for token_object in self.generate_all_tokens(self.before_classes[item_class]):
                yield token_object
        token_object = item_class()
        if token_str:
            token_object.set_token(token_str)
        yield token_object
        if item_class in self.after_classes:
            for token_object in self.generate_all_tokens(self.after_classes[item_class]):
                yield token_object

    def parse(self, shortscore_lexer_tokens):
        self.init_bar()
        prev_type = waiting_token = None
        while True:
            if waiting_token:
                next_token = waiting_token
                waiting_token = None
            else:
                next_token = next(shortscore_lexer_tokens, None)
            if next_token:
                token_type, token_str = next_token
            for ltype, itype in self.search_implicit(prev_type):
                if itype == token_type:
                    continue
                waiting_token = next_token
                token_type = itype
                token_str = getattr(self, itype, None)
                next_token = (token_type, token_str)
            if self.search_implicit(token_type, flip=True):
                setattr(self, token_type, token_str)
            prev_type = token_type
            if next_token is None:
                break
            if token_type in self.token_type_to_class_relations:
                item_class = self.token_type_to_class_relations[token_type]
                for token_object in self.generate_all_tokens(item_class, token_str):
                    yield token_object
            else:
                raise Exception("Unexpected token: " + ": ".join((token_type, token_str)))
