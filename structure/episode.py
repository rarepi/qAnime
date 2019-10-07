from .series import Series
import numbers

class Episode:
    """Episode"""
    def __init__(self, series, season, absolute, episodic, title):
        self.series = series
        self.season = season
        self.absolute = absolute
        self.episodic = episodic
        self.title = title