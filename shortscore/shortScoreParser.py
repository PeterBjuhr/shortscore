from .parseTreeClasses import *
from .grammarDef import GrammarDef

class ShortScoreParser:
    """
    Parsing of the tokens identified by the lexer, using the defined grammar.
    """
    def __init__(self, language = 'default'):
        self.language = language
        grammar_def = GrammarDef()
        self.syntax_list = grammar_def.get_grammar_def()
        self.lexer_notestart, self.lexer_noteend = grammar_def.get_lexer_note_endpoints()
        self.obj_func_gen = grammar_def.get_obj_functions
        self.endtokens = {}

    def init_bar(self):
        BarTemporals.durations = []
        Pitch.language = self.language

    def parse(self, shortscore_lexer_tokens):
        self.init_bar()
        note_tokens = []
        while True:
            next_token = next(shortscore_lexer_tokens, None)
            if next_token is None:
                if note_tokens and note_tokens[-1][0] in self.lexer_noteend:
                    yield from self.parse_note(note_tokens)
                else:
                    raise Exception('Wrong syntax: incomplete note!')
                break
            token_type, _ = next_token
            if token_type in self.lexer_notestart:
                if note_tokens and note_tokens[-1][0] in self.lexer_noteend:
                    yield from self.parse_note(note_tokens)
                    note_tokens = []
            note_tokens.append(next_token)

    def parse_note(self, note_tokens):
        for grammar_obj in self.syntax_list:
            if not grammar_obj.lexernames and grammar_obj.optional == 'no':
                yield self.create_obj_from_classname(grammar_obj.classname)
                continue
            try:
                token_type, token_str = self.find_token(note_tokens, grammar_obj.lexernames)
                if grammar_obj.optional == 'derived':
                    setattr(self, grammar_obj.classname.lower(), (token_type, token_str))
                    if grammar_obj.endtoken:
                        self.endtokens.setdefault(grammar_obj.endtoken, []).append(grammar_obj.classname.lower())
                for endtoken_attr in self.endtokens.get(token_type, []):
                    if hasattr(self, endtoken_attr):
                        delattr(self, endtoken_attr)
            except TypeError:
                if grammar_obj.optional == 'yes':
                    continue
                elif grammar_obj.optional == 'derived':
                    if hasattr(self, grammar_obj.classname.lower()):
                        token_type, token_str = getattr(self, grammar_obj.classname.lower())
                    else:
                        continue
                else:
                    required = str(grammar_obj.lexernames)
                    raise Exception(f"Required token {required} not found!")
            obj = self.create_obj_from_classname(grammar_obj.classname)
            if token_str:
                obj.set_token(token_str)
            self.check_obj_func(obj, note_tokens)
            yield obj

    def find_token(self, note_tokens, lexernames):
        for reqtoken in lexernames:
            for name, token in note_tokens:
                if reqtoken == name:
                    return name, token

    def create_obj_from_classname(self, classname):
        instance = globals().get(classname)
        return instance()

    def check_obj_func(self, obj, note_tokens):
        for classname, func, attr in self.obj_func_gen():
            if isinstance(obj, globals().get(classname)):
                if hasattr(self, attr):
                    getattr(obj, func)(*getattr(self, attr))
                else:
                    attrs_in_bar = {g.classname.lower(): self.find_token(note_tokens, g.lexernames) for g in self.syntax_list if self.find_token(note_tokens, g.lexernames)}
                    if attr in attrs_in_bar:
                        getattr(obj, func)(*attrs_in_bar.get(attr))
