from fractions import Fraction
import re

from .lilypondFuncs import *

class LilypondImporter():
    """
    Simple import from ly file.
    """
    def __init__(self, lyfile):
        self.unit = '1'
        self.lyscheme = []
        self.lyfile = lyfile
        self.language = self.read_language()
        glob, parts = self.get_partnames_from_ly()
        self.parts = parts
        self.partdef = {}
        self.ssc_score = {}
        if glob:
            self.glob = glob

    def read_lyfile(self):
        with open(self.lyfile) as r:
            text = r.read()
        return text

    def read_language(self):
        text = self.read_lyfile()
        lang_search = re.search(r'\\language\s*"(\w+)"', text)
        if lang_search:
            lang = lang_search.group(1).strip()
            if lang == 'english':
                lang = 'default'
        else:
            lang = 'dutch'
        return lang

    def get_partnames_from_ly(self):
        parts = []
        text = self.read_lyfile()
        parts = re.findall(r"(\w+)\s*=\s*(?:\\\w+\s*\w+[',]*\s*)?{", text)
        glob_match = re.search(r"\\new Devnull\s*\{?\s*\\(\w+)", text)
        if glob_match:
            glob = glob_match.group(1)
            parts.remove(glob)
        else:
            glob = ''
        return glob, parts

    def parse_lyglob(self, glob=None):
        if 'glob' not in self.ssc_score:
            self.ssc_score['glob'] = []
        if glob is None:
            glob = self.get_partcontent_from_ly(self.glob)
        glob_dict = {}
        scheme_dict = self.lyscheme[-1] if self.lyscheme else {}
        for g in glob.split("\n"):
            m = re.search(r"\\time\s*([\w\W]+)\b", g)
            if m:
                glob_dict['m'] = timesign = m.group(1)
            t = re.search(r"\\tempo\s*([\w\W]+)\b", g)
            if t:
                glob_dict['t'] = t.group(1)
            rm = re.search(r"\\mark\s*([\w\W]+)\b", g)
            if rm:
                mark = rm.group(1)
                if mark == r'\default':
                    glob_dict['rm'] = 'd'
                else:
                    glob_dict['rm'] = mark
            if 's' in g:
                for spacer_rest in g.split():
                    spacer_rest = spacer_rest.replace('s', '')
                    spacer_list = spacer_rest.split('*')
                    chains = len(spacer_list)
                    if chains == 1:
                        unit = spacer_list[0]
                        mult = 1
                    else:
                        unit, mult = tuple(spacer_list[:2])
                        if '.' not in unit:
                            if Fraction(timesign) == Fraction(int(mult), int(unit)):
                                unit = unit + '*' + mult
                                mult = 1
                        mult = int(mult)
                        if chains > 2:
                            for m in spacer_list[2:]:
                                mult *= int(m)
                    scheme_mult = mult
                    if glob_dict:
                        glob_dict['u'] = unit
                        self.ssc_score['glob'].append(glob_dict)
                        scheme_dict.update(glob_dict)
                        glob_dict = {}
                        mult -= 1
                    self.ssc_score['glob'] += [''] * mult
                    self.lyscheme += [scheme_dict] * scheme_mult

    def get_partcontent_from_ly(self, partname):
        text = self.read_lyfile()
        pos = text.find(partname + ' =')
        if pos > 0:
            text = text[pos:]
            start, end = get_bracket_positions(text)
            return text[start + 1:end - 1]

    def ly2shortscore(self, text):
        text = re.sub(r'\\tuplet\s*(\d+)/(\d+)\s*(\d+)\s*\{([^\}]+)}', r'[\g<4>]:\g<1>\\\g<2>:\g<3>', text)
        text = re.sub(r'\\tuplet\s*(\d+)/(\d+)\s*\{([^\}]+)}', r'[\g<3>]:\g<1>\\\g<2>', text)
        text = re.sub(r'(\]:\d+\\\d+):\s', r'\g<1> ', text)
        text = re.sub(r'\\clef\s(\w+)\b', r'«c:\g<1>»', text)
        text = re.sub(r'<([^>]+)>', r'{\g<1>}', text)
        text = re.sub(r'\\(?:grace|acciaccatura)\s*(\w+\d*\.*)', r'\g<1>µ', text)
        text = re.sub(r'\\(?:grace|acciaccatura)\s*\{([^\}]+)}', r'[\g<1>]:µ', text)
        text = re.sub(r'([>a-gis\d])\s*\\glissando[\(\s]*(\w+)\b\s*\)?', r'\g<1>:gl:\g<2>', text)
        text = re.sub(r'\\instrumentSwitch\s*"(\w+)"\s*([\w\.\',]+)\b', r'\g<2>:chi:\g<1>', text)
        text = re.sub(r'<<\s*\{\s*([^}]+)\}\s*\\\\\s*\{\s*([^}]+)\}\s*>>', r'\g<1><<\g<2>', text)
        text = re.sub(r'\\([a-z]+)\b', r':\g<1>', text)
        text = re.sub(r'([a-gis\',])\((.+)\)', r'(\g<1> \g<2>)', text)
        text = text.replace('--', '__')
        text = re.sub(r'-(.)', r'_\g<1>', text)
        text = re.sub(r'\s+', r' ', text)
        text = text.replace('~', '> <')
        return text

    def handle_multibar_rests(self, partname, bar, barnr):
        def multiply_list(multlist):
            product = 1
            for i in multlist:
                if i:
                    product *= int(i)
                else:
                    product *= 1
            return product

        words = bar.split()
        for i, w in enumerate(words):
            if 'R' in w:
                r = 1
                if barnr < len(self.lyscheme):
                    glob_dict = self.lyscheme[barnr]
                else:
                    glob_dict = self.lyscheme[-1]
                unit = glob_dict['u']
                timesign = glob_dict['m']
                w = w.replace('R', '')
                if w != unit and '*' in w:
                    if unit in w:
                        u = unit
                        w = w.replace(unit, '')
                        mults = w.replace('*', '')
                    else:
                        u, mults = w.split('*')
                    r = multiply_list(mults) or 1
                    if u != unit:
                        if '*' in unit:
                            multiplicand, multiplier = unit.split('*')
                            unit = Fraction(1, int(multiplicand)) * int(multiplier)
                        elif '.' in unit:
                            unit = unit.replace('.', '')
                            unit = Fraction(1, int(unit)) * Fraction(3, 2)
                        else:
                            unit = Fraction(1, int(unit))
                        if '.' in u:
                            u = u.replace('.', '')
                            u = Fraction(1, int(u)) * Fraction(3, 2)
                        else:
                            u = Fraction(1, int(u))
                        r = int((u / unit) * r)
                self.ssc_score[partname] += [''] * r
                del words[i]
        return " ".join(words)

    def parse_lypart(self, partname, part):
        for b in part.split("|"):
            barnr = len(self.ssc_score[partname])
            b = self.handle_multibar_rests(partname, b, barnr)
            b = self.ly2shortscore(b).strip()
            if b:
                self.ssc_score[partname].append(b)

    def read_lyvars(self):
        self.ssc_score['glob'] = []
        if self.glob:
            self.parse_lyglob()
        max = 0
        for part in self.parts:
            if part not in self.partdef:
                continue
            ssc_part = self.partdef[part]
            self.ssc_score[ssc_part] = []
            self.parse_lypart(ssc_part, self.get_partcontent_from_ly(part))
            if len(self.ssc_score[ssc_part]) > max:
                max = len(self.ssc_score[ssc_part])
        if len(self.ssc_score['glob']) < max:
            r = max - len(self.ssc_score['glob'])
            self.ssc_score['glob'] += [''] * r
        self.set_barnr_in_glob()

    def set_barnr_in_glob(self):
        for barnr, glob_dict in enumerate(self.ssc_score['glob']):
            if glob_dict:
                glob_dict['barnr'] = barnr

    def apply_globally_to_all_lyparts(self, text, barnr, after=False):
        for p in self.parts:
            if after:
                self.score[p][barnr] += text
            music = self.score[p][barnr].split()
            if music:
                music[0] += text
                self.score[p][barnr] = " ".join(music)

    def import_from_lyfile(self, ssc):
        ssc.set_language(self.language)
        self.ssc_score = ssc.score
        if not ssc.partdef:
            print("Warning! Please initiate schortscore from file")
        self.partdef = {value: key for key, value in ssc.partdef.items()}
        self.read_lyvars()
