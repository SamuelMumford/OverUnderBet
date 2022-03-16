# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 22:01:09 2019
@author: Sam
"""

from selenium import webdriver
from bs4 import BeautifulSoup
from numpy import genfromtxt
from operator import itemgetter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from webdriver_manager.chrome import ChromeDriverManager

#Change the teamnames so they match between websites
def corrname(name):
    if(name == 'TWolves'):
        name = 'Timberwolves'
    if(name == 'Sixers'):
        name = '76ers'
    if(name == 'Blazers'):
        name = 'Trail Blazers'
    if(name == 'Mavs'):
        name = 'Mavericks'
    if(name == 'Cavs'):
        name = 'Cavaliers'
    return name

#Get predicted records from 538
def getInfo():
    options = webdriver.ChromeOptions()
    #options.binary_location = "/usr/bin/chrome.exe"
    #All the arguments added for chromium to work on selenium
    options.add_argument("--no-sandbox") #This make Chromium reachable
    options.add_argument("--no-default-browser-check") #Overrides default choices
    options.add_argument("--no-first-run")
    options.add_argument("--disable-default-apps")
    options.add_argument("HideCommandPromptWindow")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)#executable_path='/home/sam/Downloads/YahooSeasonScrapeAndSimulate-master/chromedriver.exe')
    
    #Pull up the website
    ad1 = 'https://projects.fivethirtyeight.com/2022-nba-predictions/?ex_cid=rrpromo'
    driver.get(ad1)
    content = driver.page_source
    bs = BeautifulSoup(content, features="html.parser")
        
    table =  driver.find_element_by_xpath("//table[@id='standings-table']")
    
    projrecs = {}
    for row in table.find_elements_by_xpath(".//tr"):
        for td in row.find_elements_by_xpath(".//td[@class='team']"):
            name = td.get_attribute("data-str")
        for tdd in row.find_elements_by_xpath(".//td[@class='num div proj-rec']"):
            rec = tdd.text
            projwins = int(rec.split('-')[0])
            projrecs[name] = projwins
    driver.quit()
    return projrecs

#Get records from ESPN
def getInfoESPN():
    options = webdriver.ChromeOptions()
    #All the arguments added for chromium to work on selenium
    options.add_argument("--no-sandbox") #This make Chromium reachable
    options.add_argument("--no-default-browser-check") #Overrides default choices
    options.add_argument("--no-first-run")
    options.add_argument("--disable-default-apps") 
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)#executable_path='/home/sam/Downloads/YahooSeasonScrapeAndSimulate-master/chromedriver.exe')
    
    #Pull up the website
    ad1 = 'https://www.espn.com/nba/standings'
    driver.get(ad1)
    content = driver.page_source
    bs = BeautifulSoup(content, features="html.parser")
    
    realRecs = {}
    teams = 15
    
    base = "//*[@id='fittPageContainer']/div[3]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/div/div[2]/table/tbody/tr["
    end = "]/td[1]/span"
    endL = "]/td[2]/span"
    baseName = "//*[@id='fittPageContainer']/div[3]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/table/tbody/tr["
    endName = "]/td/div/span[4]/a"
    endName2 = "]/td/div/span[3]/a"
    endNameClinch = "]/td/div/span[5]/a"
    endNameElim = endName
    for i in range(1, teams+1):
        wins = int(driver.find_element_by_xpath(base + str(i) + end).text)
        loss = int(driver.find_element_by_xpath(base + str(i) + endL).text)
        if(i <= 10):
            namelist = driver.find_element_by_xpath(baseName + str(i) + endName).text.split()
            if(len(namelist) == 0):
                namelist = driver.find_element_by_xpath(baseName + str(i) + endNameClinch).text.split()
            name = namelist[-1]
            realRecs[name] = [wins, loss, wins + loss]
        else:
            namelist = driver.find_element_by_xpath(baseName + str(i) + endName2).text.split()
            if(len(namelist) == 0):
                namelist = driver.find_element_by_xpath(baseName + str(i) + endNameElim).text.split()
            name = namelist[-1]
            realRecs[name] = [wins, loss, wins + loss]
    
    base = "//*[@id='fittPageContainer']/div[3]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/div/div[2]/table/tbody/tr["
    end = "]/td[1]/span"
    endL = "]/td[2]/span"
    baseName = "//*[@id='fittPageContainer']/div[3]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/table/tbody/tr["
    endName = "]/td/div/span[4]/a"
    endName2 = "]/td/div/span[3]/a"
    endNameElim = endName
    for i in range(1, teams+1):
        wins = int(driver.find_element_by_xpath(base + str(i) + end).text)
        loss = int(driver.find_element_by_xpath(base + str(i) + endL).text)
        if(i <= 10):
            namelist = driver.find_element_by_xpath(baseName + str(i) + endName).text.split()
            if(len(namelist) == 0):
                namelist = driver.find_element_by_xpath(baseName + str(i) + endNameClinch).text.split()
            name = namelist[-1]
            realRecs[name] = [wins, loss, wins + loss]
        else:
            namelist = driver.find_element_by_xpath(baseName + str(i) + endName2).text.split()
            if(len(namelist) == 0):
                namelist = driver.find_element_by_xpath(baseName + str(i) + endNameElim).text.split()
            name = namelist[-1]
            realRecs[name] = [wins, loss, wins + loss]
    realRecs['Trail Blazers'] = realRecs['Blazers']
    driver.quit()
    return realRecs

#Process the CSV to make a dictionary with the predicted wins for each team
#also return the CSV split into an array for later iteration (not neeed but convenient)
def VegasProcess():
    players = np.empty(shape=[0, 1], dtype=str)
    VegasData = genfromtxt('Vegas.csv', delimiter=',', dtype='unicode')
    VegasRecs = {}
    for i in range(1, VegasData.shape[0]):
        name = VegasData[i, 0]
        name = corrname(name)
        pwin = float(VegasData[i, 1])
        VegasRecs[name]=pwin
        player = VegasData[i, 2]
        if(player != ''):
            if(player not in players):
                players = np.append(players, player)
        player = VegasData[i, 3]
        if(player != ''):
            if(player not in players):
                players = np.append(players, player)
    return VegasRecs, VegasData, players

#Compare the 538 predicted wins to the the Vegas lines
def predVals(pr, VegasRecs):
    comboD = {}
    for key in pr:
        if key in VegasRecs:
            comboD[key] = pr[key] - VegasRecs[key]
        else:
            print(key)
            print('missing')
    return comboD

#Compare current records to the Vegas pace
def nowVals(pr2, VegasRecs):   
    comboD = {}
    for key in pr:
        if key in VegasRecs:
            comboD[key] = pr2[key][0] - (VegasRecs[key])*pr2[key][2]/82.0
        else:
            print(str(key) + ' is missing')
    return comboD

#Make the list of over/under results for each player
def MakeRecords(VegasData, comboD, players):
    corr = [0, 0, 0, 0, 0, 0]
    delta = [0, 0, 0, 0, 0, 0]
    for j in range(0, len(players)):
        person = players[j]
        for i in range(1, VegasData.shape[0]):
            if(person == VegasData[i, 2]):
                name = VegasData[i, 0]
                name = corrname(name)
                value = comboD[name]
                if(value > 0):
                    corr[j] += 1
                if(value == 0):
                    corr[j] += .5
                delta[j] += value
            if(person == VegasData[i, 3]):
                name = VegasData[i, 0]
                name = corrname(name)
                value = comboD[name]
                if(value < 0):
                    corr[j] += 1
                if(value == 0):
                    corr[j] += .5
                delta[j] -= value
    return corr, delta

#Use the over/under results to print out standings
def ShowRecs(players, corr, delta, booly):
    sorty = []
    for i in range(0, len(players)):
        sorty.append([players[i], corr[i], delta[i]])
    recs = sorted(sorty, key=itemgetter(1), reverse=True)
    recs = sorted(recs, key=itemgetter(2), reverse=True)
    #print(recs)
    print()
    if(booly):
        print('Present Performance:')
    else:
        print('538 Predictions:')
    for i in range(0, len(players)):
        char = ''
        if(np.sign(recs[i][2]) > 0):
            char = '+'
        print(str(i+1) + '. ' + recs[i][0] + ": " + char + str("%.2f" % recs[i][2]) + ' wins, ' + str(recs[i][1]) + '-' + str(6 - recs[i][1]))
    return recs

#EVERYTHING FROM HERE IS PLOTTING

#Get the minimum and maximum over/under values chosen by gamblers. Used for 
#scaling all the plots
def getMinMax(players, VegasData, comboD):
    mini = 0
    maxi = 0
    for j in range(0, len(players)):
        person = players[j]
        for i in range(1, VegasData.shape[0]):
            if(person == VegasData[i, 2]):
                name = VegasData[i, 0]
                name = corrname(name)
                value = comboD[name]
                delt = value
            if(person == VegasData[i, 3]):
                name = VegasData[i, 0]
                name = corrname(name)
                value = comboD[name]
                delt = -value
            if(delt > maxi):
                maxi = delt
            if(delt < mini):
                mini = delt
    return mini, maxi

#Get the results for each gambler. Sort them from best to worst picks
def make_sort(person, VegasData, comboD):
    part_team = np.empty(shape=[0, 1])
    part_res = np.empty(shape=[0, 1])
    part_cats = np.empty(shape=[0, 1], dtype=bool)
    for i in range(1, VegasData.shape[0]):
        if(person == VegasData[i, 2]):
            part_cats = np.append(part_cats, True)
            name = VegasData[i, 0]
            name = corrname(name)
            value = comboD[name]
            delt = value
            part_team = np.append(part_team, name)
            part_res = np.append(part_res, delt)
        if(person == VegasData[i, 3]):
            part_cats = np.append(part_cats, False)
            name = VegasData[i, 0]
            name = corrname(name)
            value = comboD[name]
            delt = -value
            part_team = np.append(part_team, name)
            part_res = np.append(part_res, delt)
    sort_team = [x for _, x in sorted(zip(part_res, part_team), reverse=True)]
    sort_cat = [x for _, x in sorted(zip(part_res, part_cats), reverse=True)]
    sort_res = sorted(part_res, reverse=True)
    return sort_team, sort_cat, sort_res

#Split data into good and bad picks
def pos_and_neg(name_split, name_res):
    pos_xs = [item for res, item in zip(name_res, name_split) if res >= 0]
    neg_xs = [item for res, item in zip(name_res, name_split) if res < 0]
    return pos_xs, neg_xs

#Make bar charts for the good and bad picks
def autolabel(name_res, ax, mini, maxi, alph):
    pos_xs, neg_xs = pos_and_neg(range(len(name_res)), name_res)
    respos, resneg = pos_and_neg(name_res, name_res)
    width = .8
    al(ax, pos_xs, respos, width, 'blue', alph, mini, maxi)
    al(ax, neg_xs, resneg, width, 'red', alph, mini, maxi)

#Put labels on the end of bar charts
def al(ax, xs, name_res, width, c, alph, mini, maxi):
    rects = ax.bar(xs, name_res, width, color=c, alpha=alph, edgecolor="black")
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        hbase = rect.get_height()
        delta = .06 * (maxi - mini)
        if hbase < 0:
            height = hbase - delta
        else:
            height = hbase
        ax.annotate('{:.2f}'.format(hbase),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 0),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

#Format the tick marks and axis labels
def ax_format(ax, name_res, name_cats, name_team, name, alph, mini, maxi, ind):
    inds = range(len(name_res))
    pos_xs, neg_xs = pos_and_neg(inds, name_res)
    namepos, nameneg = pos_and_neg(name_team, name_res)
    pos_cs, neg_cs = pos_and_neg(name_cats, name_res)
    restot = np.sum(name_res)
    rtr = '{:.2f}'.format(restot)
    ax.set_ylabel('Over/Under Result (wins)', fontsize=13)
    ax.set_title(str(ind+1) + '. ' + name + ': ' + rtr, fontsize=15)
    ax.set_xticks(pos_xs, minor=True)
    ax.set_xticks(neg_xs)
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    tickname = ax.set_xticklabels(namepos, minor=True, verticalalignment='top')
    ticknameneg = ax.set_xticklabels(nameneg, verticalalignment='bottom')
    ax.set_ylim(mini * 1.2, maxi * 1.2)
    ticklen = 3.5
    ax.tick_params(axis='y', direction='in', length=ticklen)
    ax.tick_params(axis='x', direction='in', length=ticklen)
    ax.tick_params(axis='x', direction='out', length=ticklen, which='minor')
    neg_tick = ax.get_xticklabels()
    color_over = 'green'
    color_under = 'black'
    for xtick, cat in zip(neg_tick, neg_cs):
        if cat:
            xtick.set_color(color_over)
        else:
            xtick.set_color(color_under)
    pos_tick = ax.get_xticklabels(minor=True)
    for xtick, cat in zip(pos_tick, pos_cs):
        if cat:
            xtick.set_color(color_over)
        else:
            xtick.set_color(color_under)
    custom_lines = [Line2D([0], [0], color='blue', alpha=alph, lw=6),
                    Line2D([0], [0], color='red', alpha=alph, lw=6),
                    Line2D([0], [0], color='green', lw=1),
                    Line2D([0], [0], color='black', lw=1)]
    ax.legend(custom_lines, ['Winning Picks', 'Losing Picks', 'Over Picks', 'Under Picks'])
    plt.setp(tickname, rotation=30, fontsize=9)
    plt.setp(ticknameneg, rotation=30, fontsize=9)

#Call above methods to make plots
def make_bar(name, name_cats, name_team, name_res, mini, maxi, ind, base):
    fig = plt.figure()
    fig.set_facecolor('silver')
    ax = fig.add_subplot(111)
    ax.set_facecolor('white')
    alph = .6
    autolabel(name_res, ax, mini, maxi, alph)
    ax_format(ax, name_res, name_cats, name_team, name, alph, mini, maxi, ind)
    fname = base + str(ind+1) + '_' + name+'.svg'
    plt.savefig(fname, format='svg', bbox_inches='tight')
    plt.show()

def makePlots(players, recs, VegasData, comboD, mini, maxi, base):
    for i in range(len(players)):
        person = recs[i][0]
        # Assign the teams, pick type, and over/under result for each competitor
        name_team, name_cats, name_res = make_sort(person, VegasData, comboD)
        # Use the categorized data to make plots
        make_bar(person, name_cats, name_team, name_res, mini, maxi, i, base)
        
#How long to give the chrome pages to load, can change based on internet connection
SLEEP_SECONDS = 2
#Can do a full folder or '' to save in the working folder
#plotfolder = '/home/sam/Downloads/YahooSeasonScrapeAndSimulate-master/pics/'
plotfolder = ''
#Process the over/under bets
VegasRecs, VegasData, players = VegasProcess()
#Get the predictions from 528 and records from ESPN. Store in dictionaries with
#each team name as the key
pr = getInfo()
pr2 = getInfoESPN()
#Get the games above or below the Vegas pace for each team
comboD = predVals(pr, VegasRecs)
#Get the over/under for each gambler
corr, delta = MakeRecords(VegasData, comboD, players)
#Print out the results sorted
_ = ShowRecs(players, corr, delta, False)

#Do the same thing for the real records from ESPN
comboD = nowVals(pr2, VegasRecs)
corr, delta = MakeRecords(VegasData, comboD, players)
recs = ShowRecs(players, corr, delta, True)

#Get the scales for plotting
mini, maxi = getMinMax(players, VegasData, comboD)
#Make the bar plots
makePlots(players, recs, VegasData, comboD, mini, maxi, plotfolder)