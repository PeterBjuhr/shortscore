from parseTreeClasses import *

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
            'duration': Duration
        }

    before_classes = {
            PitchStep: PitchStart,
            PitchStart: NoteStart
        }

    after_classes = {
            Octave: PitchEnd,
            Duration: NoteEnd
        }

    implicit_classes = { #Implicit token type: token type before the implicit
            'duration': 'octave'
        }

    def __init__(self, language = 'default'):
        self.language = language

    def init_bar(self):
        BarTemporals.durations = []
        Pitch.language = self.language

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
        implicit = self.implicit_classes 
        impl_flipped = {v: k for k, v in implicit.items()}
        prev_type = waiting_token = None
        while True:
            if waiting_token:
                next_token = waiting_token
                waiting_token = None
            else:
                next_token = next(shortscore_lexer_tokens, None)
            if next_token:
                token_type, token_str = next_token
            if prev_type in impl_flipped and impl_flipped[prev_type] != token_type:
                waiting_token = next_token
                token_type = impl_flipped[prev_type]
                token_str = getattr(self, impl_flipped[prev_type], None)
                next_token = (token_type, token_str)
            else:
                if token_type in implicit:
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
