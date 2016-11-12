class Movie(object):
    def __init__(self, title, cast=[]):
        self.title = title
        self.cast = cast

    def delete(self, actor):
        self.cast.remove(actor)

    def __str__(self):
        return self.title

    
