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
        self.percdef = {}
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
            t = re.search(r"\\tempo\s*(\D+)?(\d+\.?=\d+)", g)
            if t:
                text = t.group(1)
                if text:
                    glob_dict['tt'] = text.strip().strip('"')
                tempo = t.group(2)
                glob_dict['t'] = tempo
            rm = re.search(r"\\mark\s*([\w\W]+)\b", g)
            if rm:
                mark = rm.group(1)
                if mark == r'\default':
                    glob_dict['rm'] = 'd'
                else:
                    glob_dict['rm'] = mark
            if g.strip().startswith('s'):
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
                        scheme_dict = dict(scheme_dict, **glob_dict)
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

    def replace_perc_notes(self, barmusic, percussion_instr):
        for percdef in percussion_instr:
            try:
                display_pitch, _, ly_name = percdef
                barmusic = barmusic.replace(ly_name, 'x' + display_pitch)
            except ValueError:
                print(f"Warning! Missing percussion definition when importing from {self.lyfile}")
        return barmusic

    def ly2shortscore(self, text):
        def do_clef(matches):
            clef = matches[1].replace('^8', '8U').replace('_8', '8D')
            return f'«c:{clef}» '

        text = re.sub(r'\\tuplet\s*(\d+)/(\d+)\s*\{([^\}]+)}', r'\g<1>\\\g<2>:[\g<3>]', text)
        text = re.sub(r'<<\s*\{\s*([^}]+)\}\s*\\\\\s*\{\s*([^}]+)\}\s*>>', r'\g<1><<\g<2>', text)
        text = re.sub(r'\\fermata\b', r'𝄐', text)
        text = re.sub(r'\\clef\s"?(\w+)"?\s', do_clef, text)
        text = re.sub(r'\^"([^"]+)"', r'«w:\g<1>»', text)
        text = re.sub(r'\\instrumentSwitch\s"([^"]+)"', r'«w:\g<1>»', text)
        text = re.sub(r'\\(?:grace|acciaccatura)\s*([\w\',]+\d*\.*)', r'\g<1>µ', text)
        text = re.sub(r'\\(?:grace|acciaccatura)\s*\{([^\}]+)}', r'[\g<1>]:µ', text)
        text = re.sub(r'\\downbow\b', r'×Ħ', text)
        text = re.sub(r'\\upbow\b', r'×V', text)
        text = re.sub(r'\\snappizzicato\b', r'×Ỏ', text)
        text = re.sub(r'<([a-giqst\',]+)(~)?\s*([a-giqst\',~]+)\s*\\harmonic\s*>', r"{\g<1>\g<2>♢ab \g<3>♢at \g<1>''\g<2>♢as}", text)
        text = re.sub(r'\\trill\b', r'_t', text)
        text = re.sub(r':32\b', r'_ł', text)
        text = re.sub(r'<([^<>]+)>', r'{\g<1>}', text)
        text = re.sub(r'([a-giqst\',]+\d*\s*[^a-g]*\w*)\(([^\)]+)\)', r'(\g<1> \g<2>)', text)
        text = re.sub(r'([a-giqst\',]+\d*\.*-*\s*)\(', r'(\g<1>', text)
        text = re.sub(r'([a-giqst\',]+\d*\.*)\(\s*~', r'(\g<1> >', text)
        text = re.sub(r'\\([mpfsz<>!]+)', r'«d:\g<1>»', text)
        text = text.replace('-.', '-·')
        text = text.replace('-+', '×+')
        text = re.sub(r'\s+', r' ', text)
        text = re.sub(r'~', r'>', text)
        text = re.sub(r'([>a-giqst\d])\s*\\glissando\s*(\w+\s*\)?)', r'\g<1>~ ^\g<2>', text)
        text = re.sub(r'\\([a-z]+)\b', r':\g<1>', text)
        return text

    def handle_multibar_rests(self, partname, bar, barnr):
        def multiply_list(multlist):
            product = 1
            for i in multlist:
                if i:
                    product *= int(i)
            return product

        def get_multirests(mrest_str, scheme):
            unit = scheme.get('u')
            if mrest_str.startswith(unit):
                bar_rests_str = mrest_str.replace(unit, '', 1).strip('*')
            else:
                time_sign = scheme.get('m')
                bar_len = Fraction(time_sign)
                base_str = mrest_str.split('*')[0]
                num_dots = base_str.count('.')
                base_len = Fraction(1, int(base_str.replace('.', '')))
                for n in range(num_dots):
                    base_len *= Fraction('3/2')
                if base_len < bar_len:
                    bar_rests_str = "*".join(mrest_str.split('*')[2:])
                else:
                    bar_rests_str = "*".join(mrest_str.split('*')[1:])
            return multiply_list(bar_rests_str.split('*'))

        words = bar.split()
        music_only = []
        for i, w in enumerate(words):
            if 'R' in w:
                w = w.replace('R', '')
                try:
                    barscheme = self.lyscheme[barnr]
                except IndexError:
                    raise Exception(f'Index {barnr} is missing in the bar scheme. The scheme has {len(self.lyscheme)} bars.')
                num_bar_rests = get_multirests(w, barscheme)
                self.ssc_score[partname] += [''] * num_bar_rests
                barnr += num_bar_rests
            else:
                music_only.append(w)
        return " ".join(music_only)

    def parse_lypart(self, partname, part):
        for b in part.split("|"):
            barnr = len(self.ssc_score[partname])
            b = self.handle_multibar_rests(partname, b, barnr)
            percdef = self.percdef.get(partname)
            if percdef:
                b = self.replace_perc_notes(b, percdef)
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
        self.percdef = ssc.percdef
        self.read_lyvars()
