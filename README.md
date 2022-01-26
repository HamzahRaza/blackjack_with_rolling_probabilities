# BlackJack With Rolling Probabilities
The underlying probabilities of a blackjack game are unintuitive. 

Blackjack is a series of dependant trials - each new card dealt dramatically shifts the edge towards the player or the house. As a result probabilities are in flux, and can be impractical to calculate without computer simulation.

This implementation of blackjack informs the player of relevant probabilities throughout the game. Playing the game was quite revelatory for me. Consider: the probability of the dealer going bust with an upcard of 6 is 42%. Yet, with an upcard of 7, the same probability drops to 26%.

This version of the project is played through the command line, though a GUI could easily be added on top of the existing program. To play, use the command ```python blackjack```.

![blackjack-demo](https://user-images.githubusercontent.com/50002504/151095848-ad83d455-6e1f-4e7e-acba-3a7dd288a4e9.jpg)
