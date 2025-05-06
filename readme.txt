Super Game Recommender: An Application designed to recommend you your next favorite game! By scraping Metacritic for reviews and game info, the user is able to input their desired video game parameters (e.g. Platform, Genre, Developer, Similar Games) to get a list of games recommended to your taste!

We used Document Search (Information Retrieval) to get the data for the games on Metacritic and used inspiration from Social Networks/Closures for our Recommendation Algorithm. Our Program searches through over 13000 games to make it's recommendations!

Code: https://github.com/dinethmeegoda/game-recommender

Jake Donnini worked on the Metacritic Webscraping part, found in Metacritic Scraper.py. It goes through Metacritic and puts every single game (and DLC) on the platform into the "All_games_ever_made" json file. 

This is a preprocessing step that the user will not have to run during the use of the program, as the original scraping took over 5 hours to run. The json file from scraping is not needed for the program locally as the algorithm gets the data from the current json file stored in our github web repository (which is why an internet connection is required to run this program).

Jibraan Ghani worked on the majority of the algorithm, found in RecommenderAlgorithm.py, using a custom scoring system to weight each parameter differently.

Dineth Meegoda made the UI/Interaction in main.py, packaged the pip requirements, made the manual (and this readme), as well as added some algorithm features, such as fuzzy search for the json parsing and "Games You Already Like".