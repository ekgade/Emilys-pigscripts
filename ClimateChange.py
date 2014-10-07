#Climate Change Script - python


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
        'IPCC',
        '(intergovernmental\spanel\son\sclimate\schange)',
        ## remember when you cacluate totals to subtract this from climate change totals or you will count it twice!
        'CRU',
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
