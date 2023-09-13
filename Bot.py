from datetime import datetime
from logging.config import listen
import speech_recognition as sr
import pyttsx3 
import webbrowser
import wikipedia
import wolframalpha
import weather2
import random
import pyjokes

list_of_likes = []
# Speech engine initialisation
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # 0 = male, 1 = female
activationWord = 'computer' # Single word
 
 
# Wolfram Alpha client
appId = 'appID'
wolframClient = wolframalpha.Client(appId)
 
def speak(text, rate = 100):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()
 
def parseCommand():
    listener = sr.Recognizer()
    print('Listening for a command')
 
    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)
 
    try: 
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en_us')
        print(f'The input speech was: {query}')
    except Exception as exception:
        print('I did not quite catch that')
        speak('I did not quite catch that')
        print(exception)
        return 'None'
 
    return query
 
def search_wikipedia(query = ''):
    searchResults = wikipedia.search(query)
    if not searchResults:
        print('No wikipedia result')
        return 'No result received'
    try: 
        wikiPage = wikipedia.page(searchResults[0])
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary
 
def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']
 
def search_wolframAlpha(query = ''):
    response = wolframClient.query(query)
 
    # @success: Wolfram Alpha was able to resolve the query
    # @numpods: Number of results returned
    # pod: List of results. This can also contain subpods
    if response['@success'] == 'false':
        return 'Could not compute'
    
    # Query resolved
    else:
        result = ''
        # Question 
        pod0 = response['pod'][0]
        pod1 = response['pod'][1]
        # May contain the answer, has the highest confidence value
        # if it's primary, or has the title of result or definition, then it's the official result
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            # Get the result
            result = listOrDict(pod1['subpod'])
            # Remove the bracketed section
            return result.split('(')[0]
        else: 
            question = listOrDict(pod0['subpod'])
            # Remove the bracketed section
            return question.split('(')[0]
            # Search wikipedia instead
            speak('Computation failed. Querying universal databank.')
            return search_wikipedia(question)
 
 
 
# Main loop
if __name__ == '__main__':
    speak('All systems nominal.')
 
    while True:
        # Parse as a list
        query = parseCommand().lower().split()
 
        if query[0] == activationWord:
            query.pop(0)
 
            # List commands
            if query[0] == 'say':
                if 'hello' in query:
                    speak('Greetings, all.')
                else: 
                    query.pop(0) # Remove say
                    speech = ' '.join(query)
                    speak(speech)
 
            # Navigation
            if query[0] == 'go' and query[1] == 'to':
                speak('Opening...')
                query = ' '.join(query[2:])
                webbrowser.open_new(query)
 
            # Wikipedia 
            if query[0] == 'wikipedia':
                query = ' '.join(query[1:])
                speak('Querying the universal databank.')
                speak(search_wikipedia(query))
                
            # Wolfram Alpha
            if query[0] == 'compute' or query[0] == 'computer':
                query = ' '.join(query[1:])
                speak('Computing')
                try: 
                    result = search_wolframAlpha(query)
                    speak(result)
                except:
                    speak('Unable to compute.')

            # Weather
            if query[0] == "weather":
                query.pop(0)
                city = query[0]
                state = query[1]
                country = " ".join(query[2:])

                speak("Processing...")
                speak(weather2.main(city, state, country))
            
            # Note taking
            if query[0] == 'log':
                speak('Ready to record your note')
                newNote = parseCommand().lower()
                now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                with open('note_%s.txt' % now, 'w') as newFile:
                    newFile.write(newNote)
                speak('Note written')

            if query[0] == "help":
                speak("I support several functions, to navigate the web say go to and then the website. To search wikipedia, say wikipedia and then the topic. To access wolframalpha, say compute or computer and then the prompt. To access weather information, say weather and then the city, state, and country of the place you want information for. To make notes, say log and then the message you would like to log.")
 
            if query[0] == "day":
                query.pop(0)
                speak("How was your day operator?")
                phrase = parseCommand().lower()
                tb_phrase = TextBlob(phrase)
                if tb_phrase.sentiment.polarity <= 0:
                    speak("I'm so sorry to hear that")
                    spec_number = random.randint(0, 1)
                    if spec_number == 0:
                        speak(pyjokes.get_joke(language = "en", category = "all"))
                    else:
                        if list_of_likes:
                            speak("Why don't you think about " + list_of_likes[random.randint(0, len(list_of_likes))])
                        else:
                            speak(pyjokes.get_joke(language = "en", category = "all"))
                else:
                    speak("What made today special?")
                    goodThing = parseCommand().lower()
                    list_of_likes.append(goodThing)
                    speak("I will remember that")

            if query[0] == 'exit':
                speak('Goodbye')
                break
