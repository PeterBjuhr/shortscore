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
        shortScoreExampleFilename = shortScoreExampleDir + '/test.ssc'
        self.copyOfShortScoreExampleFilename = shortScoreDir + '/test.ssc'
        shutil.copyfile(shortScoreExampleFilename, self.copyOfShortScoreExampleFilename)
        self.shortscore = ShortScore()

    def tearDown(self):
        os.remove(self.copyOfLilyPondExampleFilename)
        os.remove(self.copyOfShortScoreExampleFilename)

    def testReadPartDef(self):
        partdef = 'all=a\nbell=b'
        result = self.shortscore.read_partdef(partdef);
        expected = {'a': 'all', 'b': 'bell'}
        self.assertEquals(result, expected)

    def testReadShortScore(self):
        self.shortscore.read_shortscore(self.copyOfShortScoreExampleFilename)
        self.assertEquals(self.shortscore.score['sVln'][5], 'bes8:g:mf:gl:a2 bes8 g')

    def testParseGlobalData(self):
        glob = 'a:1,b:2'
        barnr = 1
        glob_dict_result = self.shortscore.parse_global_data(glob, barnr)
        self.assertEquals(glob_dict_result, {'a': '1', 'b': '2', 'u': '1', 'barnr': 1})

    def testGlobalDataToStr(self):
        result = self.shortscore.global_data_to_str({'a': '1', 'b': '2', 'barnr': '123'})
        expected = 'a:1,b:2'
        self.assertEquals(result, expected)

    def testWriteToShortScoreFile(self):
        self.shortscore.write_to_shortscore_file(self.copyOfShortScoreExampleFilename)
        with open(self.copyOfShortScoreExampleFilename) as r:
            text = r.read()
            self.assertEquals('tstFlute = fl' in text, True)


def suite():
    suite1 = unittest.makeSuite(ShortScoreTestCase)
    return unittest.TestSuite((suite1))

if __name__ == '__main__':
    unittest.main()
