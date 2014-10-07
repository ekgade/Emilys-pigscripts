#!/usr/bin/python
from __future__ import division
import csv
from collections import defaultdict
from numpy import *
import matplotlib as mpl
mpl.use('Agg')
import argparse
import matplotlib.pyplot as plt
from datetime import datetime

def main(datafile, graphTitle, imagefile):
    counts = defaultdict(lambda : defaultdict(int))
    startY = 2013
    endY = 2013
    with open(datafile, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='\t')
        for (year, month, url, word, count) in csvreader:
            #(year, month, url, word, count) = line
            if len(year) != 4:
              continue
            #for (year, month, url, word, count) in csvreader:
            if int(year) < startY and int(year) > 1994:
                # some weird counts for proliferat in 1979/80/81...
                # actually in checksum data: Hive query to view:
                # select * from url_ts_checksum where substr(cast(ts as string),1,4) = '1979';

                startY = int(year)
                counts[(url, word)][(int(year),int(month))] = int(count)

    groupWords = { 'group1': [
                            'terrorist',
                            'terrorism',
                            '(known\sand\ssuspected\sterror)',
                            'ksts'
                            ],
                    'group2': [
                            '(forest\sconservation)',
                            '(global\swarming)',
                            'desertification',
                            '(climate\schange)'
                            ],
                            #'group3': [
                            #'cyberwar',
                            #'cyberterror',
                            #'cybersecurit',
                            #'(cyber\s?attack)'
                            #],
                    'group4': [
                        # '(chemical\,?\sbiological\,?\so?r?\s?a?n?d?\s?nuclear\s?w?e?a?p?o?n?)',
                             '(chemical\sweapon)',
                             #'proliferat',
                             'nuclear',
                             '(biological\sweapon)',
                             'wmd',
                             '(weapon[a-z]+?\sof\smass\sdestruction)'
                              ]#,
                              # 'group5': [
                              #'(criminal\snetwork)',
                              #'(criminal\sbaron)',
                              #'(drug\straffic)',
                              #'(money\slaunder)',
                              #'(transnational\scrim)',
                              #'(organized\scrime)'
                              #],
                            #'group6': [
                            #'(human\srights\sviolat)',
                            # '(human\srights\sabuse)',
                            #'(violat[a-z]+?\s?o?f?\su?n?i?v?e?r?s?a?l?\s?human\sright)'
                            # ], #,
                                   #'group7': [
                            # '(food\ssecurity)',
                            # '(security\sof\sfood)'
                            #],
                            # 'group8':[
                            # '(north\skorea)'
                            # ]
                  #  'group7': [
                  #          'securities',
                  #          '(lending\scrisis*)',
                  #          'market',
                  #          '(bank*)',
                  #          '(default*)',
                    #         '(bankrupt*)',
                    #         '(toxic\sasset*)'
                    #         ],
                    # 'group8':[
                    #         '(housing\scrisis*)',
                    #         '(subprime\smortgage*)',
                    #         '(mortgage*)',
                    #         '(loan*)'
                    #     ]

                  }
    groupLabels = {'group1':'Terrorism',
                   'group2':'Environmental Degradation',
                   #'group3':'Cyber Security',
                   'group4':'Weapons of Mass Destruction'#,
                   #'group5':'Transnational Crime',
                   #'group6':'Human Rights Violations',
                   #'group8':'North Korea',
                   #'group7':'Food Security'
#                   'group7': 'Banking Crisis',
#                   'group8': 'Mortgage Crisis'

                 }

    URLLabels = ['state\.gov'

                 ,
                 #'treasury\.gov',
                 #'defense\.gov',
                 #'dod\.gov',
                 #'usdoj\.gov',
                 #'doi\.gov',
                 #'usda\.gov',
                 #'commerce\.gov',
                 #'dol\.gov',
                 #'hhs\.gov',
                 #'dot\.gov',
                 #'energy\.gov',
                 #'ed\.gov',
                 #'va\.gov',
                 #'dhs\.gov',
                 #'whitehouse\.gov',
                 #'\.senate\.gov',
                 #test with this one
                 #'nh\.gov',
                 #'\.house\.gov','other'
                 ]

    groupFrequencies = defaultdict(list)
    urlfreq= defaultdict(list)
    dates = []
    for y in range(startY, endY+1):
        #only have data thru sept of 2013, else full year
        if y == endY:
            mEnd = 9
        else:
            mEnd = 12
        # range is not inclusive, so increment by one
        for m in range(1, mEnd+1):
            if not counts[(url,'total')][(y,m)]:
                continue

            for url in URLLabels:
                for group in groupWords.keys():
                    sumGroupCounts = sum([counts[(url,word)][(y,m)] for word in groupWords[group]])
                    groupFrequencies[group].append( sumGroupCounts / counts[(url,'total')][(y,m)])
                urlfreq[url].append(groupFrequencies)

            #frequency.append(counts[wordToGraph][(y,m)] / counts['total'][(y,m)])
            dates.append(datetime(y,m,1))

    plt.clf()

    # Color progression to use
    plt.rc('axes', color_cycle=['r', 'g', 'b', 'y', 'c',  'm', 'k'])

    for url in URLLabels:
        for group in groupWords.keys():
            plt.plot_date( dates, groupFrequencies[group], '-', label=groupLabels[group])

    plt.xlabel('Date')
    plt.ylabel('Frequency')
    plt.title(graphTitle)
    plt.tight_layout()
    plt.legend(loc='upper right')
    # Use show() to display the image when run instead of saving it
    #plt.show()

    plt.savefig(imagefile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("datafile")
    parser.add_argument("graphTitle")
    parser.add_argument("imagefile")
    args = parser.parse_args()

    datafile = args.datafile
    graphTitle = args.graphTitle
    imagefile = args.imagefile

    main(datafile, graphTitle, imagefile)
