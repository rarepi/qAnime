import qa2_util


class Fastresume:
    def __init__(self, fastresume:bytes):
        self.TAG_DICT = 'd'
        self.TAG_SEPARATOR = ':'
        self.TAG_INT = 'i'
        self.TAG_LIST = 'l'
        self.TAG_END = 'e'

        self.fastresume = fastresume

        self.data = self.read_bencoded()[1]

    def rename_file(self, old:str, new:str):
        if not isinstance(old, str) or not isinstance(new, str):
            return  # TODO ERROR

        if "mapped_files" not in self.data.keys():
            self.data["mapped_files"] = []
        if not isinstance(self.data["mapped_files"], list):
            return  # TODO ERROR

        old = bytes(old, "utf-8")
        new = bytes(new, "utf-8")

        if old in self.data["mapped_files"]:
            qa2_util.debug("Found", old, "in Fastresume, replacing...", level=2)
            self.data["mapped_files"] = [x if x != old else new for x in self.data["mapped_files"]]
        else:
            self.data["mapped_files"].append(new)   # TODO assuming correct order, that's kinda bad but it works for now

    def rename_torrent(self, new:str):
        if isinstance(new, str):
            self.data["qBt-name"] = bytes(new, "utf-8")

    def edit_data(self, key:str, value):
        if isinstance(value, type(self.data[key])):
            self.data[key] = value
        else:
            pass    # TODO type error

    def write(self) -> bytearray:
        output = bytearray(bytes(self.TAG_DICT, "ascii"))
        for k, d in self.data.items():
            output += bytes(str(len(k)), "ascii") \
                      + bytes(self.TAG_SEPARATOR, "ascii") \
                      + bytes(k, "ascii")
            output += self.unpack_data(d)

        output += bytes(self.TAG_END, "ascii")
        return output

    def unpack_data(self, item) -> bytearray:
        output = bytearray()

        if isinstance(item, int):
            output += bytes(self.TAG_INT, "ascii") \
                      + bytes(str(item), "ascii") \
                      + bytes(self.TAG_END, "ascii")
        elif isinstance(item, bytes):
            output += bytes(str(len(item)), "ascii") \
                      + bytes(self.TAG_SEPARATOR, "ascii") \
                      + item
        elif isinstance(item, list):
            output += bytes(self.TAG_LIST, "ascii")
            for element in item:
                output += self.unpack_data(element)
            output += bytes(self.TAG_END, "ascii")
        return output

    def read_bencoded(self, idx=0):
        if chr(self.fastresume[idx]) == self.TAG_DICT:
            data = {}
            idx += 1

            while chr(self.fastresume[idx]) != self.TAG_END:
                # key
                if not chr(self.fastresume[idx]).isdigit():
                    # TODO This happened once when no debug message was implemented.
                    #  Then it didn't ever happen again, even on the same torrent. No idea why.
                    qa2_util.debug("Invalid Key detected at index", idx, "\nExpected Integer, got", "'" + chr(self.fastresume[idx]) + "'",
                                   "\nFull Fastresume: ", self.fastresume, level=0)
                    return None, None  # TODO ERROR
                idx_separator = self.fastresume.index(bytes(self.TAG_SEPARATOR, "ascii"), idx)
                length = int(self.fastresume[idx:idx_separator])
                idx = idx_separator + 1
                key = self.fastresume[idx:idx + length].decode("utf-8")
                idx += length

                # value
                idx, value = self.read_bencoded(idx)
                data[key] = value
            return idx, data

        elif chr(self.fastresume[idx]) == self.TAG_LIST:     # data is list
            idx += 1
            data = []
            while chr(self.fastresume[idx]) != self.TAG_END:
                idx, value = self.read_bencoded(idx)
                data.append(value)
            idx += 1
            return idx, data
        elif chr(self.fastresume[idx]) == self.TAG_INT:      # data is int
            idx += 1
            idx_end = self.fastresume.index(bytes(self.TAG_END, "ascii"), idx)
            data = int(self.fastresume[idx:idx_end])  #
            idx = idx_end + 1
            return idx, data
        elif chr(self.fastresume[idx]).isdigit():            # data is bytes
            idx_separator = self.fastresume.index(bytes(self.TAG_SEPARATOR, "ascii"), idx)
            length = int(self.fastresume[idx:idx_separator])
            idx = idx_separator + 1
            data = self.fastresume[idx:idx + length]
            idx += length
            return idx, data
        else:
            print("Got", chr(self.fastresume[idx]))
            return None, None    # TODO ERROR