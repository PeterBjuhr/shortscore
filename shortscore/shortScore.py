#!/usr/bin/python

import re

class ShortScore():
    """
    Export from shortscore to lilypond.
    Simple import from ly file.
    """
    def __init__(self, lyfile):
        self.unit = '1'
        self.lyfile = lyfile
        glob, parts = self.getPartNamesFromLy()
        self.parts = parts
        self.initScore()
        if glob:
            self.score[glob] = []
            self.glob = glob

    def initScore(self):
        self.score = {}
        for p in self.parts:
            self.score[p] = []

    def getPartNamesFromLy(self):
        with open(self.lyfile) as r:
            text = r.read()
        parts = []
        parts = re.findall(r"(\w+)\s*=\s*(?:\\\w+\s*\w+[',]*\s*)?{", text)
        globMatch = re.search(r"\\new Devnull\s*\{?\s*\\(\w+)", text)
        if globMatch:
            glob = globMatch.group(1)
            parts.remove(glob)
        else:
            glob = ''
        return glob, parts

    def parseLyGlob(self, glob):
        globDict = {}
        for g in glob.split("\n"):
            m = re.search(r"\\time\s*([\w\W]+)\b", g)
            if m:
                globDict['m'] = timesign = m.group(1)
            t = re.search(r"\\tempo\s*([\w\W]+)\b", g)
            if t:
                globDict['t'] = t.group(1)
            rm = re.search(r"\\mark\s*([\w\W]+)\b", g)
            if rm:
                mark = rm.group(1)
                if mark == r'\default':
                    globDict['rm'] = 'd'
                else:
                    globDict['rm'] = mark
            if 's' in g:
                for spacerRest in g.split():
                    spacerRest = spacerRest.replace('s', '')
                    sprList = spacerRest.split('*')
                    chains = len(sprList)
                    if chains == 1:
                        unit = sprList[0]
                        mult = 1
                    else:
                        unit, mult = tuple(sprList[:2])
                        from fractions import Fraction
                        if '.' not in unit:
                            if Fraction(timesign) == Fraction(int(mult), int(unit)):
                                unit = unit + '*' + mult
                                mult = 1
                        mult = int(mult)
                        if chains > 2:
                            for m in sprList[2:]:
                                mult *= int(m)
                    if globDict:
                        globDict['u'] = unit
                        self.score[self.glob].append(globDict)
                        globDict = {}
                        mult -= 1
                    self.score[self.glob] += [''] * mult

    def getBracketPositions(self, text):
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

    def getPartContentFromLy(self, partname):
        with open(self.lyfile) as r:
            text = r.read()
        pos = text.find(partname + ' =')
        if pos:
            text = text[pos:]
            start, end = self.getBracketPositions(text)
            return text[start + 1:end - 1]

    def replaceLyPartContent(self, partname, newContent):
        with open(self.lyfile) as r:
            text = r.read()
        pos = text.find(partname + ' =')
        if pos:
            slice = text[pos:]
            start, end = self.getBracketPositions(slice)
            slice = slice[:start + 1] + "\n" + newContent + "\n" + slice[end:]
            text = text[:pos] + slice
        with open(self.lyfile, "w") as w:
            w.write(text)

    def ly2shortScore(self, text):
        text = re.sub(r'\\tuplet\s*(\d+)/(\d+)\s*(\d*)\s*\{([^\}]+)}', r'[\g<4>]:\g<1>\\\g<2>:\g<3>', text)
        text = re.sub(r'(\]:\d+\\\d+):\s', r'\g<1> ', text)
        text = re.sub(r'\\(?:grace|acciaccatura)\s*([a-gis]+\d*)', r'\g<1>:g', text)
        text = re.sub(r'\\(?:grace|acciaccatura)\s*\{([^\}]+)}', r'[\g<1>]:g', text)
        text = re.sub(r'([>a-gis\d])\s*\\glissando[\(\s]*(\w+)\b\s*\)?', r'\g<1>:gl:\g<2>', text)
        text = re.sub(r'\\([mpf]+)\b', r':\g<1>', text)
        return text

    def handleRests(self, partname, bar):
        words = bar.split()
        for i, w in enumerate(words):
            if 'R' in w or 's' in w:
                w = w.replace('R', '')
                w = w.replace('s', '')
                n = w.split('*')
                compare = 2 if n[0] > self.unit else 1
                if len(n) > compare:
                    r = int(n[-1])
                else:
                    r = 1
                self.score[partname] += [''] * r
                del words[i]
        return " ".join(words)

    def parseLyPart(self, partname, part):
        for b in part.split("|"):
            b = self.handleRests(partname, b)
            b = self.ly2shortScore(b)
            if b.strip():
                self.score[partname].append(b.strip())

    def readLyVars(self):
        self.initScore()
        if self.glob:
            self.score[self.glob] = []
            self.parseLyGlob(self.getPartContentFromLy(self.glob))
        else:
            self.glob = "Glob"
            self.score[self.glob] = []
        max = 0
        for part in self.parts:
            self.parseLyPart(part, self.getPartContentFromLy(part))
            if len(self.score[part]) > max:
                max = len(self.score[part])
        if len(self.score[self.glob]) < max:
            r = max - len(self.score[self.glob])
            self.score[self.glob] += [''] * r
        self.setBarnrInGlob()

    def setBarnrInGlob(self):
        for barnr, globDict in enumerate(self.score[self.glob]):
            if globDict:
                globDict['barnr'] = barnr

    def createPartDefFromParts(self, shortScoreFile):
        with open(shortScoreFile) as r:
            text = r.read()
        # Read part definition
        try:
            partDef, ssc = tuple(text.split("@@@"))
        except ValueError:
            ssc = text
        partDefList = []
        for p in self.parts:
            partDefList.append(p + " =")
        partDef = "\n".join(partDefList)
        with open(shortScoreFile, "w") as w:
            w.write(partDef)
            w.write("\n@@@\n")
            w.write(ssc)

    def getShortScoreFromFile(self, shortScoreFile):
        try:
            with open(shortScoreFile) as r:
                text = r.read()
        except IOError:
            return False
        # Read part definition
        try:
            partDef, ssc = tuple(text.split("@@@"))
        except ValueError:
            partDef = ''
            ssc = text
        return partDef, ssc

    def readPartDef(self, partDef, flipped=True):
        partDefDict = {}
        for l in partDef.split("\n"):
            if l.strip():
                partname, shortname = tuple(l.split("="))
                if flipped:
                    partDefDict[partname.strip()] = shortname.strip()
                else:
                    partDefDict[shortname.strip()] = partname.strip()
        return partDefDict

    def readShortScore(self, shortScoreFile):
        self.initScore()
        if not self.glob:
            self.glob = "Glob"
        self.score[self.glob] = []
        # Get scortcore
        partDef, ssc = self.getShortScoreFromFile(shortScoreFile)
        partDefDict = self.readPartDef(partDef, False)
        # Read shortscore
        bars = ssc.split("|")
        for barnr, b in enumerate(bars):
            if not b.strip():
                continue
            # Add empty bar to each part
            for k in self.score:
                self.score[k].append('')
            if '@' in b:
                glob, b = tuple(b.split("@"))
                self.score[self.glob][-1] = self.parseGlobalData(glob, barnr)
            parts = b.split("/")

            for p in parts:
                if not p.strip():
                    continue
                data = p.split("::")
                try:
                    parts = data[0].strip()
                    music = data[1].strip()
                except IndexError:
                    print(data)
                partList = [p.strip() for p in parts.split(",")]
                if parts.strip().startswith('^'):
                    partMusic = self.explodeChords(music, len(partList))
                    partList[0] = partList[0][1:]
                else:
                    partMusic = [music] * len(partList)
                for pnr, partname in enumerate(partList):
                    try:
                        if partname in partDefDict:
                            partname = partDefDict[partname]
                        self.score[partname][-1] = partMusic[pnr]
                    except KeyError:
                        print("Error: " + partname + " not found in score!")

    def explodeChords(self, music, nrOfParts):
        parts = [''] * nrOfParts
        start = 0
        for n, t in enumerate(music):
            if t == '<':
                parts = [p + music[start:n] for p in parts]
                start = n + 1
            elif t == '>':
                try:
                    dura = music[n + 1:].split()[0]
                except IndexError:
                    dura = ''
                if not dura.isdigit():
                    dura = ''
                for i, c in enumerate(reversed(music[start:n].split())):
                    parts[i] += c + dura
                start = n + 1 + len(dura)
        return [p + music[start:] for p in parts]

    def parseGlobalData(self, glob, barnr):
        globDict = {}
        globDict['barnr'] = barnr
        for data in glob.split(","):
            data = data.strip()
            if data:
                key, val = tuple(data.split(":"))
                globDict[key] = val
        if 'u' in globDict:
            self.unit = globDict['u']
        else:
            globDict['u'] = self.unit
        return globDict

    def globalDataToStr(self, globDict):
        globList = []
        for key in globDict:
            if key != 'barnr': # Do not write out bar number
                globList.append(":".join([key, globDict[key]]))
        return ",".join(globList)

    def getPartsFromPartDef(self, partDefDict):
        parts = []
        for p in self.parts:
            if p in partDefDict:
                parts.append(partDefDict[p])
            else:
                parts.append(p)
        return parts

    def writeToShortScoreFile(self, shortScoreFile):
        # Read part definition
        partDef, ssc = self.getShortScoreFromFile(shortScoreFile)
        partDefDict = self.readPartDef(partDef)
        # Write to file
        with open(shortScoreFile, "w") as w:
            w.write(partDef)
            w.write("@@@\n")
            for barnr, bar in enumerate(self.score[self.glob]):
                if bar:
                    w.write(self.globalDataToStr(bar) + "@\n")
                barDict = {}
                for part in self.parts:
                    if part in partDefDict:
                        partname = partDefDict[part]
                    else:
                        partname = part
                    try:
                        if self.score[part][barnr]:
                            # Use music as key
                            key = self.score[part][barnr]
                            if key in barDict:
                                barDict[key].append(partname)
                            else:
                                barDict[key] = [partname]
                    except IndexError:
                        pass
                # write bar
                mo = []
                for m in barDict:
                    mo.append(",".join(barDict[m]) + ":: " + m)
                w.write(" / ".join(mo))
                w.write(" |\n")

    def outputGlobalDataToLy(self, globDict):
        output = []
        if 'm' in globDict:
            output.append(r"\time " + globDict['m'])
        if 't' in globDict:
            output.append(r"\tempo " + globDict['t'])
        if 'k' in globDict:
            output.append(r"\key " + globDict['k'])
        if 'rm' in globDict:
            if globDict['rm'] == 'd':
                output.append(r"\mark \default")
            else:
                output.append(r"\mark " + globDict['rm'])
        if 'd' in globDict:
            self.applyGloballyToAllLyParts(":" + globDict['d'], globDict['barnr'])
        # Handle rests
        if 'u' in globDict:
            output.append("s" + globDict['u'] + "*")
        return "\n".join(output)

    def applyGloballyToAllLyParts(self, text, barnr, after=False):
        for p in self.parts:
            if after:
                self.score[p][barnr] += text
            music = self.score[p][barnr].split()
            if music:
                music[0] += text
                self.score[p][barnr] = " ".join(music)

    def shortScoreMusicToLy(self, text):
        text = re.sub(r'\[([^\]]+)\]:(\d+)\\(\d+):?(\d*)\b', r"\\tuplet \g<2>/\g<3> \g<4> {\g<1>}", text)
        text = re.sub(r'([a-gis\d>])\s*:gl:([\w\',]+)\b', r"\g<1> \\glissando( \g<2>)", text)
        text = re.sub(r'\b([a-gis\d]+):g', r"\\acciaccatura \g<1>", text)
        text = re.sub(r'\[([^\]]+)\]:g', r"\\acciaccatura {\g<1>}", text)
        text = re.sub(r':([mpf]+)\b', r"\\\g<1>", text)
        text = re.sub(r'\b([\w\.\',]+)\s*:pizz\b', r'\\instrumentSwitch "pizzstring" \g<1>', text)
        text = re.sub(r'\b([\w]+):(arco\w+)\b', r'\\instrumentSwitch "\g<2>" \g<1>', text)
        text = re.sub(r' +', ' ', text)
        return text

    def writeToLyFile(self):
        unit = '1'
        m = 0
        glob = ''
        for b in self.score[self.glob]:
            if b:
                if m:
                    glob += str(m) + "\n"
                glob += self.outputGlobalDataToLy(b)
                m = 1
            else:
                m += 1
        glob += str(m) + "\n"
        self.replaceLyPartContent(self.glob, glob)

        for part in self.parts:
            multibar = 0
            content = []
            for barnr, bar in enumerate(self.score[part]):
                if 'u' in self.score[self.glob][barnr]:
                    if unit and unit != self.score[self.glob][barnr]['u']:
                        if multibar:
                            content.append(restStr + str(multibar))
                            multibar = 0
                    unit = self.score[self.glob][barnr]['u']
                    restStr = 'R' + unit + '*'
                if bar:
                    if multibar:
                        content.append(restStr + str(multibar))
                        multibar = 0
                    # Some music
                    content.append(bar + " |")
                else:
                    multibar += 1
            if multibar:
                content.append(restStr + str(multibar))
            self.replaceLyPartContent(part, self.shortScoreMusicToLy("\n".join(content)))
