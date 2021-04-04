# Weather-chatbot
The bot responds to requests for weather only for the 5 days for Moscow and SPb.  It gets data from the OpenWeatherMap free API.

Commands:
* /start - displays basic information about itself
* /help - displays basic information about itself
* /bye - end communication

Messages are taken by the bot as requests regarding the weather. 

Processing requests:
* parsing the incoming message, extracting the city and date from the message
* search of the forecast in the found city for the corresponding date

Parsing of an incoming message is done using the pymorphy2 library.
