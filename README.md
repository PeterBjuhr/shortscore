Shortscore
====================

Shortscore is intended to be a simple text-based music notation syntax especially created for easy handling of large scores.

The basic principle is to write one measure at a time horizontally of the full score. Only parts that actually contain music are included.

See the [example folder](https://github.com/PeterBjuhr/shortscore/tree/master/example) for an example with resulting score.

Presently the shortcode notation is closely associated with LilyPond music notation. And basic import and export functionality is included.  

### Advantages of using Shortscore

When working with a score especially if it is containing several parts it is often very convinient to have easy access to all the different parts at once. This is presumably the case when working with a graphical notation software, but in text-based music notation it is less easily obtained. In Shortscore you can easily add, remove, copy or remove a full bar for all parts vertically across the score. In addition:

- when several different parts contain the same music in unison or in different octaves you only need to type the music once.
- when the rhythm is the same for several different parts but not the pitches so a chord is formed you can also type those parts together notating that chord.  
- you can also easily move the music from one part to another.
- you don't need to type in a lot of rests - when a part is absent from a bar a full bar rest is assumed.

### Disadvantages

You need to type in the instrument on every bar so make sure you use a good shortname for each instrument.
