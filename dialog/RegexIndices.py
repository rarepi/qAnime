import bisect

import qa2_util


class RegexIndices:
    def __init__(self):
        self.data = [(0,'s')]   # must stay sorted

    # Sorted insert of index data
    def insert(self, begin:int, end:int, char:chr):
        qa2_util.debug("Inserting regex index data:", begin, end, char, level=1)
        qa2_util.debug(self.data, level=1)
        if begin >= end:
            return  # TODO ERROR
        data_indices = [x[0] for x in self.data]        # list of all indices in data

        if end in data_indices:                         # check if new index already exists
            ins_idx = data_indices.index(end)
            if self.data[ins_idx][1] is char:           # if the following indices share our begin's char,
                self.data.pop(ins_idx)                  # this item becomes redundant, so remove it
                qa2_util.debug('-', end, char, level=1)
        else:
            next_char = max([x for x in self.data if x[0] < end])[1]    # character of highest-indexed item before end
            if next_char is not char:                   # no need to insert next char if it just stays the same as begin's char
                ins_idx = bisect.bisect_left(data_indices, end)         # find sorted insert position
                self.data.insert(ins_idx, (end, next_char))
                qa2_util.debug('add', end, next_char, 'at index', ins_idx, level=1)
        qa2_util.debug(self.data, level=1)

        previous_char = max([x for x in self.data if x[0] < begin])[1]  # character of highest-indexed item below begin
        if begin in data_indices:                                       # check if our index already exists in data set
            ins_idx = data_indices.index(begin)
            if previous_char is not char:                               # check if previous item would make the new one redundant
                self.data[ins_idx] = (begin, char)                          # if not, overwrite the char of the pre-existing item
                qa2_util.debug('set', ins_idx, '=', begin, char, level=1)
            else:                                                           # if previous item would cover ours
                self.data.pop(ins_idx)                                      # this one would become redundant data, so just remove it
                qa2_util.debug('-', begin, char, level=1)
        else:                                                           # insert our index as a new item
            if previous_char is not char:                               # only if not redundant
                ins_idx = bisect.bisect_left(data_indices, begin)       # find sorted insert position
                self.data.insert(ins_idx, (begin, char))
                qa2_util.debug('add', begin, char, 'at index', ins_idx, level=1)
            else:
                pass                                                    # previous item covers ours, no need to add it
        qa2_util.debug(self.data, level=1)

        self.data = [x for x in self.data if begin >= x[0] or x[0] >= end]  # drop any overwritten items
        qa2_util.debug(self.data, level=1)
        qa2_util.debug("---", level=1)