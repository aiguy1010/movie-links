from lmdb import *
import random

class Linker(object):
    def __init__(self, lmdb=None):
        if lmdb:
            self.lmdb = lmdb
        else:
            self.lmdb = LMDb()

        self.filmography_d = {}
        self.cast_d = {}

        self.sync()


    def sync(self):
        self.cast_d = {}
        for movie in self.lmdb.movies:
            self.cast_d[movie.title] = set(movie.cast)

        self.filmography_d = {}
        for movie in self.lmdb.movies:
            for actor in movie.cast:
                if not actor in self.filmography_d:
                    self.filmography_d[actor] = []
                self.filmography_d[actor].append(movie.title)
        for actor in self.filmography_d:
            self.filmography_d[actor] = set(self.filmography_d[actor])


    def getLinks(self, movie1, movie2):
        neighbors1 = self.getNeighbors(movie1)
        neighbors2 = self.getNeighbors(movie2)
        links = neighbors1 & neighbors2
        return links

    def getNeighbors(self, movie):
        neighbors = set()
        for actor in self.cast_d[movie]:
            neighbors = neighbors | self.filmography_d[actor]
        neighbors.remove(movie)
        return neighbors

    def makeQuestion(self, allowDirect=False):
        start = random.choice(list(self.cast_d.keys()))
        if len(self.getNeighbors(start)) == 0:
            return self.makeQuestion(allowDirect)
        middle = random.choice(list(self.getNeighbors(start)))
        endCandidates = self.getNeighbors(middle)
        endCandidates.remove(start)
        if len(endCandidates) == 0:
            return self.makeQuestion(allowDirect)
        end = random.choice(list(endCandidates))
        if not allowDirect:
            if len(self.cast_d[start] & self.cast_d[end]) != 0:
                start, end = self.makeQuestion(False)
        return start, end
        
    
