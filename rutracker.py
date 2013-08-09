#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2013, Ivan Lalashkov.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import optparse, urllib, urllib2, cookielib, os, re, Cookie, ConfigParser, sys

_SCRIPT_PATH = os.path.realpath(__file__)

class Configuration:
    __config = None

    def __init__(self):
        self.__config = ConfigParser.ConfigParser()
        if not os.path.exists(self._getConfigPath()):
            self.__config.add_section('user')
            self.__config.add_section('server')
            self.__config.add_section('script')
            self.__config.set('user', 'username', '')
            self.__config.set('user', 'password', '')
            self.__config.set('server', 'host', 'rutracker.org')
            self.__config.set('server', 'home_page', '/forum/index.php')
            self.__config.set('server', 'login_page', '/forum/login.php')
            self.__config.set('server', 'download_page', '/forum/dl.php?t=%s')
            self.__config.set('server', 'login_prefix', 'login.')
            self.__config.set('server', 'download_prefix', 'dl.')
            self.__config.set('server', 'download_cookie', 'bb_dl')
            self.__config.set('server', 'topic_page', '/forum/viewtopic.php?t=%s')

            self.__config.set('script', 'cookie_file', 'cookies.txt')
            self.__config.set('script', 'torrents_dir', '.')
            self.__config.set('script', 'user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_7)')

            self.save()
        else:
            self.__config.read(self._getConfigPath())

    def get(self, section, name):
        return self.__config.get(section, name)
    
    def set(self, section, name, value):
        self.__config.set(section, name, value)

    def save(self):
        with open(self._getConfigPath(), 'wb+') as configfile:
            self.__config.write(configfile)

    def getConfigParser(self):
        return self.__config

    def _getConfigPath(self):
        return os.path.join(os.path.dirname(_SCRIPT_PATH), "config.ini");

    def reload(self):
        self.__config.read(self._getConfigPath())


class Tracker:
    __config = None
    __opener = None

    def __init__(self, config = None):
        if config is None:
            self.__config = Configuration()
        else:
            self.__config = config

        self.__cookieJar = cookielib.MozillaCookieJar(self.__config.get('script', 'cookie_file'))
        if os.path.exists(self.__config.get('script', 'cookie_file')):
            self.__cookieJar.load()

        self.__opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(debuglevel=0),
            urllib2.HTTPCookieProcessor(self.__cookieJar)
        )

        self.__opener.addheaders = [("User-Agent", self.__config.get('script', 'user_agent'))]

        
    def getConfig(self):
        return self.__config


    def iterate(self, topicId = None, inputFile = None):
        if not topicId is None:
            self.login()
            self.download(topicId)

        if not inputFile is None:
            topics = self._parseInputFile(inputFile)

            if len(topics) > 0:
                for topic in topics:
                    self.login()
                    self.download(topic)

    def _parseInputFile(self, file):
        f = open(file, "r")
        lines = f.readlines()
        non_decimal = re.compile(r'[^\d]+')
        f.close()

        compiledLines = []
        for line in lines:
            if non_decimal.sub('', line) != '':
                compiledLines.append(non_decimal.sub('', line))
        return compiledLines


    def _authCheck(self, content):
        if re.findall(r"action.*?=.*?login\.php", content):
            return False
        return True

    def login(self):
        response = self.__opener.open("http://%s%s" % (self.__config.get('server', 'host'), self.__config.get('server', 'home_page')));
        self.__cookieJar.save();

        if (not self._authCheck(response.read())):
            print "Try to login"
            login_params = {
                "login_username": self.__config.get('user', 'username'),
                "login_password": self.__config.get('user', 'password'),
                "login": "%C2%F5%EE%E4"
            }
            response = self.__opener.open("http://%s%s%s" % (
                    self.__config.get('server', 'login_prefix'), 
                    self.__config.get('server', 'host'), 
                    self.__config.get('server', 'login_page')
                ), urllib.urlencode(login_params))
            self.__cookieJar.save();
            if not self._authCheck(response.read()):
                print "Could not login to server."
                sys.exit(2)

        return True

    def download(self, topicId):
        torrentName = "torrent[%s].torrent" % str(topicId);
        cookie = cookielib.Cookie(version=0, name=self.__config.get('server', 'download_cookie'),
                              value=str(topicId),
                              port=None, port_specified=False,
                              domain='.%s' % self.__config.get('server', 'host'),
                              domain_specified=True,
                              domain_initial_dot=True, path='/',
                              path_specified=True, secure=False,
                              expires=None, discard=True, comment=None,
                              comment_url=None, rest={'HttpOnly': None})
        self.__cookieJar.set_cookie(cookie)

        self.__opener.addheaders = [('Referer', 'http://%s%s' % (
            self.__config.get('server', 'host'), 
            self.__config.get('server', 'topic_page') % str(topicId))
        )]

        response = self.__opener.open("http://%s%s%s" % (
                self.__config.get('server', 'download_prefix'), 
                self.__config.get('server', 'host'), 
                self.__config.get('server', 'download_page') % str(topicId)
            ))
        torrentPath = self.__config.get('script', 'torrents_dir') + os.sep + torrentName
        tFile = open(torrentPath, 'wb')
        tFile.write(response.read())
        tFile.close()
        print "Torrent was saved as %s" % torrentPath


if __name__ == '__main__':
    try:
        print("\n\tRuTracker Downloader - Download torrent files from RuTracker\n\n");

        parser = optparse.OptionParser( usage = "Usage: %prog [options]\n\n" + 
                                                "EXAMPLE:\n" + 
                                                "\t%prog --topic topic_id --username yout-username --password your-password"
            )
        parser.add_option("-t", "--topic", action="store", dest="topic_id", default=None, help="Topic Id")
        parser.add_option("-u", "--username", action="store", dest="username", default=None, help="Your username")
        parser.add_option("-p", "--password", action="store", dest="password", default=None, help="Your password")
        parser.add_option("-i", "--input-file", action="store", dest="inputFile", default=None, help="File with topic ids")
        parser.add_option("-o", "--output-dir", action="store", dest="outputFolder", default=None, help="Output folder to store torrent files")

        (o,args) = parser.parse_args()

        tracker = Tracker()

        if (o.topic_id is None) and (o.inputFile is None):
            print "No topic Id specified."
        elif (o.password is None) and (tracker.getConfig().get('user', 'password') == ''):
            print "No password specified."
        elif (o.username is None) and (tracker.getConfig().get('user', 'username') == ''):
            print "No username specified."
        elif (not o.inputFile is None) and (not os.path.exists(o.inputFile)):
            print "input file does not exists or unaccessable."
        elif (not o.outputFolder is None) and (not os.path.exists(o.outputFolder)):
            print "Output folder does not exists or unaccessable."
        else:
            if not o.username is None:
                tracker.getConfig().getConfigParser().set('user', 'username', o.username)
            if not o.password is None:
                tracker.getConfig().getConfigParser().set('user', 'password', o.password)
            tracker.getConfig().save()
            if not o.outputFolder is None:
                tracker.getConfig().set('script', 'torrents_dir', o.outputFolder)

            tracker.iterate(o.topic_id, o.inputFile);

    except Exception as e:
        print str(e)
