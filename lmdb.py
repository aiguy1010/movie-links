from movie import *
import urllib3
import re

resultMatcher = re.compile(r'<table class="findList">[\s\S]*?<td class="result_text">[\s\S]*?<a href="(.*?)" >')
titleMatcher = re.compile(r'<h1 class="header"> <span class="itemprop" itemprop="name">(.*?)<\/span>[\s]*<span class="nobr">\(<a href=".*?"[\s]>([0-9]{4})<\/a>')
starsSecMatcher = re.compile(r'<h4 class="inline">Stars:<\/h4>([\s\S]*?)See full cast and crew')
starMatcher = re.compile(r'itemprop="name">(.*?)<\/span>')
castSecMatcher = re.compile(r'<table class="cast_list">[\s\S]*?<\/table>')

actorMatcher = re.compile(r'<span class="itemprop" itemprop="name">(.*?)</span>')

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
        # Search
        words = title.strip().split()
        quary = ''
        for word in words:
            quary += word + '+'
        quary = quary[:-1]
        searchUrl='http://www.imdb.com/find?ref_=nv_sr_fn&q='+quary+'&s=all'
        searchPage = urllib3.urlopen(searchUrl).read()
        movieUrl = resultMatcher.search(searchPage).group(1)

        # Rip
        moviePage = urllib3.urlopen('http://www.imdb.com'+movieUrl).read()
        officialTitle, year = titleMatcher.search(moviePage).groups()

        starsSec = starsSecMatcher.search(moviePage).group(0)
        stars = starMatcher.findall(starsSec)[::-1]
        castSection = castSecMatcher.search(moviePage).group(0)
        cast = actorMatcher.findall(castSection)[::-1]

        # Add
        pickedActors = []
        picked = 0
        while picked < actorCount:
            if len(stars) > 0:
                pickedActors.append(stars.pop())
                picked += 1
                continue
            elif len(cast) > 0:
                actor = cast.pop()
                if actor not in pickedActors:
                    pickedActors.append(actor)
                    picked += 1
                continue
            else:
                break
        self.add( Movie(officialTitle, pickedActors) )

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
