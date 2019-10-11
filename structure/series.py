from numbers import Number

class Series(object):
    """Series"""
    def __init__(self, tvdbid, title):
        self.tvdbid = tvdbid
        self.title = title
        self.pattern_sets = {}
    
    def addPattern(self, season, p1, p2):
        self.pattern_sets.setdefault(season, []).append((p1, p2))
    def getPatternSets(self, season=None):
        if season is None:
            return self.pattern_sets
        else:
            return self.pattern_sets[season]