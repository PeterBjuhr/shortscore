import re

from .parseTreeClasses import ArticulationEnd, TechnicalEnd, OrnamentEnd

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
            'gliss': self._is_gliss,
            'fermata': self._is_fermata,
            'harmonic': self._is_harmonics,
            'articulation': self._is_articulation,
            'ornament': self._is_ornament,
            'technical': self._is_technical,
            'backup': self._is_backup,
            'staffbackup': self._is_staff_backup,
            'barattr': self._is_barattr
            }
        self.note_cache = NoteCache()
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
        self.note_cache.clean_cache()

    def convert_from_alternative_syntax(self, bar_of_music):
        def separate_expr(matches):
            notes = matches[1]
            expr = matches[2]
            return " ".join(note + expr for note in notes.split())

        # trailing tuplet ratio is supported but more difficult to parse
        bar_of_music = re.sub(r'\[([^\]]+)\]:(\d+)\\(\d+)', r'\g<2>\\\g<3>:[\g<1>]', bar_of_music)
        # Duration after chord is supported but after first note is recommended
        bar_of_music = re.sub(r'\{([a-gs\',]+)([^\}]+)\}(\d+\.*)', r'{\g<1>\g<3>\g<2>}', bar_of_music)
        bar_of_music = re.sub(r'\[([^\]]+)\]:(\w+)', separate_expr, bar_of_music)
        return bar_of_music

    def _is_note(self, char):
        note = char
        if char == 'x':
            pitch = "".join(self.reader.read_while(use_re=r'[a-g]'))
            octave = "".join(self.reader.read_while(use_in = "',"))
            note = pitch + octave
            yield ("unpitched", pitch)
            yield ("unpitched_oct", octave)
        elif re.match(r'[a-g]', char):
            alter = "".join(self.reader.read_while(use_re = self.alter_regex))
            octave = "".join(self.reader.read_while(use_in = "',"))
            note = char + alter + octave
            func = self.note_cache.get_func(note)
            if func:
                yield from func()
            yield ("pitchstep", char)
            if alter:
                yield ("pitchalter", alter)
            yield ("octave", octave)
        self.note_cache.add_note(note)

    def _is_duration(self, char):
        if re.match(r'[1-9]', char):
            all_chars = char + "".join(self.reader.read_while(use_re = r'[0-9\.\\:]'))
            if '\\' in all_chars and ':' in all_chars:
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
        yield from self._is_start_end(char, 'tie', '>', '&')

    def _is_grace(self, char):
        if char == 'µ':
            yield ("grace", char)

    def _is_gliss(self, char):
        yield from self._is_start_end(char, 'gliss', '~', '^')

    def _is_fermata(self, char):
        if char == '𝄐':
            yield ("fermata", char)

    def _is_harmonics(self, char):
        if char == '♢':
            yield ('harmonic', char + "".join(self.reader.read_while(use_in='anbts')))

    def _is_articulation(self, char):
        if char == '-':
            yield ("artic", char + "".join(self.reader.read_while(use_in=ArticulationEnd.artic_dict)))

    def _is_ornament(self, char):
        if char == '_':
            yield ("ornament", char + "".join(self.reader.read_while(use_in=OrnamentEnd.ornament_dict)))

    def _is_technical(self, char):
        if char == '×':
            yield ("tech", char + "".join(self.reader.read_while(use_in=TechnicalEnd.tech_dict)))

    def _is_backup(self, char):
        if char == '<':
            yield ("backup", char + "".join(self.reader.read_while(use_in='<')))

    def _is_staff_backup(self, char):
        if char == '↓':
            yield ("staffbackup", char + "".join(self.reader.read_while(use_in='<')))

    def _is_start_end(self, char, description, start_char, end_char):
        enabled_automatic_end = ['>']
        if char == start_char:
            yield (f"{description}_start", char)
            if char in enabled_automatic_end:
                self.note_cache.add_func(lambda: self._is_start_end(end_char, description, start_char, end_char))
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


class NoteCache:
    """Cache notes to be able to add stop char automatically"""

    def __init__(self):
        self._cached_notes = []

    def clean_cache(self):
        self._cached_notes = [n for n in self._cached_notes if n.get('func')]

    def add_note(self, note):
        self._cached_notes.append({'char': note})

    def add_func(self, func):
        self._cached_notes[-1]['func'] = func

    def get_func(self, note):
        for cached_item in self._cached_notes:
            if note == cached_item['char']:
                func = cached_item.get('func')
                if func:
                    cached_item['func'] = None
                    return func
