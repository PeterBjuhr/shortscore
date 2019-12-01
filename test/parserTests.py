import unittest

try:
    from shortscore.shortScoreLexer import ShortScoreLexer
    from shortscore.shortScoreParser import ShortScoreParser
except ImportError:
    import sys
    sys.path.append('../shortscore')
    from shortScoreLexer import ShortScoreLexer
    from shortScoreParser import ShortScoreParser

class ShortScoreLexerTests(unittest.TestCase):
    def setUp(self):
        self.ssc_lexer = ShortScoreLexer()
        self.ssc_parser = ShortScoreParser()

    def test_basics(self):
        expected_list = [
                "NoteStart",
                "PitchStart",
                "PitchStep",
                "Octave",
                "PitchEnd",
                "Duration",
                "NoteEnd",
                "NoteStart",
                "PitchStart",
                "PitchStep",
                "PitchAlter",
                "Octave",
                "PitchEnd",
                "Duration",
                "NoteEnd",
                "NoteStart",
                "PitchStart",
                "PitchStep",
                "Octave",
                "PitchEnd",
                "Duration",
                "NoteEnd"
        ]
        resulting_list = []
        for item in self.ssc_parser.parse(self.ssc_lexer.lex('a4 bf4 c2')):
            resulting_list.append(item.__class__.__name__)
        self.assertEquals(resulting_list, expected_list)
    
    def test_implicit_durations(self):
        expected_list = [
                "NoteStart",
                "PitchStart",
                "PitchStep",
                "Octave",
                "PitchEnd",
                "Duration",
                "NoteEnd",
                "NoteStart",
                "PitchStart",
                "PitchStep",
                "PitchAlter",
                "Octave",
                "PitchEnd",
                "Duration",
                "NoteEnd",
                "NoteStart",
                "PitchStart",
                "PitchStep",
                "Octave",
                "PitchEnd",
                "Duration",
                "NoteEnd"
        ]
        resulting_list = []
        for item in self.ssc_parser.parse(self.ssc_lexer.lex('a4 bf c2')):
            resulting_list.append(item.__class__.__name__)
        self.assertEquals(resulting_list, expected_list)

    def test_dotted_duration(self):
        expected_list = [
                "NoteStart",
                "PitchStart",
                "PitchStep",
                "Octave",
                "PitchEnd",
                "Duration",
                "NoteEnd",
                "NoteStart",
                "PitchStart",
                "PitchStep",
                "Octave",
                "PitchEnd",
                "Duration",
                "NoteEnd"
        ]
        resulting_list = []
        for item in self.ssc_parser.parse(self.ssc_lexer.lex('a4. c')):
            resulting_list.append(item.__class__.__name__)
        self.assertEquals(resulting_list, expected_list)

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
