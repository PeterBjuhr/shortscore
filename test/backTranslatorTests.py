import unittest

try:
    from shortscore.shortScoreLexer import ShortScoreLexer
    from shortscore.shortScoreParser import ShortScoreParser
    from shortscore.backTranslator import BackTranslator
except ImportError:
    import sys
    sys.path.append('../shortscore')
    from shortScoreLexer import ShortScoreLexer
    from shortScoreParser import ShortScoreParser
    from backTranslator import BackTranslator

class ShortScoreLexerTests(unittest.TestCase):
    def setUp(self):
        self.ssc_lexer = ShortScoreLexer()
        self.ssc_parser = ShortScoreParser()
        self.ssc_backtranslator = BackTranslator()

    def test_basics(self):
        expected_str = "a4 bf c2"
        parser_tree = self.ssc_parser.parse(self.ssc_lexer.lex('a4 bf4 c2'))
        resulting_str = "".join(self.ssc_backtranslator.translate_back(parser_tree)).strip()
        self.assertEquals(resulting_str, expected_str)
    
    def test_implicit_durations(self):
        expected_str = "a4 bf c2"
        parser_tree = self.ssc_parser.parse(self.ssc_lexer.lex('a4 bf c2'))
        resulting_str = "".join(self.ssc_backtranslator.translate_back(parser_tree)).strip()
        self.assertEquals(resulting_str, expected_str)

    def test_dotted_duration(self):
        expected_str = "a4. c"
        parser_tree = self.ssc_parser.parse(self.ssc_lexer.lex('a4. c'))
        resulting_str = "".join(self.ssc_backtranslator.translate_back(parser_tree)).strip()
        self.assertEquals(resulting_str, expected_str)

    def rtest_tuplets(self):
        expected_list = [
                ("tupletstart", '['),
                ("pitchstep", 'a'),
                ("octave", ""),
                ("duration", '8'),
                ("pitchstep", 'b'),
                ("octave", ""),
                ("pitchstep", 'c'),
                ("octave", ''),
                ("tupletend", ']'),
                ("modification", ':'),
                ("tupletratio", '3\2'),
                ("pitchstep", 'd'),
                ("octave", ""),
                ("duration", '4')
        ]
        resulting_list = [token for token in self.ssc_lexer.lex("[a8 b c]:3\2 d4")]
        self.assertEquals(resulting_list, expected_list)


if __name__ == '__main__':
    unittest.main()
