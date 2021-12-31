import os

from .shortScoreLexer import ShortScoreLexer
from .shortScoreParser import ShortScoreParser
from .backTranslator import BackTranslator
from .lilypond.lilypondExporter import LilypondExporter
from .lilypond.lilypondImporter import LilypondImporter
from .musicxml.musicxmlExporter import MusicXMLExporter
from .musicxml.musicxmlImporter import MusicXMLImporter

class ShortScore():
    """
    Representing a shortscore
    """
    def __init__(self, ssc_file=None, language='default'):
        self.set_language(language)
        self.backtranslator = BackTranslator()
        self.unit = '1'
        self.parts = []
        if ssc_file:
            partdef, self.ssc_text = self.get_shortscore_from_file(ssc_file)
            self.partdef = self.read_partdef(partdef)
        else:
            self.partdef = {}
        glob = 'glob'
        self.glob = glob
        self.init_score()

    def set_language(self, language):
        self.language = language
        self.lexer = ShortScoreLexer(language)
        self.parser = ShortScoreParser(language)
        self.mxml_exporter = MusicXMLExporter(language)

    def init_score(self):
        self.score = {}
        self.score[self.glob] = []
        if self.parts:
            for p in self.parts:
                self.score[p] = []

    def get_shortscore_from_file(self, shortscore_file):
        try:
            with open(shortscore_file) as r:
                text = r.read()
        except IOError:
            return False
        # Read part definition
        try:
            partdef, ssc = tuple(text.split("@@@"))
        except ValueError:
            partdef = ''
            ssc = text
        return partdef, ssc

    def read_partdef(self, partdef, flipped=False):
        partdef_dict = {}
        for line in partdef.split("\n"):
            if line.strip():
                partname, shortname = tuple(line.split("="))
                if flipped:
                    partdef_dict[partname.strip()] = shortname.strip()
                else:
                    partdef_dict[shortname.strip()] = partname.strip()
        return partdef_dict

    def explode_chords(self, music, nrofparts):
        parts = [''] * nrofparts
        start = 0
        for n, t in enumerate(music):
            if t == '<':
                parts = [p + music[start:n] for p in parts]
                start = n + 1
            elif t == '>':
                try:
                    dura = music[n + 1:].split()[0]
                except IndexError:
                    dura = ''
                if not dura.isdigit():
                    dura = ''
                for i, c in enumerate(music[start:n].split()):
                    parts[i] += c + dura
                start = n + 1 + len(dura)
        return [p + music[start:] for p in parts]

    def read_shortscore(self, shortscore_file):
        # Get scortcore
        partdef, ssc_str = self.get_shortscore_from_file(shortscore_file)
        self.partdef = partdef_dict = self.read_partdef(partdef)
        self.parts = partdef_dict.keys()
        # Read shortscore
        self.init_score()
        bars = ssc_str.split("|")
        for barnr, bar in enumerate(bars):
            if not bar.strip():
                continue
            # Add empty bar to each part
            for instrument in self.score:
                self.score[instrument].append('')
            if '@' in bar:
                glob, bar = tuple(bar.split("@"))
                self.score[self.glob][-1] = self.parse_global_data(glob, barnr)
            parts = bar.split("/")

            for p in parts:
                if not p.strip():
                    continue
                try:
                    parts, music = p.split("::")
                except IndexError:
                    print(p)
                part_list = [p.strip() for p in parts.split(",")]
                if parts.strip().startswith('<'):
                    part_music = self.explode_chords(music, len(part_list))
                    part_list[0] = part_list[0][1:]
                else:
                    part_music = [music] * len(part_list)
                for pnr, partname in enumerate(part_list):
                    try:
                        self.score[partname][-1] = part_music[pnr].strip()
                    except KeyError:
                        print("Error: " + partname + " not found in score!")

    def parse_global_data(self, glob, barnr):
        glob_dict = {}
        glob_dict['barnr'] = barnr
        for data in glob.split(","):
            data = data.strip()
            if data:
                key, val = tuple(data.split(":"))
                glob_dict[key] = val
        if 'u' in glob_dict:
            self.unit = glob_dict['u']
        else:
            glob_dict['u'] = self.unit
        return glob_dict

    def global_data_to_str(self, glob_dict):
        glob_list = []
        for key in glob_dict:
            if key != 'barnr': # Do not write out bar number
                glob_list.append(":".join([key, glob_dict[key]]))
        return ",".join(glob_list)

    def write_to_shortscore_file(self, shortscore_file):
        if os.path.isfile(shortscore_file):
            partdef, ssc = self.get_shortscore_from_file(shortscore_file)
            partdef_dict = self.read_partdef(partdef, flipped=True)
        else:
            partdef_dict = {fullname: shortname for shortname, fullname in self.partdef.items()}
            partdef = "\n".join("=".join((fullname, shortname)) for fullname, shortname in partdef_dict.items())
            partdef += "\n"
        with open(shortscore_file, "w") as w:
            w.write(partdef)
            w.write("@@@\n")
            for barnr, bar in enumerate(self.score['glob']):
                if bar:
                    w.write(self.global_data_to_str(bar) + "@\n")
                bardict = {}
                for part in self.score:
                    if part == 'glob':
                        continue
                    try:
                        if self.score[part][barnr]:
                            # Use music as key
                            key = self.score[part][barnr]
                            if key in bardict:
                                bardict[key].append(part)
                            else:
                                bardict[key] = [part]
                    except IndexError:
                        pass
                # write bar
                parts_list = []
                for music in bardict:
                    parts_list.append(",".join(bardict[music]) + ":: " + music)
                w.write(" / ".join(parts_list))
                w.write(" |\n")

    def export_to_ly(self, lyfile):
        """Export to lilypond file"""
        exporter = LilypondExporter(lyfile)
        exporter.export_to_lyfile(self)

    def import_from_ly(self, lyfile):
        """Import from lilypond file"""
        self.init_score()
        importer = LilypondImporter(lyfile)
        importer.import_from_lyfile(self)

    def export_to_mxml(self, xml_file):
        """Export to MusicXML file"""
        for num, part in enumerate(self.parts):
            self.mxml_exporter.setup_part(part, num)
            for num, bar in enumerate(self.score[part]):
                bar_number = num + 1
                if bar:
                    self.mxml_exporter.export_bar(self.score[self.glob][num], bar, bar_number)
                else:
                    self.mxml_exporter.make_multi_rest(bar_number)
        self.mxml_exporter.write_to_file(xml_file)

    def import_from_mxml(self, xmlfile):
        """Import from MusicXML file"""
        importer = MusicXMLImporter(xmlfile)
        import_dict = importer.do_import()
        partdef_list = list(import_dict['partdef'])
        self.partdef = {pabbr: pname for pid, pname, pabbr in partdef_list}
        mxml_partdef = {pid: pabbr for pid, pname, pabbr in partdef_list}
        for part_id in import_dict['parts']:
            ssc_part = mxml_partdef[part_id]
            self.parts.append(ssc_part)
            self.score[ssc_part] = []
            for bar_number, bar_gen in import_dict['parts'][part_id]:
                bar = "".join(self.backtranslator.translate_back(bar_gen))
                self.score[mxml_partdef[part_id]].append(bar)
        mult = int(bar_number) - 1
        self.score['glob'] = [''] * mult
