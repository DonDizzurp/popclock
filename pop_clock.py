## Digital clock with message and sound
## Evandro Flores - eof@eof.com.br
## Special thanks to:
## Guilherme Chapiewski - chapa@gc.blog.br
## The Knights who say Ni! - knights@whosay.ni

import pygame
from pygame.locals import *
import os
import time
from time import gmtime, strftime, sleep
import sys
import locale
import getopt
import urllib2
import re
from config import SIZES
from colors import Color


class PopClock (object):

    def __init__(self, options, args):
        pygame.init()
        self.init_time = time.time()

        resolution=None
        
        self.size = SIZES.get(resolution)
        if self.size is None:
            self.size = SIZES["640x480"]
        
        # If you don't have DejaVuSans font: use this file 
        # or 'sudo apt-get install mscoretruefont' or
        #self.bigfont = pygame.font.Font("DejaVuSans.ttf", 90)
        self.bigfont = pygame.font.SysFont("DejaVuSans", self.size.bigfont)
        self.mediumfont = pygame.font.SysFont("DejaVuSans", self.size.mediumfont)
        self.smallfont = pygame.font.SysFont("DejaVuSans", self.size.smallfont)
        self.tinyfont = pygame.font.SysFont("DejaVuSans", self.size.tinyfont)
    
        self.quit = False
        self.time = " -- : -- : -- "
        self.timedesc = "..."
        self.timecolor = Color.WHITE
        self.msgcolor = Color.WHITE
        self.bgcolor = Color.BLACK
        self.verbose = False
        self.timelimit = options.exitat
        self.message = ""
        self.timeline = False
        self.debug = options.debug
        self.alarm = options.alarm

        if self.debug:
            print "Options %s" % options

        if options.message:
            self.message = options.message

        if options.timeline:
            self.timeline = True
            self.wikinfo = WikiInfo()

        if options.fullscreen:
            self.screen = pygame.display.set_mode(self.size.screen, FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.size.screen)

        if options.soundfile:
            self.sound = pygame.mixer.Sound(options.soundfile)
            self.sound.play()

        pygame.display.set_caption("PopClock")

    def update(self):
        if ((time.time() - self.init_time)/60) >= self.timelimit:
            self.quit = True

        self.time = strftime(" %H: %M:%S ")
        self.timedesc = strftime(" %A, %d %B %Y")

        if self.msgcolor == Color.WHITE:
            self.msgcolor = Color.BLACK
        else:
            self.msgcolor = Color.WHITE

        if self.alarm:
            if self.bgcolor == Color.RED:
                self.bgcolor = Color.YELLOW
                self.msgcolor = Color.RED
                self.timecolor = Color.RED
            else:
                self.bgcolor = Color.RED
                self.msgcolor = Color.YELLOW
                self.timecolor = Color.YELLOW

        return

    def draw(self):
        self.screen.fill(self.bgcolor)

        msgrender = self.bigfont.render(self.message, True, self.msgcolor)
        msgpos = msgrender.get_rect()
        msgpos.centerx = self.screen.get_rect().centerx
        msgpos.centery = self.size.message_top
        self.screen.blit(msgrender, msgpos)

        timerender = self.bigfont.render(self.time, True, self.timecolor)
        timepos = timerender.get_rect()
        timepos.centerx = self.screen.get_rect().centerx
        timepos.centery = self.size.time_top
        self.screen.blit(timerender, timepos)

        timedescrender = self.smallfont.render(self.timedesc, True, self.timecolor)
        timedescpos = timedescrender.get_rect()
        timedescpos.centerx = self.screen.get_rect().centerx
        timedescpos.centery = self.size.time_desc_top
        self.screen.blit(timedescrender, timedescpos)

        if self.timeline:
            sprintrender = self.smallfont.render(self.wikinfo.sprint, True, Color.WHITE)
            sprintreder_pos = self.size.timeline_left, self.size.timeline_sprint_top
            self.screen.blit(sprintrender, sprintreder_pos)

            bgline_start = (self.size.timeline_left, self.size.timeline_linetop)
            bgline_size = (len(self.wikinfo.datelist)+1) * self.size.timeline_dayline
            bgline_end = (bgline_size, self.size.timeline_linetop)
            bgline_width = self.size.timeline_width
                                
            pygame.draw.line(self.screen, Color.GRAY, bgline_start, bgline_end, bgline_width)

            qtd=0
            pastdays=0
            today = strftime("%d %b")
            future = False

            for day in self.wikinfo.datelist:
                if (future):
                    datarender = self.tinyfont.render(day, True, Color.GRAY)
                else:
                    datarender = self.tinyfont.render(day, True, Color.WHITE)
                    pastdays+=1

                datapos = timedescrender.get_rect()
                datapos.x = self.size.timeline_left+((self.size.timeline_dayline+1)*qtd)
                datapos.y = self.size.timeline_datelist_top
                self.screen.blit(datarender, datapos)
                qtd+=1
                if day == today:
                    future = True

            progress_start = (self.size.timeline_left, self.size.timeline_linetop)
            progress_size = (self.size.timeline_left+(self.size.timeline_dayline*(pastdays)))
            progress_end = (progress_size, self.size.timeline_linetop)
            progress_width = self.size.timeline_width

            pygame.draw.line(self.screen, Color.RED, progress_start, progress_end, progress_width)

        pygame.display.flip()

    def run(self):
        while not self.quit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.quit = True
            self.update()
            self.draw()
            sleep(0.3)

#TODO: Make a plugin with WikiInfo 
class WikiInfo:

    def __init__(self):
        self.sprint = "Sprint XX"
        self.datelist = ['00 Ooo', '00 Ooo', '00 Ooo', '00 Ooo', '00 Ooo',
                         '00 Ooo', '00 Ooo', '00 Ooo', '00 Ooo', '00 Ooo']

        wiki = 'http://wiki.globoi.com/view'

        wiki_header = urllib2.urlopen('%s/A3/SprintAtual?cover=print'%wiki)
        html_header = wiki_header.read()
        current_sprint = re.compile("location.href='/A3/(.*)';").findall(html_header)
        if current_sprint:
            self.sprint = current_sprint[0].replace("A3Sprint", "Sprint ")

        wiki_current_sprint = '%s/A3/%s?cover=print' % (wiki, current_sprint)

        wiki_current_sprint = urllib2.urlopen(wiki_current_sprint)
        html_sprint = wiki_current_sprint.read()

        pattern = '<li> ([0-9]{2} [A-Za-z]{3}) [0-9]{4} - [Daily Meeting|Sprint Planning|Review].*[^<]\n</li>'

        dailys = re.compile(pattern).findall(html_sprint)
        
        #remove duplicates
        lastday = ''
        for i, day in enumerate(dailys):
            if day == lastday:
                dailys.pop(i)
            lastday = day

        if dailys:
            #remove next planning
            dailys.pop()
            self.datelist = dailys

