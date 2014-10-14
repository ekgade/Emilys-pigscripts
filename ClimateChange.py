#Climate Change Script - python


@outputSchema("match:chararray)")
def ClimateChangeWords(content):
   try:
      # these can be arbitrary regular expressions
      ClimateChange_Words = [
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

      for i in range(len(ClimateChange_Words)):
         tmp = len(re.findall(ClimateChange_Words[i], content, re.IGNORECASE))
         if tmp > 0:
            return ClimateChange_Words[i]

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
