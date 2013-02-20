#This class should not need persistant backing.

import heapq

class QueueEmptyError(Exception):
    pass


class ChallengeQueue(object):
    def __init__(self):
        self.queue = []

    def append(self, item, prio=0):
        #Set priority with prio, zero is highest
        heapq.heappush(self.queue, (prio, item))

    def pop(self):
        if not self.queue:
            raise QueueEmptyError
        else:
            return heapq.heappop(self.queue)[1]

    def __len__(self):
        return len(self.queue)
