from fractions import Fraction
from functools import reduce
import math

class ParseTreeObject:
    """Abstract class for the parse tree classes"""
    add_onfuncs = []

    def __init__(self):
        self.token = None

    def __repr__(self):
        return str(id(self)) + ':' + self.__class__.__name__ + str(self.__dict__)

    def set_token(self, token):
        self.token = token

    def get_token(self):
        return self.token

    def get_mxml_value(self):
        return None

    def set_token_from_mxml(self, mxml_value):
        self.token = mxml_value


class BarAttrStart(ParseTreeObject):
    """Representing a bar attribute"""


class BarAttrEnd(ParseTreeObject):
    """Representing a bar attribute"""
    add_onfuncs = ['clef']

    def set_token(self, token):
        self.token = token
        self.lookup = dict(d.split(':') for d in token.split(','))

    def get_clef(self):
        return self.lookup.get('c')


class Note(ParseTreeObject):
    """Representing a note"""


class NoteStart(Note):
    """Representing the start of the note"""


class NoteEnd(Note):
    """Representing the end of the note"""


class Chord(ParseTreeObject):
    """Representing a chord note"""


class Pitch(ParseTreeObject):
    """Representing a pitch"""

    language = 'default'


class PitchStart(Pitch):
    """"Representing the start of the pitch"""


class PitchEnd(Pitch):
    """Representing the end of the pitch"""


class UnPitchedStart(Pitch):
    """"Representing the start of the unpitched note"""


class UnPitchedEnd(Pitch):
    """Representing the end of the unpitched note"""


class PitchStep(Pitch):
    """Representing a pitch step"""
    def get_mxml_value(self):
        return self.token.upper()

    def set_token_from_mxml(self, mxml_value):
        self.token = mxml_value.lower()


class UnPitchedStep(PitchStep):
    """Representing a display step for unpitched note"""


class PitchAlter(Pitch):
    """Representing a pitch step"""

    alter_dict = {'qs': 0.5, 'qf': -0.5, 's': 1, 'f': -1, 'tqs': 1.5, 'tqf': -1.5}

    def get_mxml_value_from_dutch(self):
        count_dict = {'is': 2, 'es': -2, 'ih': 1, 'eh': -1}
        alter = self.token
        alter_steps = 0
        alter_list = [alter[i:i + 2] for i in range(0, len(alter), 2)]
        for alt in alter_list:
            alter_steps += count_dict[alt]
        try:
            return int(str(alter_steps / Fraction(2)))
        except ValueError:
            return float(alter_steps / Fraction(2))

    def get_mxml_value_from_default(self):
        alter = self.token
        if alter in self.alter_dict:
            return str(self.alter_dict[alter])
        else:
            alter_sum = 0
            for char in alter:
                if char in self.alter_dict:
                    alter_sum += self.alter_dict[char]
            return str(alter_sum)

    def get_mxml_value(self):
        if self.language == 'dutch':
            mxml_value = self.get_mxml_value_from_dutch()
        else:
            mxml_value = self.get_mxml_value_from_default()
        return mxml_value

    def set_token_from_mxml(self, mxml_value):
        if self.language == 'dutch':
            self.set_dutch_token_from_mxml(mxml_value)
        else:
            self.set_default_token_from_mxml(mxml_value)

    def set_default_token_from_mxml(self, mxml_value):
        alter_dict_flipped = {num: val for val, num in self.alter_dict.items()}
        try:
            mxml_value = int(mxml_value)
        except ValueError:
            mxml_value = float(mxml_value)
        if mxml_value in alter_dict_flipped:
            self.token = alter_dict_flipped[mxml_value]
        else:
            try_half = mxml_value / 2
            if try_half in alter_dict_flipped:
                self.token = "".join([try_half] * 2)

    def set_dutch_token_from_mxml(self, mxml_value):
        alter_num = Fraction(mxml_value)
        alter_num = int(alter_num / Fraction('0.5'))
        if alter_num < 0:
            basic_symb = 'e'
        else:
            basic_symb = 'i'
        abs_alter_num = abs(alter_num)
        alter_list = []
        for n in range(abs_alter_num):
            n += 1
            if not n % 2:
                alter_list.append(basic_symb + 's')
        if n % 2:
            alter_list.append(basic_symb + 'h')
        self.token = "".join(alter_list)


class Octave(ParseTreeObject):
    """Representing an octave"""
    def get_mxml_value(self):
        """
        Octaves represented by the numbers,
        where 4 indicates the octave started by middle C
        """
        plus = minus = 0
        if self.token:
            plus = self.token.count("'")
            minus = self.token.count(",")
        octave_as_number = 3 + plus - minus
        return str(octave_as_number)

    def set_token_from_mxml(self, mxml_value):
        small_c_diff = int(mxml_value) - 3
        if small_c_diff > 0:
            self.token = "".join(["'"] * small_c_diff)
        elif small_c_diff < 0:
            self.token = "".join([","] * abs(small_c_diff))
        else: # == 0
            self.token = ''


class UnpitchedOctave(Octave):
    """Representing a display octave for an unpitched note"""


class UnpitchedInstrument(ParseTreeObject):
    """Representing the instrument of an unpitched note"""

    def attr_id(self):
        return self.token


class Rest(ParseTreeObject):
    """Representing a rest"""
    pass

class BarTemporals(ParseTreeObject):
    """Keeping track of temporal stuff for the bar"""
    durations = None
    divisions = 0

    def __init__(self):
        self.timemod = None

    def set_token(self, token):
        self.token = token
        self.durations.append(self)

    def set_timemod(self, token_type, ratio_token):
        self.timemod = Fraction(ratio_token[:-1].replace('\\', '/'))

    def calculate_mxml_divisions(self):
        ratios = set(dur.get_ratio() for dur in self.durations)
        denominators = set(r.denominator for r in ratios)
        if len(denominators) > 2:
            lcm = reduce(lambda x, y: math.gcd(x, y), denominators)
        elif len(denominators) > 1:
            lcm = math.prod(denominators) / math.gcd(*denominators)
        else:
            lcm = denominators.pop()
        BarTemporals.divisions = int(lcm)

    def get_ratio(self):
        duration = self.token
        if '.' in duration:
            duration = duration.replace('.', '')
            ratio = Fraction('1/' + duration)
            ratio += ratio / 2
        else:
            ratio = Fraction('1/' + duration)
        if self.timemod:
            ratio *= 1 / self.timemod
        return ratio


class Duration(BarTemporals):
    """Representing a duration"""
    duration_names = {
            1: 'whole',
            2: 'half',
            4: 'quarter',
            8: 'eighth',
            16: '16th',
            32: '32nd'
        }
    add_onfuncs = ['dot']

    def get_mxml_value(self):
        if not self.divisions:
            self.calculate_mxml_divisions()
        divisions = self.divisions
        ratio = self.get_ratio()
        duration_num = 4 * ratio * divisions
        return str(int(duration_num))

    def get_dot(self):
        dot = False
        if '.' in self.token:
            dot = None
        return dot

    def set_token_from_mxml(self, mxml_value):
        for duration in self.duration_names:
            if self.duration_names[duration] == mxml_value:
                self.token = str(duration)
                break

    def modify_dot(self, text):
        self.token += '.'


class Type(ParseTreeObject):
    """Representing a duration type"""

    def get_mxml_value(self):
        duration = int(self.token.replace('.', ''))
        if duration in Duration.duration_names:
            return Duration.duration_names[duration]


class TimeModificationStart(ParseTreeObject):
    """Representing a time modification"""


class TimeModificationEnd(ParseTreeObject):
    """Representing a time modification"""

    add_onfuncs = ['actual_notes', 'normal_notes']

    def get_actual_notes(self):
        ratio = Fraction(self.token[:-1].replace('\\', '/'))
        return str(ratio.numerator)

    def get_normal_notes(self):
        ratio = Fraction(self.token[:-1].replace('\\', '/'))
        return str(ratio.denominator)


class NotationStart(ParseTreeObject):
    """Representing a notation start"""


class NotationEnd(ParseTreeObject):
    """Representing a notation end"""


class Tuplet(ParseTreeObject):
    """Representing a tuplet"""

    def attr_type(self):
        return 'start' if self.token == '[' else 'stop'


class Slur(ParseTreeObject):
    """Representing a slur"""

    def attr_type(self):
        return 'start' if self.token == '(' else 'stop'


class Tie(ParseTreeObject):
    """Representing a tie"""

    def attr_type(self):
        return 'start' if self.token == '>' else 'stop'


class Tied(ParseTreeObject):
    """Representing a tie"""

    def attr_type(self):
        return 'start' if self.token == '>' else 'stop'


class Grace(ParseTreeObject):
    """Representing a grace note"""

    def attr_slash(self):
        return 'yes'


class Glissando(ParseTreeObject):
    """Representing a glissando"""

    def attr_line_type(self):
        return 'wavy'

    def attr_type(self):
        return 'start' if self.token == '~' else 'stop'


class ArticulationStart(ParseTreeObject):
    """Representing an articulation"""


class ArticulationEnd(ParseTreeObject):
    """Representing an articulation"""

    artic_dict = {
        '·': 'staccato',
        '>': 'accent',
        '-': 'tenuto',
        'u': 'unstress'
    }

    def set_token(self, token):
        self.token = token
        artic_name = self.artic_dict.get(token[1])
        if artic_name:
            setattr(self, 'get_' + artic_name, lambda: None)
            self.add_onfuncs = []
            self.add_onfuncs.append(artic_name)
