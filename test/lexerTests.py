import unittest

try:
    from shortscore.shortScoreLexer import ShortScoreLexer
except ImportError:
    import sys
    sys.path.append('../shortscore')
    from shortScoreLexer import ShortScoreLexer

class ShortScoreLexerTests(unittest.TestCase):
    def setUp(self):
        self.ssc_lexer = ShortScoreLexer()

    def test_basics(self):
        expected_list = [
                ("pitchstep", 'a'),
                ("octave", ''),
                ("duration", '4'),
                ("pitchstep", 'b'),
                ("pitchalter", 'f'),
                ("octave", ''),
                ("duration", '4'),
                ("pitchstep", 'c'),
                ("octave", ''),
                ("duration", '2')
        ]
        resulting_list = [token for token in self.ssc_lexer.lex('a4 bf4 c2')]
        self.assertEquals(resulting_list, expected_list)

    def test_dutch_pitches(self):
        expected_list = [
                ("pitchstep", 'a'),
                ("octave", ''),
                ("duration", '4'),
                ("pitchstep", 'a'),
                ("pitchalter", 'es'),
                ("octave", ''),
                ("pitchstep", 'e'),
                ("octave", ''),
                ("pitchstep", 'e'),
                ("pitchalter", 'es'),
                ("octave", '')
        ]
        self.ssc_lexer.set_alter_lang('dutch')
        resulting_list = [token for token in self.ssc_lexer.lex('a4 aes e ees')]
        self.assertEquals(resulting_list, expected_list)

    def test_short_durations(self):
        expected_list = [
                ("pitchstep", 'a'),
                ("octave", ''),
                ("duration", '16'),
                ("pitchstep", 'b'),
                ("octave", ''),
                ("duration", '32'),
                ("pitchstep", 'c'),
                ("octave", ''),
                ("duration", '32')
        ]
        resulting_list = [token for token in self.ssc_lexer.lex('a16 b32 c32')]
        self.assertEquals(resulting_list, expected_list)

    def test_quarter_tones(self):
        expected_list = [
                ("pitchstep", 'a'),
                ("octave", ''),
                ("duration", '4'),
                ("pitchstep", 'b'),
                ("pitchalter", 'qf'),
                ("octave", ''),
                ("duration", '4'),
                ("pitchstep", 'c'),
                ("pitchalter", 'qs'),
                ("octave", ''),
                ("duration", '2')
        ]
        resulting_list = [token for token in self.ssc_lexer.lex('a4 bqf4 cqs2')]
        self.assertEquals(resulting_list, expected_list)

    def test_dotted_duration(self):
        expected_list = [
                ("pitchstep", 'a'),
                ("octave", ''),
                ("duration", '4.'),
                ("pitchstep", 'c'),
                ("octave", '')
        ]
        resulting_list = [token for token in self.ssc_lexer.lex('a4. c')]
        self.assertEquals(resulting_list, expected_list)

    def test_octaves(self):
        expected_list = [
                ("pitchstep", 'a'),
                ("octave", "'"),
                ("duration", '4'),
                ("pitchstep", 'c'),
                ("octave", ',')
        ]
        resulting_list = [token for token in self.ssc_lexer.lex("a'4 c,")]
        self.assertEquals(resulting_list, expected_list)

    def test_tuplets(self):
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
