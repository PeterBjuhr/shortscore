def get_bracket_positions(text):
    stack = []
    start = False
    end = False
    for i, t in enumerate(text):
        if t == '{':
            if start is not False:
                stack.append('')
            else:
                start = i
        if t == '}':
            if stack:
                stack.pop()
            else:
                end = i
                return start, end
