import collections

class RoundRobinList(collections.UserList):
    def __init__(self, initlist=None):
        super(RoundRobinList, self).__init__(initlist)
        self._iter_index = 0
        
    def __next__(self):
        if not self:
            raise StopIteration
        if self._iter_index >= len(self):
            self._iter_index = 0
        item = self[self._iter_index]
        self._iter_index += 1
        return item

    def __iter__(self):
        return self
