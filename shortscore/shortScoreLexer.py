import re

class ShortScoreLexer:
    """A lexer for the ShortScore musical notation"""
    default_alter_regex = r'[sfqt]'
    dutch_alter_regex = r'[eihs]'

    def __init__(self, alter_lang = 'default'):
        self._token_types_dict = {
            'notes': self._is_note,
            'chord': self._is_chord,
            'rest': self._is_rest,
            'tuplet': self._is_tuplet,
            'duration': self._is_duration,
            'slur': self._is_slur,
            'tie': self._is_tie,
            'grace': self._is_grace,
            'barattr': self._is_barattr
            }
        if alter_lang == 'dutch':
            self.alter_regex = self.dutch_alter_regex
        else:
            self.alter_regex = self.default_alter_regex

    def set_alter_lang(self, alter_lang): 
        if alter_lang == 'dutch':
            self.alter_regex = self.dutch_alter_regex

    def lex(self, bar_of_music):
        """Generate tuplets of type and string from bar of music"""
        self.reader = ShortScoreReader(self.convert_from_alternative_syntax(bar_of_music))
        for char in self.reader.read_char():
            for token_type in self._token_types_dict:
                for token in self._token_types_dict[token_type](char):
                    yield token

    def convert_from_alternative_syntax(self, bar_of_music):
        def separate_expr(matches):
            notes = matches[1]
            expr = matches[2]
            return " ".join(note + expr for note in notes.split())

        # trailing tuplet ratio is supported but more difficult to parse
        bar_of_music = re.sub(r'\[([^\]]+)\]:(\d+)\\(\d+)', r'\g<2>\\\g<3>:[\g<1>]', bar_of_music)
        # Duration after chord is supported but after first note is recommended
        bar_of_music = re.sub(r'\{([a-g\',]+)([^>]+)\}(\d+)', r'{\g<1>\g<3>\g<2>}', bar_of_music)
        bar_of_music = re.sub(r'\[([^\]]+)\]:(\w+)', separate_expr, bar_of_music)
        return bar_of_music

    def _is_note(self, char):
        if re.match(r'[a-g]', char):
            yield ("pitchstep", char)
            alter = "".join(self.reader.read_while(use_re = self.alter_regex))
            if alter:
                yield ("pitchalter", alter)
            yield ("octave", "".join(self.reader.read_while(use_in = "',")))

    def _is_duration(self, char):
        if re.match(r'[1-9]', char):
            all_chars = char + "".join(self.reader.read_while(use_re = r'[1-9\.\\:]'))
            if ':' in all_chars:
                yield ("tuplet_ratio", all_chars)
            else:
                yield ("duration", all_chars)

    def _is_rest(self, char):
        if char == 'r':
            yield ("rest", char)

    def _is_chord(self, char):
        yield from self._is_start_end(char, 'chord', '{', '}')

    def _is_tuplet(self, char):
        yield from self._is_start_end(char, 'tuplet', '[', ']')

    def _is_slur(self, char):
        yield from self._is_start_end(char, 'slur', '(', ')')

    def _is_tie(self, char):
        yield from self._is_start_end(char, 'tie', '>', '<')

    def _is_grace(self, char):
        if char == 'µ':
            yield ("grace", char)

    def _is_start_end(self, char, description, start_char, end_char):
        if char == start_char:
            yield (f"{description}_start", char)
        if char == end_char:
            yield (f"{description}_end", char)

    def _is_barattr(self, char):
        if char == '«':
            yield ("barattr", "".join(self.reader.read_while(use_re=r'[^»]')))


class ShortScoreReader:
    """Helper class for reading the music"""

    def __init__(self, bar_of_music):
        self.reader = self.read(bar_of_music)
        self.prev_char = self.next_char = ''

    def read(self, bar_of_music):
        for char in bar_of_music:
            yield char

    def goto_next(self):
        self.prev_char = self.next_char
        self.next_char = next(self.reader, None)

    def read_char(self):
        while True:
            if self.prev_char:
                yield self.prev_char
            elif self.prev_char is None:
                break
            self.goto_next()

    def read_while(self, use_re = '', use_in = ''):
        while True:
            char = self.next_char
            if char is None:
                break
            if use_re and not re.match(use_re, char):
                break
            elif use_in and char not in use_in:
                break
            yield char
            self.goto_next()
