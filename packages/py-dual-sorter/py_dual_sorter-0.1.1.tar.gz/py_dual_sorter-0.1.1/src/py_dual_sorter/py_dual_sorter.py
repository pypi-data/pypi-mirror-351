import json


# --------------------
## hold and access content with two keys
class PyDualSorter:
    # --------------------
    ## constructor
    def __init__(self):
        ## the content
        self._content = []

    # --------------------
    ## save content to json file
    #
    # @param path
    # @return None
    def save(self, path):
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(self._content, fp, indent=4)

    # --------------------
    ## load content from json file
    #
    # @param path      the path to the file to load
    # @param validate  (optional) check the content for unique left, right keys; default skip the check
    # @return None
    def load(self, path, validate=False):
        with open(path, 'r', encoding='utf-8') as fp:
            if not validate:
                self._content = json.load(fp)
                return

            j = json.load(fp)
            keys = {}
            duplicates = []
            for item in j:
                if item[0] in keys:
                    duplicates.append(item[0])
                else:
                    keys[item[0]] = 1
            if len(duplicates) > 0:
                raise Exception(f'duplicate left keys exist: {duplicates}')

            keys = {}
            duplicates = []
            for item in j:
                if item[1] in keys:
                    duplicates.append(item[1])
                else:
                    keys[item[1]] = 1
            if len(duplicates) > 0:
                raise Exception(f'duplicate right keys exist: {duplicates}')

            self._content = j

    # --------------------
    ## add a new entry to the content.
    #
    # @param left   the left key
    # @param right  the right key
    # @param info   (optional) additional content to hold; defaults to None
    # @return None
    def add(self, left, right, info=None):
        if self.is_left(left):
            raise Exception(f'duplicate left key: {left}')

        if self.is_right(right):
            raise Exception(f'duplicate right key: {right}')

        self._content.append((left, right, info))

    # --------------------
    ## perform a sorted iteration using the left key.
    # yields: left key, right key and info
    #
    # @return None
    def all_by_left(self):
        for item in sorted(self._content, key=lambda x: x[0]):
            yield item[0], item[1], item[2]

    # --------------------
    ## perform a sorted iteration using the right key
    # yields: left key, right key and info
    #
    # @return None
    def all_by_right(self):
        for item in sorted(self._content, key=lambda x: x[1]):
            yield item[0], item[1], item[2]

    # --------------------
    ## checks if the value given is a valid left key
    #
    # @param val   the value to check
    # @return True if val is a left key, False otherwise
    def is_left(self, val):
        for item in self._content:
            if item[0] == val:
                return True
        return False

    # --------------------
    ## checks if the value given is a valid right key
    #
    # @param val   the value to check
    # @return True if val is a right key, False otherwise
    def is_right(self, val):
        for item in self._content:
            if item[1] == val:
                return True
        return False

    # --------------------
    ## get the left key for the given right key
    #
    # @param right   the right key
    # @return if found, the left key, otherwise None
    def get_left(self, right):
        for item in self._content:
            if item[1] == right:
                return item[0]
        return None

    # --------------------
    ## get the right key for the given left key
    #
    # @param left   the left key
    # @return if found, the right key, otherwise None
    def get_right(self, left):
        for item in self._content:
            if item[0] == left:
                return item[1]
        return None

    # --------------------
    ## get the info given the left key
    #
    # @param left   the left key
    # @return if found, the associated info, otherwise None
    def info_by_left(self, left):
        for item in self._content:
            if item[0] == left:
                return item[2]
        return None

    # --------------------
    ## get the info given the right key
    #
    # @param right   the right key
    # @return if found, the associated info, otherwise None
    def info_by_right(self, right):
        for item in self._content:
            if item[1] == right:
                return item[2]
        return None
