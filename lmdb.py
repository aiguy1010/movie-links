from movie import *
import requests
import json

apiUrl = 'https://www.omdbapi.com/?'

class LMDb(object):
    def __init__(self, filename=None, movies=[]):
        self.movies = movies
        self.filename = filename
        self.titleRegistry = []

        if self.filename:
            self.load()


    def load(self, filename=None):
        if not filename:
            if self.filename:
                self.load(self.filename)
                return
            raise(Exception('Linker object not associated with a file!'))

        self.movies = []
        self.titleRegistry = []

        text = open(filename, 'r').read()
        for line in text.split('\n'):
            if len(line.strip()) == 0:
                continue
            title, csActors = line.split('::')
            cast = csActors.split(',')
            self.add( Movie(title, cast) )


    def save(self, filename=None):
        if not filename:
            if self.filename:
                self.save(self.filename)
                return
            raise(Exception('Linker object not associated with a file!'))

        f = open(filename, 'w')
        for movie in self.movies:
            line = movie.title + '::'
            for actor in movie.cast:
                line += actor + ','
            line = line[:-1]
            f.write(line + '\n')


    def delete(self, title):
        delMovie = None
        for movie in self.movies:
            if movie.title == title:
                delMovie = movie
                break
        if delMovie == None:
            raise(Exception('Could not find movie to delete.'))
        self.movies.remove(delMovie)
        self.titleRegistry.remove(title)


    def display(self):
        for movie in self.movies:
            print(movie)
            for actor in movie.cast:
                print('  '+actor)
            print('')

    def download(self, title, actorCount=5):
        # Pull the data from OMDb
        words = title.strip().split()
        titleQuary = ''
        for word in words:
            titleQuary += word + '+'
        titleQuary = titleQuary[:-1]
        requestUrl= apiUrl + 't=' + titleQuary + '&r=json'
        response = requests.get( requestUrl )
        data = json.loads(response.text)

        actors=        data['Actors'].split(', ')
        officialTitle= data['Title']
        year=          data['Year']

        self.add( Movie(officialTitle, actors) )

        return officialTitle, year


    def add(self, movie):
        if movie.title in self.titleRegistry:
            return False
        self.movies.append(movie)
        self.titleRegistry.append(movie.title)
        self.sort()
        return True


    def sort(self):
        ignore = ['the', 'a']
        self.movies.sort( key=lambda movie: movie.title.lower() if movie.title.lower().split()[0] not in ignore else ' '.join(movie.title.lower().split()[1:]) )
        self.titleRegistry.sort( key=lambda title: title.lower() if title.lower().split()[0] not in ignore else ' '.join(title.lower().split()[1:]) )
