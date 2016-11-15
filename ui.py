#!/usr/local/bin/python2
from linker import *
import os


savePath = 'defaultLMDb'
if not os.path.isfile(savePath):
    f=open(savePath, 'w')
    f.close()

myLMDb = LMDb(savePath)
linker = Linker(myLMDb)

lastQuestion=None
lastDownloadTitle = None

print('Welcome to Movie Linker v0.3!')
print('Type "help" for a list of available commands.')

while True:
    # Format input
    inputList = input('>').strip().split()
    if len(inputList)==0:
        continue
    command = inputList[0]
    argv = []
    if len(inputList) > 1:
        argv = inputList[1:]


    # Parse input
    if command == 'add':
        if len(argv) < 2:
            print('Command "add" requires arguments. Type "help" for additional info.')
            continue
        if argv[0] == 'movie':
            title = ' '.join(argv[1:])
            myLMDb.add( Movie(title) )
        elif argv[0] == 'actor':
            actor, title = ' '.join(argv[1:]).split(',')
            title = title.strip()
            actor = actor.strip()
            movieFound = False
            for movie in myLMDb.movies:
                if movie.title == title:
                    movieFound = True
                    if actor in movie.cast:
                        print('Movie already has actor. No action required.')
                        break
                    movie.cast.append(actor)
                    break
            if not movieFound:
                print('Unable to locate movie: '+title)
        else:
            print('"'+argv[0]+'": Not a recognized option. Type "help" for proper usage info.')
            continue
        linker.sync()
        continue



    if command == 'clear':
        os.system('cls' if os.name == 'nt' else 'clear')
        continue

    if command == 'help':
        print(open('help.txt', 'r').read())
        continue

    if command == 'delete':
        if len(argv) == 0:
            if lastDownloadTitle == None:
                print('No downloads yet this session. Please specify something to delete.')
                continue
            print('Deleting...\n'+lastDownloadTitle)
            myLMDb.delete(lastDownloadTitle)
            continue
        elif len(argv) == 1:
            print('Command "delete" requires additional arguments. Type "help" for syntax info.')
            continue

        if argv[0] == 'movie':
            try:
                title = ' '.join(argv[1:]).strip()
                myLMDb.delete(title)
            except:
                print('Could not find movie to delete. Make sure it is really in the')
                print('LMDb and check your spelling and capitalization.')
        elif argv[0] == 'actor':
            try:
                actor, title = ' '.join(argv[1:]).split(',')
                title = title.strip()
                actor = actor.strip()
                movieFound = False
                for movie in myLMDb.movies:
                    if movie.title == title:
                        movieFound = True
                        movie.delete(actor)
                if not movieFound:
                    print('Failed to locate specified movie. Make sure it is really in')
                    print('the LMDb and check your spelling and capitalization.')
            except:
                print('Failed to locate actor. Make sure that the specified actor is')
                print('in the specified movie and check your spelling and capitalization.')
        else:
            print('"'+argv[0]+'": Not a recognized option. Type "help" for proper usage info.')
            continue
        linker.sync()
        continue


    if command == 'done' or command == 'exit':
        break

    if command == 'display':
        myLMDb.display()
        continue

    if command == 'list':
        if len(argv) == 0:
            for title in myLMDb.titleRegistry:
                print(title)
        else:
            title = ' '.join(argv)
            if title not in linker.cast_d.keys():
                print('Unrecognized movie title. Check your spelling and capitolization.')
                continue
            else:
                for actor in linker.cast_d[title]:
                    print(actor)
        continue

    if command == 'download':
        if len(argv) == 0:
            print('Command "download" requires an argument. Type "help" for additional info.')
            continue
        try:
            actorCount=5
            if '-n' in argv:
                i = argv.index('-n')
                actorCount = int( argv[i+1] )
                argv= argv[:i]
            title = ' '.join(argv)

            downloadedTitle, year = myLMDb.download(title, actorCount)
            lastDownloadTitle = downloadedTitle
            print('Downloaded...')
            print('Title: ' + downloadedTitle)
            print(' Year: ' + year)
        except:
            print('And error occured while trying to download "'+title+'".')
            print('You may have better luck with a different spelling.')
        linker.sync()
        continue

    if command == 'generate':
        try:
            title1, title2 = lastQuestion = linker.makeQuestion()
            print(title1 + '\n|\n?\n|\n' + title2)
        except:
            print('Unable to generate Movie-Link. Try adding more movies to the Local')
            print('Movie Database.')
        continue

    if command == 'set':
        if argv[0] == 'savePath':
            savePath = argv[1]
            print('Variable "savePath" set to value "'+savePath+'"')
            continue

    if command == 'spoil':
        if lastQuestion == None:
            print('There is nothing to be spoiled yet. Type "generate" to\n')
            print('get yourself a spoilable question. You pathetic bastard.')
            continue
        solutions = linker.getLinks(*lastQuestion)
        for solution in solutions:
            print(solution)
        continue

    if command == 'save':
        myLMDb.save(savePath)
        continue

    if command == 'solve':
        rest = ' '.join(argv)
        try:
            title1, title2 = rest.split(',')
            title1 = title1.strip()
            title2 = title2.strip()
            if len(title1) == 0 or len(title2) == 0:
                raise Exception()
        except:
             print('Could not parse arguments. Type "help" for additional info.')
             continue
        try:
            solutions = linker.getLinks(title1, title2)
        except:
            print('Could not recognize one or more titles.')
            print('Please check your spelling and capitalization.')
            continue
        else:
            if len(solutions) == 0:
                print('No solutions found!')
                continue
            for solution in solutions:
                print(solution)
            continue

    if command == 'load':
        myLMDb.load(savePath)
        linker.sync()
        continue

    print('"'+command+'" is not a recognized command.\nType "help" for a list of available commands')
