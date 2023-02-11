import re

from .lilypondFuncs import *

class LilypondExporter():
    """
    Export from shortscore to lilypond.
    """
    def __init__(self, lyfile):
        self.lyfile = lyfile

    def replace_ly_partcontent(self, partname, new_content):
        with open(self.lyfile) as r:
            text = r.read()
        pos = text.find(partname + ' =')
        if pos != -1:
            slice = text[pos:]
            start, end = get_bracket_positions(slice)
            slice = slice[:start + 1] + "\n" + new_content + "\n" + slice[end:]
            text = text[:pos] + slice
        else:
            print(f"LilyPondExporter: Warning! Can't find {partname} in ly-file!")
        with open(self.lyfile, "w") as w:
            w.write(text)

    def global_data_to_str(self, glob_dict):
        glob_list = []
        for key in glob_dict:
            if key != 'barnr': # Do not write out bar number
                glob_list.append(":".join([key, glob_dict[key]]))
        return ",".join(glob_list)

    def output_global_data_to_ly(self, glob_dict):
        output = []
        if 'm' in glob_dict:
            output.append(r"\time " + glob_dict['m'])
        if 't' in glob_dict:
            output.append(r"\tempo " + glob_dict['t'])
        if 'k' in glob_dict:
            output.append(r"\key " + glob_dict['k'])
        if 'rm' in glob_dict:
            if glob_dict['rm'] == 'd':
                output.append(r"\mark \default")
            else:
                output.append(r"\mark " + glob_dict['rm'])
        if 'd' in glob_dict:
            self.apply_globally_to_all_ly_parts(":" + glob_dict['d'], glob_dict['barnr'])
        # Handle rests
        if 'u' in glob_dict:
            output.append("s" + glob_dict['u'] + "*")
        return "\n".join(output)

    def replace_perc_notes(self, barmusic, percussion_instr):
        for percdef in percussion_instr:
            display_pitch, _, ly_name = percdef
            barmusic = re.sub(rf'x{display_pitch}([^,\']|$)', rf'{ly_name}\g<1>', barmusic)
        return barmusic

    def shortscore_to_ly(self, text):
        def do_barattrs(matches):
            change_dict = dict(tuple(m.split(':')) for m in matches[1].split(','))
            additions = []
            clef = change_dict.get('c')
            if clef:
                additions.append(f'\clef {clef}')
            dynamic = change_dict.get('d')
            if dynamic:
                additions.append(f'\{dynamic}')
            word = change_dict.get('w')
            if word:
                additions.append(f'^"{word}"')
            return " ".join(additions)

        def adapt_chord(matches):
            re_dura = re.compile(r'[\d\.]+')
            durations = [m for m in re_dura.findall(matches[1])]
            chord = '<' + re_dura.sub('', matches[1]) + '>'
            if durations:
                chord += durations[-1]
            return chord

        text = re.sub(r'>\s*<', r'~ ', text)
        text = re.sub(r'>\s*&', r'~ ', text)
        text = re.sub(r'«([^»]+)»', do_barattrs, text)
        text = re.sub(r'\{([^\}]+)\}', adapt_chord, text)
        text = re.sub(r'\[([^\]]+)\]:(\d+)\\(\d+):?(\d*)\b', r"\\tuplet \g<2>/\g<3> \g<4> {\g<1>}", text)
        text = re.sub(r'(\d+)\\(\d+):\[([^\]]+)\]', r"\\tuplet \g<1>/\g<2> {\g<3>}", text)
        text = re.sub(r'([a-gis\d>])\s*:gl:([\w\',]+)\b', r"\g<1> \\glissando( \g<2>)", text)
        text = re.sub(r'\b([\w\'\,]+\d*\.*)µ', r"\\acciaccatura \g<1>", text)
        text = re.sub(r'\[([^\]]+)\]:µ', r"\\acciaccatura {\g<1>}", text)
        text = text.replace('-·', '-.')
        text = re.sub(r':(\D+)\b', r"\\\g<1>", text)
        text = re.sub(r'𝄐', r"\\fermata", text)
        text = re.sub(r'×Ħ', r"\\downbow", text)
        text = re.sub(r'×V', r"\\upbow", text)
        text = re.sub(r'×+', r"-+", text)
        text = re.sub(r'_t', r"\\trill", text)
        text = re.sub(r'_ł', r":32", text)
        text = re.sub(r'(.+)<<(.+)', r'<<{\g<1>}\\\\{\g<2>}>>', text)
        text = re.sub(r'\(([a-gis\',]+\d*\.*)', r'\g<1>(', text)
        text = re.sub(r' +', ' ', text)
        return text

    def export_to_lyfile(self, ssc):
        def get_multirest(rest_str, multibar):
            if multibar > 1:
                multirest = rest_str + '*' + str(multibar)
            else:
                multirest = rest_str
            return multirest

        unit, m, glob = '1', 0, ''
        for b in ssc.score['glob']:
            if b:
                if m:
                    glob += str(m) + "\n"
                glob += self.output_global_data_to_ly(b)
                m = 1
            else:
                m += 1
        glob += str(m) + "\n"
        self.replace_ly_partcontent('Glob', glob)

        for part in ssc.partdef.keys():
            multibar = 0
            content = []
            ly_part = ssc.partdef[part]
            for barnr, bar in enumerate(ssc.score[part]):
                if 'u' in ssc.score['glob'][barnr]:
                    if unit and unit != ssc.score['glob'][barnr]['u']:
                        if multibar:
                            content.append(get_multirest(rest_str, multibar))
                            multibar = 0
                    unit = ssc.score['glob'][barnr]['u']
                    rest_str = 'R' + unit
                if bar:
                    if multibar:
                        content.append(get_multirest(rest_str, multibar))
                        multibar = 0
                    # Some music
                    percdef = ssc.percdef.get(part)
                    if percdef:
                        bar = self.replace_perc_notes(bar, percdef)
                    content.append(self.shortscore_to_ly(bar) + " |")
                else:
                    multibar += 1
            if multibar:
                content.append(get_multirest(rest_str, multibar))
                multibar = 0
            self.replace_ly_partcontent(ly_part, "\n".join(content))
