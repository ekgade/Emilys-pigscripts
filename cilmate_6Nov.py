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
            '(natural\sdisaster)',
            '(global\swarming)',
            '(fresh\swater)',
            '(forest\sconservation)',
            '(food\ssecurity)',
            '(security\sof\sfood)',
            'desertification',
            '(intergovernmental\spanel\son\sclimate\schange)',
            '(climatic\sresearch\sunit)',
            'climategate',
            '(greenhouse\sgas)',
            'anthropogenic',
            'anthropocene',
            '(ocean\sacidification)',
            'pollution',
            '(climate\schange)'
            ]

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
