#!/usr/bin/python

import re

class ShortScore():
    """
    Export from shortscore to lilypond.
    Simple import from ly file.
    """
    def __init__(self, lyfile):
        self.lyfile = lyfile
        glob, parts = self.getPartNamesFromLy()
        self.score = {}
        if glob:
            self.score[glob] = []
        self.glob = glob
        self.parts = parts
        for p in parts:
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
                globDict['m'] = m.group(1)
            t = re.search(r"\\tempo\s*([\w\W]+)\b", g)
            if t:
                globDict['t'] = t.group(1)
            restmatch = re.findall(r"s([\d\*\.]+?)(\d+)\b", g)
            if restmatch:
                globDict['u'] = restmatch[0][0][:-1]
                self.score[self.glob].append(globDict)
                globDict = {}
                rests = [int(r) for u, r in restmatch]
                rests[0] -= 1
                for r in rests:
                    if r:
                        self.score[self.glob] += [''] * r

    def getBracketPositions(self, text):
        stack = []
        start = False
        end = False
        for i, t in enumerate(text):
            if t == '{':
                if start:
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
        pos = text.find(partname)
        if pos:
            text = text[pos:]
            start, end = self.getBracketPositions(text)
            return text[start + 1:end - 1]

    def replacePartContent(self, partname, newContent):
        with open(self.lyfile) as r:
            text = r.read()
        pos = text.find(partname)
        if pos:
            slice = text[pos:]
            start, end = self.getBracketPositions(slice)
            slice = slice[:start + 1] + "\n" + newContent + "\n" + slice[end:]
            text = text[:pos] + slice
        with open(self.lyfile, "w") as w:
            w.write(text)

    def ly2shortScore(self, text):
        text = re.sub(r'\\tuplet\s*(\d+)/(\d+)\s*(\d*)\s*\{([^\}]+)}', r'[\g<4>]\g<1>:\g<2>:\g<3>', text)
        text = re.sub(r'(\]\d+:\d+):\s', r'\g<1> ', text)
        return text

    def parseLyPart(self, partname, part):
        for b in part.split("|"):
            # print(b)
            rests = [int(r) for r in re.findall(r"(?:R|s)[\d\*\.]+?(\d+)\b", b)]
            for r in rests:
                self.score[partname] += [''] * r
            b = re.sub(r"(?:R|s)[\d\*\.]+", '', b)
            b = self.ly2shortScore(b)
            if b.strip():
                self.score[partname].append(b.strip())

    def readLyVars(self):
        if self.glob:
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
        if not self.glob:
            self.glob = "Glob"
            self.score[self.glob] = []
        with open(shortScoreFile) as r:
            text = r.read()
        # Read part definition
        try:
            partDef, ssc = tuple(text.split("@@@"))
        except ValueError:
            partDef = ''
            ssc = text
        partDefDict = self.readPartDef(partDef, False)
        # Read shortscore
        bars = ssc.split("|")
        for b in bars:
            if not b.strip():
                continue
            # Add empty bar to each part
            for k in self.score:
                self.score[k].append('')
            if '@' in b:
                glob, b = tuple(b.split("@"))
                self.score[self.glob][-1] = self.parseGlobalData(glob)
            parts = b.split("/")

            for p in parts:
                if not p.strip():
                    continue
                data = p.split("::")
                try:
                    partnames = data[0].strip()
                    music = data[1].strip()
                except IndexError:
                    print(data)
                for partname in [p.strip() for p in partnames.split(",")]:
                    try:
                        if partname in partDefDict:
                            partname = partDefDict[partname]
                        self.score[partname][-1] = music
                    except KeyError:
                        print("Error: " + partname + " not found in score!")

    def parseGlobalData(self, glob):
        globDict = {}
        for data in glob.split(","):
            data = data.strip()
            if data:
                key, val = tuple(data.split(":"))
                globDict[key] = val
        return globDict

    def globalDataToStr(self, globDict):
        globList = []
        for key in globDict:
            globList.append(":".join([key, globDict[key]]))
        return ",".join(globList)

    def getPartsFromPartDef(self, partDefDict):
        print(partDefDict)
        parts = []
        for p in self.parts:
            if p in partDefDict:
                parts.append(partDefDict[p])
            else:
                parts.append(p)
        return parts

    def writeToShortScoreFile(self, shortScoreFile):
        # Read part definition
        with open(shortScoreFile) as r:
            text = r.read()
        try:
            partDef, ssc = tuple(text.split("@@@"))
        except ValueError:
            partDef = ''
        partDefDict = self.readPartDef(partDef)
        # Write to file
        with open(shortScoreFile, "w") as w:
            w.write(partDef)
            w.write("@@@\n")
            for barnr, bar in enumerate(self.score[self.glob]):
                if bar:
                    w.write(self.globalDataToStr(bar) + " @\n")
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
        if 'u' in globDict:
            output.append("s" + globDict['u'] + "*")
        return "\n".join(output)

    def shortScoreMusicToLy(self, text):
        text = re.sub(r'\[([^\]]+)\](\d+):(\d+):?(\d*)\b', r"\\tuplet \g<2>/\g<3> \g<4> {\g<1>}", text)
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
        self.replacePartContent(self.glob, glob)

        for part in self.parts:
            multibar = False
            content = []
            for barnr, bar in enumerate(self.score[part]):
                if 'u' in self.score[self.glob][barnr]:
                    unit = self.score[self.glob][barnr]['u']
                restStr = 'R' + unit + '*'
                if bar:
                    if multibar:
                        content.append(restStr + str(multibar))
                        multibar = False
                    # Some music
                    content.append(bar + " |")
                else:
                    if multibar:
                        multibar += 1
                    else:
                        multibar = 1
            if multibar:
                content.append(restStr + str(multibar))
            self.replacePartContent(part, self.shortScoreMusicToLy("\n".join(content)))
