import sys
import requests
from enum import Enum
import json
import pymongo

# class that is used as enumarator for input processing states

class InputStatus(Enum):
    NotProcessed = 0
    InProgress = 1
    Finished = 2


# global variables

API_KEY = "8f0d9811"

class Global_Vars:
    movieTitles = []
    rating = -1
    genre = "noGenre"

# global functions

def loadSearchCriteria(arguments, argsNum):
    try:
        if (argsNum == 2):
            raise Exception()
    except:
        print('Command line arguments error: Movie title/s has not been given!')
        exit()

    movieInput = InputStatus.NotProcessed
    ratingsInput = InputStatus.NotProcessed
    genreInput = InputStatus.NotProcessed

    for i in range(argsNum):
        if (i == 0):
            continue

        arg = arguments[i]
        
        match arg:
            case '-mt':
                if (movieInput == InputStatus.NotProcessed):
                    movieInput = InputStatus.InProgress
                else:
                    print("Command line arguments error: argument -mt stated multiple times!")
                    exit()
            case '-rt':
                if (ratingsInput == InputStatus.NotProcessed and len(Global_Vars.movieTitles) > 0):
                    ratingsInput = InputStatus.InProgress
                    movieInput = InputStatus.Finished
                elif (ratingsInput == InputStatus.NotProcessed and len(Global_Vars.movieTitles) == 0):
                    print('Command line arguments error: Movie title/s has not been given!')
                    exit()
                else:
                    print("Command line arguments error: argument -rt stated multiple times!")
                    exit()
            case '-g':
                if (genreInput == InputStatus.NotProcessed and ratingsInput != InputStatus.InProgress):
                    genreInput = InputStatus.InProgress
                    movieInput = InputStatus.Finished
                elif (genreInput == InputStatus.NotProcessed and ratingsInput == InputStatus.InProgress):
                    print("Command line arguments error: no rating given after -rt argument!")
                    exit()               
                else:
                    print("Command line arguments error: argument -g stated multiple times!")
                    exit()
            case _:
                if (movieInput == InputStatus.InProgress):
                    Global_Vars.movieTitles.append(arguments[i])
                elif (ratingsInput == InputStatus.InProgress):
                    try:
                        Global_Vars.rating = float(arguments[i])
                    except ValueError:
                        print("Command line arguments error: rating must be a number!")
                        exit()
                    ratingsInput = InputStatus.Finished
                elif (genreInput == InputStatus.InProgress):
                    Global_Vars.genre = arguments[i]
                    genreInput = InputStatus.Finished
                else:
                    print("Command line arguments error: rating or genre has multiple values given!")
                    exit()

def loadMovieInformation():
    info = requests.get('http://www.omdbapi.com/?apikey='+API_KEY+'&t='+movie).json()
    if (info["Response"] == 'False'):
        info = None
    return info


def checkTheCriteria(info):
    genres = info['Genre'].split(',')
    for i in range(len(genres)):
        if (i > 0):
            genres[i] = genres[i][1:]

    ratingCriteriaPassed = False
    if (Global_Vars.rating == -1 or float(info['imdbRating']) < Global_Vars.rating):
        ratingCriteriaPassed = True

    genreCriteriaPassed = False
    if (Global_Vars.genre == "noGenre" or Global_Vars.genre in genres):
        genreCriteriaPassed = True

    return ratingCriteriaPassed and genreCriteriaPassed

def writeOutput(moviesInfo):
    open('output.txt', 'w').close()
    f = open("output.txt", "a")

    for movie in moviesInfo:
        f.write(json.dumps(movie))
        f.write("\n")

    f.close()  

# main program

argsNum = len(sys.argv)
loadSearchCriteria(sys.argv, argsNum)

moviesInfo = [] # list of all movies that wil be written to output file

myclient = pymongo.MongoClient("mongodb://localhost:27017/") # connect to mongodb

for movie in Global_Vars.movieTitles:
    info = loadMovieInformation()

    if info != None and checkTheCriteria(info):
        moviesInfo.append(info)

writeOutput(moviesInfo)