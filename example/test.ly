\version "2.19.62"

\include "instrumentDefs.ily"

tstGlob = {
  \time 3/4
  s2.*5
  \mark \default
  s2.*6

}

tstFlute = \relative c'' {
  a2.\pp |
  bes2.~ |
  bes2. |
  bes2. |
  R2.*7
}

tstOboe = \relative c'' {
  a2.\pp |
  bes2.~ |
  bes2. |
  bes2. |
  R2.*7
}

tstClarinet = \relative c'' {
  a2.\pp |
  bes2.~ |
  R2.*9
}

tstMarUpper = \relative c'' {
  a2.:32\pp |
  gis2.:32 |
  R2.*9
}

tstMarLower = \relative c' {
  R2.*11
}

tstPerc = \drummode {
  R2.*11
}

tstHarpRight = \relative c'' {
  R2.*11
}

tstHarpLeft = \relative c' {
  R2.*11
}

%%%%%%%%%%%%%%%%%Vln solo%%%%%%%%%%%%%

tstSoloViolin = \relative c'' {
  R2.*5
  \acciaccatura bes8\mf \glissando( a2) bes8 g |
  bes2 \glissando( fis8) g |
  a16-. d,-. c'-. d,-. d'-. d,-. a'-. d,-. g'-. d,-. f-. d-. |
  g'2 \tuplet 3/2 {a8( cis d)} |
  e2 a,16( cis d e) |
  g2. |
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


tstViolinI = \relative c'' {
  R2.*2
  \acciaccatura bes8 \glissando( a2) bes8 g |
  bes2 \glissando( fis8) g |
  a8-.\mf c-. d-. a-. g-. f-. |
  R2.*6
}

tstViolinII = \relative c'' {
  R2.*4
  a8-.\mf c-. d-. a-. g-. f-. |
  R2.*6
}

tstViola = \relative c' {
  R2.*4
  c8-.\mf e-. f-. g-. e-. g-. |
  R2.*4
  a8 cis d e g,4( |
  bes2.) |
}

tstCello = \relative c {
  R2.*4
  bes4\mf( a2) |
  R2.*3
  bes2 a4 |
  R2.*1
  d2. |
}

tstContrabass = \relative c {
  a2.\pp |
  bes2.~ |
  bes2. |
  bes2. |
  bes4\mf( a2) |
  bes2 a4 |
  bes2 g4 |
  \instrumentSwitch "pizzstring" a8 c d a g f |
  \instrumentSwitch "arcostr" bes2 a4 |
  R2.*1
  d2. |
}

tstFlutePart = \new Staff \with {
  instrumentName = "Flute"
  midiInstrument = "flute"
} \tstFlute

tstOboePart = \new Staff \with {
  instrumentName = "Oboe"
  midiInstrument = "oboe"
} \tstOboe

tstClarinetPart = \new Staff \with {
  instrumentName = "Clarinet"
  midiInstrument = "clarinet"
} \tstClarinet

tstMarimbaPart = \new PianoStaff \with {
  instrumentName = "Marimba"
} <<
  \new Staff = "right" \with {
    midiInstrument = "marimba"
  } \tstMarUpper
  \new Staff = "left" \with {
    midiInstrument = "marimba"
  } { \clef bass \tstMarLower }
>>

tstPercPart = \new DrumStaff \with {
  \consists "Instrument_name_engraver"
  instrumentName = "Percussion"
} \tstPerc

tstHarpPart = \new PianoStaff \with {
  instrumentName = "Harp"
} <<
  \new Staff = "upper" \with {
    midiInstrument = "orchestral harp"
  } \tstHarpRight
  \new Staff = "lower" \with {
    midiInstrument = "orchestral harp"
  } { \clef bass \tstHarpLeft }
>>

tstSoloViolinPart = \new Staff \with {
  instrumentName = "Violin solo"
  midiInstrument = "violin"
} \tstSoloViolin

tstViolinIPart = \new Staff \with {
  instrumentName = "Violin I"
  midiInstrument = "string ensemble 1"
} \tstViolinI

tstViolinIIPart = \new Staff \with {
  instrumentName = "Violin II"
  midiInstrument = "string ensemble 1"
} \tstViolinII

tstViolaPart = \new Staff \with {
  instrumentName = "Viola"
  midiInstrument = "string ensemble 1"
} { \clef alto \tstViola }

tstCelloPart = \new Staff \with {
  instrumentName = "Cello"
  midiInstrument = "string ensemble 1"
} { \clef bass \tstCello }

tstContrabassPart = \new Staff \with {
  instrumentName = "Contrabass"
  midiInstrument = "string ensemble 1"
} { \clef bass \tstContrabass }

%%{
\score {
  <<
    \new Devnull \tstGlob
    \new StaffGroup <<
      \tstFlutePart
      \tstOboePart
      \tstClarinetPart
    >>
    \new StaffGroup <<
      \tstMarimbaPart
      \tstPercPart
    >>
    \tstHarpPart
    \tstSoloViolinPart
    \new StaffGroup <<
      \tstViolinIPart
      \tstViolinIIPart
      \tstViolaPart
      \tstCelloPart
      \tstContrabassPart
    >>
  >>
  \layout { }
}
\score {
  <<
    \new StaffGroup <<
      \tstFlutePart
      \tstOboePart
      \tstClarinetPart
    >>
    \new StaffGroup <<
      \tstMarimbaPart
      \tstPercPart
    >>
    \tstHarpPart
    \tstSoloViolinPart
    \new StaffGroup <<
      \tstViolinIPart
      \tstViolinIIPart
      \tstViolaPart
      \tstCelloPart
      \tstContrabassPart
    >>
  >>
  \midi { }
}
%}