from collections import defaultdict
import sys
import re

@outputSchema("URLs:chararray")
def pickURLs(url):
   try:
      # these can be arbitrary regular expressions
      keyURLs = [
      'whitehouse\.gov'
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
