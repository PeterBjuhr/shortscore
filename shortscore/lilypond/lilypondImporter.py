from fractions import Fraction
import re

import lilypondFuncs

class LilypondImporter():
    """
    Simple import from ly file.
    """
    def __init__(self, lyfile):
        self.unit = '1'
        self.lyscheme = []
        self.lyfile = lyfile
        glob, parts = self.get_partnames_from_ly()
        self.parts = parts
	self.ssc_score = {}
        if glob:
            self.glob = glob

    def get_partnames_from_ly(self):
        with open(self.lyfile) as r:
            text = r.read()
        parts = []
        parts = re.findall(r"(\w+)\s*=\s*(?:\\\w+\s*\w+[',]*\s*)?{", text)
        glob_match = re.search(r"\\new Devnull\s*\{?\s*\\(\w+)", text)
        if glob_match:
            glob = glob_match.group(1)
            parts.remove(glob)
        else:
            glob = ''
        return glob, parts

    def parse_lyglob(self, glob=None):
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
                        self.ssc_score[self.glob].append(glob_dict)
                        scheme_dict.update(glob_dict)
                        glob_dict = {}
                        mult -= 1
                    self.ssc_score[self.glob] += [''] * mult
                    self.lyscheme += [scheme_dict] * scheme_mult

    def get_partcontent_from_ly(self, partname):
        with open(self.lyfile) as r:
            text = r.read()
        pos = text.find(partname + ' =')
        if pos > 0:
            text = text[pos:]
            start, end = lilypondFuncs.get_bracket_positions(text)
            return text[start + 1:end - 1]

    def ly2shortscore(self, text):
        text = re.sub(r'\\tuplet\s*(\d+)/(\d+)\s*(\d+)\s*\{([^\}]+)}', r'[\g<4>]:\g<1>\\\g<2>:\g<3>', text)
        text = re.sub(r'\\tuplet\s*(\d+)/(\d+)\s*\{([^\}]+)}', r'[\g<3>]:\g<1>\\\g<2>', text)
        text = re.sub(r'(\]:\d+\\\d+):\s', r'\g<1> ', text)
        text = re.sub(r'\\(?:grace|acciaccatura)\s*([a-gis]+\d*)', r'\g<1>:g', text)
        text = re.sub(r'\\(?:grace|acciaccatura)\s*\{([^\}]+)}', r'[\g<1>]:g', text)
        text = re.sub(r'([>a-gis\d])\s*\\glissando[\(\s]*(\w+)\b\s*\)?', r'\g<1>:gl:\g<2>', text)
        text = re.sub(r'\\instrumentSwitch\s*"(\w+)"\s*([\w\.\',]+)\b', r'\g<2>:chi:\g<1>', text)
        text = re.sub(r'\\([mpf]+)\b', r':\g<1>', text)
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
                if barnr < len(self.lyscheme):
                    glob_dict = self.lyscheme[barnr]
                else:
                    glob_dict = self.lyscheme[-1]
                unit = glob_dict['u']
                timesign = glob_dict['m']
                w = w.replace('R', '')
                match = re.match(unit + r'*(\d+)', w)
                if w == unit:
                    r = 1
                elif match:
                    r = int(match.group(1))
                else:
                    n = w.split('*')
                    time_fraction = Fraction(timesign)
                    rest_num = multiply_list(n[1:])
                    rest_den = n[0]
                    if '.' in rest_den:
                        undotted = rest_den.replace('.', '')
                        rest_den = int(undotted) * 2
                        rest_num *= 3
                    else:
                        rest_den = int(rest_den)
                    rest_fraction = Fraction(rest_num, rest_den)
                    quotient = rest_fraction / time_fraction
                    if quotient.denominator > 1:
                        print("Something went wrong when calculating multibar rests!")
                    r = quotient.numerator
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
        if self.glob:
            self.ssc_score[self.glob] = []
            self.parse_lyglob()
        else:
            self.glob = "Glob"
            self.ssc_score[self.glob] = []
        max = 0
        for part in self.parts:
            self.ssc_score[part] = []
            self.parse_lypart(part, self.get_partcontent_from_ly(part))
            if len(self.ssc_score[part]) > max:
                max = len(self.ssc_score[part])
        if len(self.ssc_score[self.glob]) < max:
            r = max - len(self.ssc_score[self.glob])
            self.ssc_score[self.glob] += [''] * r
        self.set_barnr_in_glob()

    def set_barnr_in_glob(self):
        for barnr, glob_dict in enumerate(self.ssc_score[self.glob]):
            if glob_dict:
                glob_dict['barnr'] = barnr

    def read_partdef(self, partdef, flipped=True):
        partdef_dict = {}
        for l in partdef.split("\n"):
            if l.strip():
                partname, shortname = tuple(l.split("="))
                if flipped:
                    partdef_dict[partname.strip()] = shortname.strip()
                else:
                    partdef_dict[shortname.strip()] = partname.strip()
        return partdef_dict

    def apply_globally_to_all_lyparts(self, text, barnr, after=False):
        for p in self.parts:
            if after:
                self.score[p][barnr] += text
            music = self.score[p][barnr].split()
            if music:
                music[0] += text
                self.score[p][barnr] = " ".join(music)

    def import_from_lyfile(self, ssc):
	self.ssc_score = ssc.score
        self.read_lyvars()
