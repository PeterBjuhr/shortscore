import re

def note(s):
    m = re.match(r'([a-z]+)(?:([1-9])(\.?))?', s)
    if m:
        return ("NOTE", ("PITCH_STEP", m.group(1)), ("DURATION", m.group(2), ("DOTTED", m.group(3))))
    return ("PARSE_FAILED", "NOTE", s)

def note_list_helper(s):
    spl = re.split(r"\s+", s)
    return map(note, spl)

def tuplet(s):
    m = re.match(r"\[([^\]]*)\](?::(\d+\\\d+))?", s)
    if m:
        return ("TUPLET", ("TUPLET_NOTES", note_list_helper(m.group(1))), ("TUPLET_RATIO", m.group(2)))
    return ("PARSE_FAILED", "TUPLET", s)

def note_or_tuplet_list_helper(s_in):
    s = s_in.strip()
    if not s:
        return []
    m = re.match(r"(\[[^\]]*\](?::\d+\\\d+)?)", s)
    if m:
        tuplet_string = m.group(1)
        rest = s[m.end():].strip()
        return [tuplet(tuplet_string)] + note_or_tuplet_list_helper(rest)
    space_index = s.find(" ")
    if space_index == -1:
        note_string = s
        rest = ""
    else:
        note_string = s[0:space_index]
        rest = s[space_index:].strip()
    return [note(note_string)] + note_or_tuplet_list_helper(rest)

def bar(s):
    return ("BAR", note_or_tuplet_list_helper(s))

def parse(s):
    return bar(s)

def print_parse(s):
    print "Input:\t", s
    print "Output:\t", parse(s)

examples = [
    # "a",
    # "a8",
    # "a a8",
    # "a4 bf4 c2",
    # "a4 bf c2",
    # "a4. c",
    "[a8 b c]:3\\2 d4"
]

for e in examples:
    print_parse(e)