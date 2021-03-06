from fractions import Fraction

class ParseTreeObject:
    """Abstract class for the parse tree classes"""

    token = None

    def set_token(self, token):
        self.token = token

    def get_token(self):
        return self.token

    def get_mxml_value(self):
        return None

    def set_token_from_mxml(self, mxml_value):
        self.token = mxml_value


class Note(ParseTreeObject):
    """Representing a note"""


class NoteStart(Note):
    """Representing the start of the note"""


class NoteEnd(Note):
    """Representing the end of the note"""


class Pitch(ParseTreeObject):
    """Representing a pitch"""

    language = 'default'


class PitchStart(Pitch):
    """"Representing the start of the pitch"""


class PitchEnd(Pitch):
    """Representing the end of the pitch"""


class PitchStep(Pitch):
    """Representing a pitch step"""
    def get_mxml_value(self):
        return self.token.upper()

    def set_token_from_mxml(self, mxml_value):
        self.token = mxml_value.lower()


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

class BarTemporals(ParseTreeObject):
    """Keeping track of temporal stuff for the bar"""
    time_fraction = Fraction('4/4')
    durations = None

    def set_token(self, token):
        self.token = token
        self.durations.append(token)

    def calculate_mxml_divisions(self):
        ratios = [self.get_ratio(dur) for dur in self.durations]
        lowest_ratio = quarter = Fraction('1/4')
        for ratio in ratios:
            if ratio < lowest_ratio:
                lowest_ratio = ratio
        if lowest_ratio < quarter:
            return int(1 / (lowest_ratio * 4))
        else:
            return int(lowest_ratio * 4)

    def get_ratio(self, duration):
        if '.' in duration:
            duration = duration.replace('.', '')
            ratio = Fraction('1/' + duration)
            ratio += ratio / 2
        else:
            ratio = Fraction('1/' + duration)
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
    def get_mxml_value(self):
        divisions = self.calculate_mxml_divisions()
        if divisions == 1 and '.' not in self.token:
            duration = int(self.token)
            duration_num = 4 / duration
        else:
            ratio = self.get_ratio(self.token)
            duration_num = 4 * ratio * divisions
        return str(duration_num)

    def get_type(self):
        duration = int(self.token.replace('.', ''))
        if duration in self.duration_names:
            return self.duration_names[duration]

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


