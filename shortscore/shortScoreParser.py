from .parseTreeClasses import *
from .grammarDef import GrammarDef

class ShortScoreParser:
    """
    Parsing of the tokens identified by the lexer, using the defined grammar.
    """
    allowed_ahead_tokens = ['tie_end']

    def __init__(self, language = 'default'):
        self.language = language
        grammar_def = GrammarDef()
        self.syntax_list = grammar_def.get_grammar_def()
        self.lexer_notestart, self.lexer_noteend = grammar_def.get_lexer_note_endpoints()
        self.non_notes = grammar_def.get_non_notes()
        self.obj_func_gen = grammar_def.get_obj_functions
        self.endtokens = {}
        self.ahead_tokens = []

    def init_bar(self):
        BarTemporals.durations = []
        Pitch.language = self.language
        self.ahead_tokens = []

    def parse(self, shortscore_lexer_tokens):
        note_tokens = self.ahead_tokens or []
        self.init_bar()
        while True:
            next_token = next(shortscore_lexer_tokens, None)
            if next_token is None:
                last_lexer = note_tokens[-1][0]
                if note_tokens and last_lexer in self.lexer_noteend:
                    yield from self.parse_note(note_tokens)
                elif last_lexer in self.allowed_ahead_tokens:
                    self.ahead_tokens.append(note_tokens[-1])
                else:
                    raise Exception(f'Wrong syntax: incomplete note! {note_tokens}')
                break
            token_type, _ = next_token
            if token_type in self.non_notes or token_type in self.lexer_notestart:
                if note_tokens and note_tokens[-1][0] in self.lexer_noteend:
                    yield from self.parse_note(note_tokens)
                    note_tokens = []
            if token_type in self.non_notes:
                for classname in self.non_notes.get(token_type):
                    yield self.create_obj_from_lexer(next_token, classname)
                continue
            note_tokens.append(next_token)

    def parse_note(self, note_tokens):
        for grammar_obj in self.syntax_list:
            if not grammar_obj.lexernames and grammar_obj.optional == 'no':
                yield self.create_obj_from_classname(grammar_obj.classname)
                continue
            try:
                token_type, token_str = self.find_token(note_tokens, grammar_obj.lexernames)
                if grammar_obj.optional == 'derived' or grammar_obj.optional == 'shadowed':
                    setattr(self, grammar_obj.classname.lower(), (token_type, token_str))
                    if grammar_obj.endtoken:
                        self.endtokens.setdefault(grammar_obj.endtoken, set()).add(grammar_obj.classname.lower())
                if grammar_obj.optional == 'shadowed':
                    continue
            except TypeError:
                if grammar_obj.optional == 'yes':
                    continue
                elif grammar_obj.optional == 'derived' or grammar_obj.optional == 'shadowed':
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
        self.check_endtokens(note_tokens)

    def check_endtokens(self, note_tokens):
        for endtoken, attr_set in list(self.endtokens.items()):
            if self.find_token(note_tokens, [endtoken]):
                for endtoken_attr in attr_set:
                    if hasattr(self, endtoken_attr):
                        delattr(self, endtoken_attr)
                del(self.endtokens[endtoken])

    def find_token(self, note_tokens, lexernames):
        def search(reqtoken, note_tokens):
            for name, token in note_tokens:
                if reqtoken == name:
                    return name, token

        for reqtoken in lexernames:
            if '+' in reqtoken:
                name_one, name_two = reqtoken.split('+')
                try:
                    name_one, token_one = search(name_one, note_tokens)
                    name_two, token_two = search(name_two, note_tokens)
                    return name_one, token_one + token_two
                except TypeError:
                    pass
            else:
                find_token = search(reqtoken, note_tokens)
                if find_token:
                    return find_token

    def create_obj_from_classname(self, classname):
        instance = globals().get(classname)
        return instance()

    def create_obj_from_lexer(self, lexertoken, classname):
        token_type, token_str = lexertoken
        instance = globals().get(classname)
        obj = instance()
        if token_str:
            obj.set_token(token_str)
        return obj

    def check_obj_func(self, obj, note_tokens):
        for classname, func, attr in self.obj_func_gen():
            if isinstance(obj, globals().get(classname)):
                if hasattr(self, attr):
                    getattr(obj, func)(*getattr(self, attr))
                else:
                    attrs_in_bar = {g.classname.lower(): self.find_token(note_tokens, g.lexernames) for g in self.syntax_list if self.find_token(note_tokens, g.lexernames)}
                    if attr in attrs_in_bar:
                        getattr(obj, func)(*attrs_in_bar.get(attr))
