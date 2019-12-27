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
        with open('testfiles/expected_basics.xml') as file_obj:
            expected_str = file_obj.read()
        self.ssc_exporter.setup_part('test', 1)
        self.ssc_exporter.export_bar('a4 bf c2')
        resulting_str = self.ssc_exporter.write_to_str()
        self.assertEquals(resulting_str, expected_str.strip())

    def test_divisions(self):
        expected_divs = 8
        self.ssc_exporter.setup_part('test', 1)
        self.ssc_exporter.export_bar('a32 bf g8 c2.')
        resulting_divs = self.ssc_exporter.divisions
        self.assertEquals(resulting_divs, expected_divs)
    

if __name__ == '__main__':
    unittest.main()
