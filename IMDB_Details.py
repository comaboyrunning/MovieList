#!/usr/bin/env python

"""Get the rating of a movie on IMDB."""

# ImdbRating
# Laszlo Szathmary, 2011 (jabba.laci@gmail.com)
#
# Project's home page: 
# https://pythonadventures.wordpress.com/2011/03/25/get-the-imdb-rating-of-a-movie/
#
# Version: 0.2 
# Date:    2011-03-29 (yyyy-mm-dd)
#
# Inspired by the script of Rag Sagar:
# https://ragsagar.wordpress.com/2010/11/20/python-script-to-find-imdb-rating/
#
# This free software is copyleft licensed under the same terms as Python, or,
# at your option, under version 2 of the GPL license.

import sys
import urllib
import urlparse
import os
import re
import shutil
import pyodbc
import time

from mechanize import Browser
from BeautifulSoup import BeautifulSoup

class MyOpener(urllib.FancyURLopener):
    """Tricking web servers."""
    version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'

class ImdbRating:
    """Get the rating of a movie."""
    # title of the movie
    title = None
    # IMDB URL of the movie
    url = None
    # IMDB rating of the movie
    rating = None
    # Did we find a result?
    found = False
    
    # constant
    BASE_URL = 'http://www.imdb.com'
    
    def __init__(self, title):
        self.title = title
        self._process()
        
    def _process(self):
        """Start the work."""
        movie = '+'.join(self.title.split())
        br = Browser()
        url = "%s/find?s=tt&q=%s" % (self.BASE_URL, movie)
        br.open(url)

        if re.search(r'/title/tt.*', br.geturl()):
            self.url = "%s://%s%s" % urlparse.urlparse(br.geturl())[:3]
            soup = BeautifulSoup( MyOpener().open(url).read() )
        else:
            link = br.find_link(url_regex = re.compile(r'/title/tt.*'))
            res = br.follow_link(link)
            self.url = urlparse.urljoin(self.BASE_URL, link.url)
            soup = BeautifulSoup(res.read())

        try:
            self.title = soup.find('h1').contents[0].strip()
            for span in soup.findAll('span'):
                if span.has_key('itemprop') and span['itemprop'] == 'ratingValue':
                    self.rating = span.contents[0]
                    break
            self.found = True
        except:
            pass

# class ImdbRating

def insert_sql(sqlserver, username, password, databasename, tablename,moviepath, moviefilename,moviename,movieyear,moviefiletype,imdbrating):
    cnxn_string = 'DSN=%s;DATABASE=%s;UID=%s;PWD=%s' % (sqlserver, databasename, username, password)
    cnxn = pyodbc.connect(cnxn_string)
    cursor = cnxn.cursor()
    try:
        sql = "INSERT INTO [%s].[dbo].[%s] VALUES ('%s','%s','%s','%s','%s','%s')" % (databasename, tablename, moviepath, moviefilename,moviename,movieyear,moviefiletype,imdbrating)
        #print sql
        cursor.execute(sql)
        cnxn.commit()
        cursor.close()
    except Exception as e:
        sql = "INSERT INTO [%s].[dbo].[%s] VALUES ('%s','%s','%s','%s','%s','%s')" % (databasename, tablename, moviepath, moviefilename,moviename,movieyear,moviefiletype,"-1")
        print "Error with: "+moviefilename,e
        pass

def clear_temp_dir(sqlserver, username, password, databasename, tablename):
    cnxn_string = 'DSN=%s;DATABASE=%s;UID=%s;PWD=%s' % (sqlserver, databasename, username, password)
    cnxn = pyodbc.connect(cnxn_string)
    cursor = cnxn.cursor()
    sql = "DELETE FROM [%s].[dbo].[%s]" % (databasename,tablename)
    cursor.execute(sql)
    cnxn.commit()
    cursor.close()

def list_movie_directory(moviepath):
    SourceFiles = os.listdir(moviepath)
    SourceFiles.sort()
    #insert_sql(sqlserver, username, password, databasename, tablename,moviepath, moviedata)
    for moviefilename in SourceFiles:
        movie_details = re.findall('[^()]+', moviefilename)
        #print moviefilename, movie_details[0].strip(), movie_details[1].strip(),movie_details[2].strip()
        try:
            ##movie_string = "%s (%s)" % (movie_details[0].strip(),movie_details[1].strip())
            ##imdb = ImdbRating(movie_string)
            #insert_sql("SQLServer", "sa", "sa1", "Movies","movie_raw_list",moviepath,moviefilename, movie_details[0].strip(), movie_details[1].strip(),movie_details[2].strip(),imdb.rating)
            insert_sql("SQLServer", "sa", "sa1", "Movies","movie_raw_list",moviepath,moviefilename, movie_details[0].strip(), movie_details[1].strip(),movie_details[2].strip(),"-1")
            #time.sleep(5)
        except Exception as e:
            print "Error with: "+moviefilename,e
            pass


def list_movies_no_rating():
    cnxn_string = 'DSN=SQLServer;DATABASE=Movies;UID=sa;PWD=sa1'
    cnxn = pyodbc.connect(cnxn_string)
    cursor = cnxn.cursor()
    sql = "select * from film_needs_rating"
    cursor.execute(sql)
    rows = cursor.fetchall()
    listbmu = rows
    return listbmu


if __name__ == "__main__":
    #moviepath = 'H:\Movies'
    #moviepath = 'H:\Movies\HighRating'
    #SourceFiles = os.listdir(moviepath)
    #SourceFiles.sort()
    #MovieToKeep = []
    #MovieToMove =[]
    #print SourceFiles

    clear_temp_dir("SQLServer", "sa", "sa1", "Movies","movie_raw_list")

    moviedir = ['H:\Movies', 'Z:\Films']
    for each_movie_dir in moviedir:
        list_movie_directory(each_movie_dir)




    #listbmu = list_movies_no_rating()
    for x in list_movies_no_rating():
        movie_string = "%s (%s)" % (x[2].strip(),x[3].strip())
        imdb = ImdbRating(movie_string)
        print movie_string, imdb.rating

        try:
            cnxn_string = 'DSN=SQLServer;DATABASE=Movies;UID=sa;PWD=sa1'
            cnxn = pyodbc.connect(cnxn_string)
            cursor = cnxn.cursor()
            sql = """INSERT INTO movie_imdb (movie_path,movie_filename,movie_name,movie_year,movie_filetype,movie_rating) values ('%s','%s','%s','%s','%s','%s')""" % (x[0],x[1],x[2],x[3],x[4],float(imdb.rating))

            #print sql

            cursor.execute(sql)
            cnxn.commit()
            cursor.close()
            time.sleep(10)
        except Exception as e:
            print e
            pass


    for MovieName in SourceFiles:
        try:
            print os.path.splitext(MovieName)[0]
            imdb = ImdbRating(os.path.splitext(MovieName)[0])

            movie_details = re.findall('[^()]+', MovieName)
            #print movie_details[0].strip(), movie_details[1].strip(),movie_details[2].strip(),imdb.rating
            #print MovieName.split(".")[0]+'\t'+ MovieName.split(".")[1]+'\t'+imdb.rating
            if imdb.found and float(imdb.rating) >= 7:

                #sourceDir = "Z:\Films"
                #targetDir = "Z:\Films\Move"

                sourceDir = "H:\Movies"
                targetDir = "H:\Movies\HighRating"
                sourcename = os.path.join(sourceDir,MovieName)
                destpath = os.path.join(targetDir,MovieName)
                shutil.move(sourcename,destpath)
                print "Moved : "+MovieName+'\t'+imdb.rating
        except Exception as e:             
            print "Error with: "+MovieName, e
            pass
