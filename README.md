Shortscore
====================

Shortscore is intended to be a simple text-based music notation syntax especially created for easy handling of large scores.

The basic principle is to write one measure at a time horizontally of the full score. Only parts that actually contain music are included.

See the [example folder](https://github.com/PeterBjuhr/shortscore/tree/master/example) for an example with resulting score.

### Advantages of using Shortscore

When working with a score especially if it is containing several parts it is often very convinient to have easy access to all the different parts at once. This is presumably the case when working with a graphical notation software, but in text-based music notation it is less easily obtained. In Shortscore you can easily add, remove, copy or remove a full bar for all parts vertically across the score. In addition:

- when several different parts contain the same music in unison or in different octaves you only need to type the music once.
- when the rhythm is the same for several different parts but not the pitches so a chord is formed you can also type those parts together notating that chord.  
- you can also easily move the music from one part to another.
- you don't need to type in a lot of rests - when a part is absent from a bar a full bar rest is assumed.

### Disadvantages

You need to type in the instrument on every bar so make sure you use a good shortname for each instrument.

### Portability

As the main purpose of the shortscore language and package is to create and edit scores, you are dependent of export functionality to do anything else. There is an export to Lilypond and an experimental export to musicxml.

### Quick reference

The shortscore language has been inspired by Lilypond and ABC notations. Perhaps yu can spot the simularities and differences?

notes: c d e f g b

raise octave: c'

lower octave: c,

durations: 1 2 4 8 16 32

chords: {c'4 e' g'} (also allowed alternative notation: {c' e' g'}4)

ties: c'4> <c'8

slurs: (c'4 d')

grace notes: (c'µ16 d'4)

tuplets (simple triol 3 over 2): 3\2:[c'8 d' e'] (also allowed alternative notation: [c'8 d' e']:3\2)
