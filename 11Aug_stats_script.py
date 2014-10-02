from collections import defaultdict
import sys
import re

@outputSchema("URLs:chararray")
def pickURLs(url):
   try:
      # these can be arbitrary regular expressions
      keyURLs = [
      'state\.gov',
      'treasury\.gov',
      'defense\.gov',
      'dod\.gov',
      'usdoj\.gov',
      'doi\.gov',
      'usda\.gov',
      'commerce\.gov',
      'dol\.gov',
      'hhs\.gov',
      'dot\.gov',
      'energy\.gov',
      'ed\.gov',
      'va\.gov',
      'dhs\.gov',
      'whitehouse\.gov',
      '\.senate\.gov',
#test with this one
     # 'nh\.gov',
      '\.house\.gov'
      ]

      #URLs =  defaultdict(int) ##### WHAT DO THEY EQUAL EMILY???   defaultdict(int)
      URLs = []
         #URLs['other'] = 0

      for i in range(len(keyURLs)):
         tmp = len(re.findall(keyURLs[i], url, re.IGNORECASE))
         if tmp > 0:
            #URLs[keyURLs[i]] = tmp
            #URLs.append(keyURLs[i])
            return keyURLs[i]
      return 'other'
   except IOError:
      print('An error occured trying to read the file.')
   except ValueError:
      print('Non-numeric data found in the file.')
   except ImportError:
      print "NO module found"
   except EOFError:
      print('Why did you do an EOF on me?')
   except KeyboardInterrupt:
      print('You cancelled the operation.')
   except:
      print('An error occured.')

@outputSchema("counts:bag{tuple(word:chararray,count:int)}")
def Threat_countWords(content):
   try:
      # these can be arbitrary regular expressions
      Threat_Words = [
        'wmd',
      	'(weapon[a-z]+?\sof\smass\sdestruction)',
      	'(violat[a-z]+?\s?o?f?\su?n?i?v?e?r?s?a?l?\s?human\sright)',
      	'(transnational\scrim)',
      	'terrorist',
      	'terrorism',
      	'taliban',
      	'proliferat',
      	'nuclear',
      	'(north\skorea)',
      	'(natural\sdisaster)',
      	'(money\slaunder)',
      	'ksts',
      	'(known\sand\ssuspected\sterror)',
      	'(organized\scrime)',
      	'(human\srights\sviolat)',
      	'(human\srights\sabuse)',
      	'(global\swarming)',
      	'(fresh\swater)',
      	'(fragile\sstate)',
      	'(failed\sstate)',
      	'(state\sfailure)',
      	'(forest\sconservation)',
      	'(food\ssecurity)',
      	'(security\sof\sfood)',
      	'(drug\straffic)',
      	'disease',
      	'pandemic',
      	'desertification',
      	'cyberwar',
      	'cyberterror',
      	'cybersecurit',
      	'(cyber\s?attack)',
      	'(criminal\snetwork)',
      	'(criminal\sbaron)',
      	'(climate\schange)',
      	'(chemical\,?\sbiological\,?\so?r?\s?a?n?d?\s?nuclear\s?w?e?a?p?o?n?)',
      	'(chemical\sweapon)',
      	'bioterror',
      	'(biological\sweapon)',
      	'securities',
      	'(housing\scrisis*)',
      	'(subprime\smortgage*)',
      	'(lending\scrisis*)',
      	'market',
      	'(mortgage*)',
      	'(loan*)',
      	'(bank*)',
      	'(default*)',
      	'(bankrupt*)',
      	'(toxic\sasset*)',
      	'securities']

      threat_counts  = defaultdict(int)
      threat_counts['total'] = 0

      if not content or not isinstance(content, unicode):
         return [(('total'), 0)]
      threat_counts['total'] = len(content.split())

      for i in range(len(Threat_Words)):
         tmp = len(re.findall(Threat_Words[i], content, re.IGNORECASE))
         if tmp > 0:
            threat_counts[Threat_Words[i]] = tmp
      # Convert counts to bag
      countBag = []
      for word in threat_counts.keys():
         countBag.append( (word, threat_counts[word] ) )
      return countBag
   except IOError:
      print('An error occured trying to read the file.')
   except ValueError:
      print('Non-numeric data found in the file.')
   except ImportError:
      print "NO module found"
   except EOFError:
      print('Why did you do an EOF on me?')
   except KeyboardInterrupt:
      print('You cancelled the operation.')
   except:
      print('An error occured.')



#@outputSchema("counts:bag{tuple(urlname:chararray, urlcount:int, year:int, month:int, word:chararray, count:int, filled:int,
 #afterLast:int)}")
#@outputSchema("counts:bag{tuple(year:int, month:int, maxSeenDate:int, word:chararray, count:int, filled:int, afterLast:int,
URLs:chararray)}")
@outputSchema("counts:bag{tuple(year:int, month:int, word:chararray, count:int, filled:int, afterLast:int, URLs:chararray)}")
#@outputSchema("counts:bag{tuple(year:int, month:int, word:chararray, count:int, seendates:int, date:int, URLs:chararray)}")

def fillInCounts(data):
   try:
      outBag = []
      firstYear = 2013
      firstMonth = 9
      lastYear = 0
      lastMonth = 0
      # used to compute averages for months with multiple captures
      # word -> (year, month) -> count
      counts = defaultdict(lambda : defaultdict(list))

      # The next two dictionaries areused to return stats for subsequent months without captures
      # (year,month) -> date
      lastCaptureOfMonth = defaultdict(int)
      # word -> (year,month) -> {date, count}
      endOfMonthCounts = defaultdict(lambda : defaultdict(lambda: dict({'date':0,'count':0})))
      seenDates = {}
      #for s in src:
      #  maxSeenDate= max(date)
      # maxSeenDate=data[data.src==src].max(date) ### try filter relevant rows, then ask for max observed date
      for (src, date, wordCounts, urls) in data:
#         maxSeenDate = max(data[src]['date'])
         for (word, countTmp) in wordCounts:
            year = int(date[0:4])
            month = int(date[4:6])
            # some regexs '(chemical\,?\sbiological\,?\so?r?\s?a?n?d?\s?nuclear\s?w?e?a?p?o?n?)'
            # are returning tuples of the form (chemical\,), with no count
            # not sure what's going on, this is temporary fix
            if isinstance(countTmp,str) or isinstance(countTmp,int):
               count = int(countTmp)
            else:
               continue

            ymtup = (year, month)
            counts[word][ymtup].append(count)

            if date > lastCaptureOfMonth[ymtup]:
               lastCaptureOfMonth[ymtup] = date
            if date > endOfMonthCounts[word][ymtup]['date']:
               endOfMonthCounts[word][ymtup]['date'] = date
               endOfMonthCounts[word][ymtup]['count'] = count

            seenDates[(year,month)] = True

            if year < firstYear:
               firstYear = year
               firstMonth = month
            elif year == firstYear and month < firstMonth:
               firstMonth = month
            elif year > lastYear:
               lastYear = year
               lastMonth = month
            elif year == lastYear and month > lastMonth:
               lastMonth = month


      for word in counts.keys():
         # The data was collected until Sep 2013
         years = range(firstYear, 2014)
         useCount = 0
         afterLast = False
         filled = False
         ymLastUsed = (0,0)
         for y in years:
            if y > lastYear:
               afterLast = True
            if y == firstYear:
               mStart = firstMonth
            else:
               mStart = 1
            if y == 2013:
               mEnd = 9
            else:
               mEnd = 12
            for m in range(mStart, mEnd+1):
               if y == lastYear and m > lastMonth:
                  #afterLast = True
          ## trying to fix the problem of having years
               #if afterLast == True:
                  pass
               #else:
              #    continue
               if (y,m) in seenDates:
                  # Output sum, as we will divide by sum of totals later
                  useCount = sum(counts[word][(y,m)])
                  ymLastUsed = (y,m)
                  filled = False
               else:
                  # If we didn't see this date in the capture, we want to use the last capture
                  # we saw previously (we might have two captures in Feb,
                  # so for Feb we output both, but to fill-in for March we would only output
                  # the final Feb count)

                  # Automatically output an assumed total for each month (other words
                  # may no longer exist)
                  #if word == 'total':
                  #    useCount = counts[word][ymLastUsed]
                  #elif
                  if endOfMonthCounts[word][ymLastUsed]['date'] == lastCaptureOfMonth[ymLastUsed]:
                     useCount = endOfMonthCounts[word][ymLastUsed]['count']
                  else:
                     continue
                  filled = True
               if useCount == 0:
                  continue
               outBag.append( (y, m, word, useCount, int(filled), int(afterLast), urls) )
               #outBag.append( (urlname, urlcount, y, m, word, useCount, int(filled), int(afterLast)) )

      return outBag
   except IOError:
      print('An error occured trying to read the file.')
   except ValueError:
      print('Non-numeric data found in the file.')
   except ImportError:
      print "NO module found"
   except EOFError:
      print('Why did you do an EOF on me?')
   except KeyboardInterrupt:
      print('You cancelled the operation.')
   except:
      print('An error occured.')
###########
