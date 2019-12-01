import unittest

try:
    from shortscore.backTranslator import BackTranslator
    from shortscore.musicxml.musicxmlExporter import MusicXMLExporter
    from shortscore.musicxml.musicxmlImporter import MusicXMLImporter
except ImportError:
    import sys
    sys.path.append('../shortscore')
    from backTranslator import BackTranslator
    from musicxml.musicxmlExporter import MusicXMLExporter
    from musicxml.musicxmlImporter import MusicXMLImporter

class MXLMImporterTests(unittest.TestCase):

    def setUp(self):
        self.ssc_exporter = MusicXMLExporter()
        self.ssc_backtranslator = BackTranslator()

    def generic_import_test_from_file(self, xmlfile, expected_str):
        importer = MusicXMLImporter('testfiles/' + xmlfile)
        resulting_str = "".join(self.ssc_backtranslator.translate_back(importer.do_import())).strip()
        self.assertEquals(resulting_str, expected_str)

    def generic_export_import_test(self, export_import_str):
        self.ssc_exporter.export_bar(export_import_str)
        importer = MusicXMLImporter(self.ssc_exporter.write_to_str())
        parser_obj_generator = importer.do_import()
        resulting_str = "".join(self.ssc_backtranslator.translate_back(list(parser_obj_generator))).strip()
        self.assertEquals(resulting_str, export_import_str)

    def test_basics(self):
        self.generic_import_test_from_file('test1.xml', "a'4 bf' c'2")

    def test_different_durations(self):
        self.generic_export_import_test('a32 bf g8 c2.')

    def test_octaves(self):
        self.generic_export_import_test("a,,4 b, c d' e''")

    def test_quarter_tones(self):
        self.generic_export_import_test("aqf4 btqf ctqs dqs eqf")

 
if __name__ == '__main__':
    unittest.main()
