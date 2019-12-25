import os
import shutil
import sys
import unittest

try:
    from shortscore.shortScore import ShortScore
except ImportError:
    import sys
    sys.path.append('../shortscore')
    from shortScore import ShortScore


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
        self.shortScore = ShortScore(self.copyOfLilyPondExampleFilename)

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
        glob, parts = self.shortScore.getPartNamesFromLy()
        self.assertEquals(glob, 'tstGlob')
        self.assertEquals(parts, expectedParts)

    def testGetBracketPositions(self):
        self.assertEquals(self.shortScore.getBracketPositions(''), None)
        self.assertEquals(self.shortScore.getBracketPositions('{'), None)
        self.assertEquals(self.shortScore.getBracketPositions('{{}'), None)
        self.assertEquals(self.shortScore.getBracketPositions(' {{}'), None)
        self.assertEquals(self.shortScore.getBracketPositions('{}'), (0, 1))
        self.assertEquals(self.shortScore.getBracketPositions('{{}}'), (0, 3))
        self.assertEquals(self.shortScore.getBracketPositions(' {{}}'), (1, 4))
        self.assertEquals(self.shortScore.getBracketPositions(' a { a } a'), (3, 7))

    def testHandleMultibarRests(self):
        self.shortScore.initScore()
        if self.shortScore.glob:
            self.shortScore.score[self.shortScore.glob] = []
        glob = """\\time 6/8
        s2.*4"""
        self.shortScore.parseLyGlob(glob)
        self.shortScore.handleMultibarRests('tstSoloViolin', 'R2.*2')
        self.assertEquals(self.shortScore.score['tstSoloViolin'], ['', ''])
        self.shortScore.score['tstSoloViolin'] = []
        self.shortScore.handleMultibarRests('tstSoloViolin', 'R4.*4')
        self.assertEquals(self.shortScore.score['tstSoloViolin'], ['', ''])

    def testSetBarnrInGlob(self):
        self.shortScore.glob = 'tstGlob'
        self.shortScore.score['tstGlob'] = [{'u': '2.', 'm': '3/4'}]
        self.shortScore.setBarnrInGlob()
        expectedTstGlobScore = [{'u': '2.', 'm': '3/4', 'barnr': 0}]
        self.assertEquals(self.shortScore.score['tstGlob'], expectedTstGlobScore)

    def testCreatePartDefFromParts(self):
        self.shortScore.parts = ['tstFlute']
        self.shortScore.createPartDefFromParts(self.copyOfShortScoreExampleFilename)
        with open(self.copyOfShortScoreExampleFilename) as r:
            text = r.read()
            self.assertEquals('tstFlute =\n@@@\n' in text, True)

    def testReadPartDef(self):
        partDef = 'a=1\nb=2'
        result = self.shortScore.readPartDef(partDef);
        expected = {'a': '1', 'b': '2'}
        self.assertEquals(result, expected)

    def testReadShortScore(self):
        self.shortScore.readShortScore(self.copyOfShortScoreExampleFilename)
        self.assertEquals(self.shortScore.score['tstSoloViolin'][5], 'bes8:g:mf:gl:a2 bes8 g')

    def testParseGlobalData(self):
        glob = 'a:1,b:2'
        barnr = 1
        globDictResult = self.shortScore.parseGlobalData(glob, barnr)
        self.assertEquals(globDictResult, {'a': '1', 'b': '2', 'u': '1', 'barnr': 1})

    def testGlobalDataToStr(self):
        result = self.shortScore.globalDataToStr({'a': '1', 'b': '2', 'barnr': '123'})
        expected = 'a:1,b:2'
        self.assertEquals(result, expected)

    def testGetPartsFromPartDef(self):
        partDefDict = {'tstFlute': 'tstFluteReplacement'}
        result = self.shortScore.getPartsFromPartDef(partDefDict)
        expected = [
        'tstFluteReplacement',
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
        self.assertEquals(result, expected)

    def testWriteToShortScoreFile(self):
        self.shortScore.writeToShortScoreFile(self.copyOfShortScoreExampleFilename)
        with open(self.copyOfShortScoreExampleFilename) as r:
            text = r.read()
            self.assertEquals('tstFlute = fl' in text, True)

    def testOutputGlobalDataToLy(self):
        globDict = {'m': '1'}
        result = self.shortScore.outputGlobalDataToLy(globDict)
        self.assertEquals(result, '\\time 1')

    def testApplyGloballyToAllLyParts(self):
        text = 'applyGloballyToAllLyParts-testString'
        barnr = 0
        self.shortScore.readShortScore(self.copyOfShortScoreExampleFilename)
        self.shortScore.applyGloballyToAllLyParts(text, barnr)
        self.assertEquals(text in self.shortScore.score['tstContrabass'][barnr], True)

    def testShortScoreMusicToLy(self):
        expected = '\\tuplet 1/2 3 {abc}'
        result = self.shortScore.shortScoreMusicToLy('[abc]:1\\2:3')
        self.assertEquals(result, expected)


def suite():
    suite1 = unittest.makeSuite(ShortScoreTestCase)
    return unittest.TestSuite((suite1))

if __name__ == '__main__':
    unittest.main()
