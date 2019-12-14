from parseTreeClasses import NoteStart, NoteEnd, PitchStart, PitchEnd, PitchStep, PitchAlter, Octave, Duration

class BackTranslator:
    """Translates back to shortscore text from parse tree structure"""

    implicit = (
            Duration
        )
    
    whitespace_after = (
            NoteEnd
        )
 
    def translate_back(self, shortscore_parser_objects, use_implicit = True):
        for parser_object in shortscore_parser_objects:
            token = parser_object.get_token()
            if token:
                if use_implicit and isinstance(parser_object, self.implicit):
                    prev_implicit = getattr(self, parser_object.__class__.__name__, None)
                    if prev_implicit == token:
                        continue
                    else:
                        setattr(self, parser_object.__class__.__name__, token)
                yield token
            if isinstance(parser_object, self.whitespace_after):
                yield " "
