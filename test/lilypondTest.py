import os
import shutil
import sys
import unittest

try:
    from shortscore.shortScore import ShortScore
    from shortscore.lilypond.lilypondExporter import LilypondExporter
    from shortscore.lilypond.lilypondImporter import LilypondImporter
    import shortscore.lilypond.lilypondFuncs as lilypondFuncs
except ImportError:
    import sys
    sys.path.append('../shortscore')
    from shortScore import ShortScore
    from lilypond.lilypondExporter import LilypondExporter
    from lilypond.lilypondImporter import LilypondImporter
    import lilypond.lilypondFuncs as lilypondFuncs

class ShortScoreTestCase(unittest.TestCase):
    def setUp(self):
        shortScoreDir = os.path.dirname(os.path.realpath(__file__))
        shortScoreExampleDir = shortScoreDir + '/../example'
        lilyPondExampleFilename = shortScoreExampleDir + '/test.ly'
        self.copyOfLilyPondExampleFilename = shortScoreDir + '/test.ly'
        shutil.copyfile(lilyPondExampleFilename, self.copyOfLilyPondExampleFilename);
        shortScoreExampleFilename = shortScoreExampleDir + '/test.sly'
        self.copyOfShortScoreExampleFilename = shortScoreDir + '/test.sly'
        shutil.copyfile(shortScoreExampleFilename, self.copyOfShortScoreExampleFilename)
        self.exporter = LilypondExporter(self.copyOfLilyPondExampleFilename)
        self.importer = LilypondImporter(self.copyOfLilyPondExampleFilename)

    def tearDown(self):
        os.remove(self.copyOfLilyPondExampleFilename)
        os.remove(self.copyOfShortScoreExampleFilename)

    def testGetPartNamesFromLy(self):
        expectedParts = [
        'tstFlute',
        'tstOboe',
        'tstClarinet',
        'tstMarUpper',
        'tstMarLower',
        'tstPerc',
        'tstHarpRight',
        'tstHarpLeft',
        'tstSoloViolin',
        'tstViolinI',
        'tstViolinII',
        'tstViola',
        'tstCello',
        'tstContrabass'
        ]
        glob, parts = self.importer.get_partnames_from_ly()
        self.assertEquals(glob, 'tstGlob')
        self.assertEquals(parts, expectedParts)

    def testParseLyGlob(self):
        expected = [{'u': '2.', 'm': '3/4'}, '', '', '', '', {'rm': 'd', 'u': '2.'}, '', '', '', '', '']
        self.importer.parse_lyglob()
        result = self.importer.ssc_score['glob']
        self.assertEquals(result, expected)

    def testGetBracketPositions(self):
        self.assertEquals(lilypondFuncs.get_bracket_positions(''), None)
        self.assertEquals(lilypondFuncs.get_bracket_positions('{'), None)
        self.assertEquals(lilypondFuncs.get_bracket_positions('{{}'), None)
        self.assertEquals(lilypondFuncs.get_bracket_positions(' {{}'), None)
        self.assertEquals(lilypondFuncs.get_bracket_positions('{}'), (0, 1))
        self.assertEquals(lilypondFuncs.get_bracket_positions('{{}}'), (0, 3))
        self.assertEquals(lilypondFuncs.get_bracket_positions(' {{}}'), (1, 4))
        self.assertEquals(lilypondFuncs.get_bracket_positions(' a { a } a'), (3, 7))

    def testGetPartContentFromLy(self):
        expectedFlutePart = '\n  a2.\\pp |\n  bes2.~ |\n  bes2. |\n  bes2. |\n  R2.*7'
        flutepart = self.importer.get_partcontent_from_ly('tstFlute')
        self.assertEquals(flutepart, expectedFlutePart)
        self.assertEquals(self.importer.get_partcontent_from_ly('nonExisting'), None)

    def testReplaceLyPartContent(self):
        part_name = 'tstFlute'
        new_content = 'new_content'
        self.exporter.replace_ly_partcontent(part_name, new_content)
        with open(self.copyOfLilyPondExampleFilename) as r:
            text = r.read()
            self.assertEquals(new_content in text, True)

    def testLy2shortScore(self):
        self.assertEquals(self.importer.ly2shortscore('\\tuplet 3/2 4 {a8 b c a b c}'), '[a8 b c a b c]:3\\2:4')
        self.assertEquals(self.importer.ly2shortscore('\\tuplet 3/2 {a8 b c}'), '[a8 b c]:3\\2')

    def testParseLyPart(self):
        part = '\n  a2.\\pp |\n  bes2.~'
        partname = 'tstFlute'
        self.importer.parts.append(partname)
        self.importer.ssc_score[partname] = []
        self.importer.parse_lypart(partname, part)
        self.assertEquals(self.importer.ssc_score[partname], ['a2.:pp', 'bes2.~'])

    def testHandleMultibarRests(self):
        glob = """\\time 6/8
        s2.*4"""
        self.importer.ssc_score[self.importer.glob] = []
        self.importer.parse_lyglob(glob)
        self.importer.ssc_score['tstSoloViolin'] = []
        self.importer.handle_multibar_rests('tstSoloViolin', 'R2.*2', 1)
        result = self.importer.ssc_score['tstSoloViolin']
        self.assertEquals(result, ['', ''])
        self.importer.ssc_score['tstSoloViolin'] = []
        self.importer.handle_multibar_rests('tstSoloViolin', 'R4.*4', 2)
        result = self.importer.ssc_score['tstSoloViolin']
        self.assertEquals(result, ['', ''])

    def testMultibarRestsComplexTime(self):
        glob = """\\time 5/8
        s8*5*8"""
        self.importer.ssc_score[self.importer.glob] = []
        self.importer.parse_lyglob(glob)
        self.importer.ssc_score['tstSoloViolin'] = []
        self.importer.handle_multibar_rests('tstSoloViolin', 'R8*5*4', 2)
        result = self.importer.ssc_score['tstSoloViolin']
        self.assertEquals(result, ['', '', '', ''])

    def testOutputGlobalDataToLy(self):
        glob_dict = {'m': '1'}
        result = self.exporter.output_global_data_to_ly(glob_dict)
        self.assertEquals(result, '\\time 1')

    def testShortScoreMusicToLy(self):
        expected = '\\tuplet 1/2 3 {a b c}'
        result = self.exporter.shortscore_to_ly('[a b c]:1\\2:3')
        self.assertEquals(result, expected)

    def test_export(self):
        shutil.copyfile(self.copyOfLilyPondExampleFilename, 'orgtest.ly')
        with open(self.copyOfLilyPondExampleFilename) as r:
            refcontent = r.readlines()
        expected = [x.strip() for x in refcontent if x.strip()]
        ssc = ShortScore()
        ssc.read_shortscore(self.copyOfShortScoreExampleFilename)
        self.exporter.export_to_lyfile(ssc)
        with open(self.copyOfLilyPondExampleFilename) as r:
            gencontent = r.readlines()
        result = [x.strip() for x in gencontent if x.strip()]
        self.assertEquals(result, expected)

    def test_import(self):
        ssc = ShortScore()
        ssc.read_shortscore(self.copyOfShortScoreExampleFilename)
        expected = ssc.score
        self.importer.import_from_lyfile(ssc)
        self.assertEquals(self.importer.ssc_score, expected)


def suite():
    suite1 = unittest.makeSuite(ShortScoreTestCase)
    return unittest.TestSuite((suite1))

if __name__ == '__main__':
    unittest.main()
