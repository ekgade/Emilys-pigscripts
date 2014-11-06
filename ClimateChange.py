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

#can also use r and then string rather than escape //

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
