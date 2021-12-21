import re

class ShortScoreLexer:
    """A lexer for the ShortScore musical notation"""
    default_alter_regex = r'[sfqt]'
    dutch_alter_regex = r'[eihs]'

    def __init__(self, alter_lang = 'default'):
        self._token_types_dict = {
            'notes': self._is_note,
            'duration': self._is_duration,
            'rest': self._is_rest
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
        self.reader = ShortScoreReader(bar_of_music)
        for char in self.reader.read_char():
            for token_type in self._token_types_dict:
                for token in self._token_types_dict[token_type](char):
                    yield token

    def _is_note(self, char):
        if re.match(r'[a-g]', char):
            yield ("pitchstep", char)
            alter = "".join(self.reader.read_while(use_re = self.alter_regex))
            if alter:
                yield ("pitchalter", alter)
            yield ("octave", "".join(self.reader.read_while(use_in = "',")))

    def _is_duration(self, char):
        if re.match(r'[1-9]', char):
            yield ("duration", char + "".join(self.reader.read_while(use_re = r'[1-9\.]')))

    def _is_rest(self, char):
        if char == 'r':
            yield ("rest", char)


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
