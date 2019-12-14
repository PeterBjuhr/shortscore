import unittest

try:
    from shortscore.shortScoreLexer import ShortScoreLexer
    from shortscore.shortScoreParser import ShortScoreParser
    from shortscore.musicxml.musicxmlExporter import MusicXMLExporter
except ImportError:
    import sys
    sys.path.append('../shortscore')
    from shortScoreLexer import ShortScoreLexer
    from shortScoreParser import ShortScoreParser
    from musicxml.musicxmlExporter import MusicXMLExporter

class MXLMExportTests(unittest.TestCase):
    def setUp(self):
        self.ssc_lexer = ShortScoreLexer()
        self.ssc_parser = ShortScoreParser()
        self.ssc_exporter = MusicXMLExporter()

    def test_basics(self):
        expected_str = """<score-partwise version="3.0"><measure><attributes><divisions>1</divisions></attributes><note><pitch><step>A</step><octave>3</octave></pitch><duration>1</duration><type>quarter</type></note><note><pitch><step>B</step><alter>-1</alter><octave>3</octave></pitch><duration>1</duration><type>quarter</type></note><note><pitch><step>C</step><octave>3</octave></pitch><duration>2</duration><type>half</type></note></measure></score-partwise>"""
        self.ssc_exporter.export_bar('a4 bf c2')
        resulting_str = self.ssc_exporter.write_to_str()
        self.assertEquals(resulting_str, expected_str)

    def test_divisions(self):
        expected_divs = 8
        self.ssc_exporter.export_bar('a32 bf g8 c2.')
        resulting_divs = self.ssc_exporter.divisions
        self.assertEquals(resulting_divs, expected_divs)
    

if __name__ == '__main__':
    unittest.main()
