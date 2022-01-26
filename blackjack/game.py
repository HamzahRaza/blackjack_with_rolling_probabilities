from copy import deepcopy
from numpy import random

#Constants
SUITS = ['H', 'D', 'S', 'C']
CARD_FACES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Deck:

    def __init__(self):
        self.cards = []
        for i in CARD_FACES:
            for j in SUITS:
                self.cards.append(i + j)

    def draw(self):
        """ remove card from deck"""
        return self.cards.pop(random.randint(len(self.cards)))

class Hand:
    def __init__(self):
        self.cards = []
        self.reveal = True #whether the first card has been revealed when printing hand

    def add(self, card):
        """add given card to hand

        Keyword arguments:
        card -- a card(string), most likely drawn from deck with Deck.draw()
        """
        self.cards.append(card)

    def score(self):
        """return score for hand according to the conventional Blackjack ruleset"""
        score = 0
        aces = 0

        for card in self.cards:
            if card[0] in '23456789':
                score += int(card[0])
            elif card[0:2] == '10':
                score += 10
            elif card[0].isalpha() and card[0] != 'A':
                score += 10
            else:
                aces += 1

        for _ in range(aces):
            if score + 11 > 21:
                score += 1
            else:
                score += 11

        return score

    def reset(self):
        """remove all cards from hand. Note that this does not return cards to deck"""
        self.cards = []

    def __str__(self):
        str = ''
        for i in range(len(self.cards)):
            if i == 0 and self.reveal == False:
                str += ' |?|'
            else:
                str += ' |{}|'.format(self.cards[i])
        
        return str

class Dealer:
    def __init__(self):
        self.hand = Hand()
        self.hand.reveal = False

class Player:
    def __init__(self):
        self.hand = Hand()
        self.cash = 1000

class Game:
    def __init__(self):
        self.deck = Deck()
        self.player = Player()
        self.dealer = Dealer()
        self.bet = 0
        self.dealer_sims = {}
        self.sim_hit_prob = 0.0
        self.sim_count = 5000 #number of hands to simulate in determining probabilities

    def placeBet(self):
        """allow player to input bet amount and subtract bet from cash"""
        print('Please place your bet (less than ${}):'.format(self.player.cash), end='')
        self.bet = input()
        while not self.bet.isnumeric() or int(self.bet) > self.player.cash:
            if self.bet == 'q':
                return
            print('{} is not a number between 0 and {}! Please re-enter your bet:'.format(self.bet, self.player.cash))
            self.bet = input()
        
        self.player.cash -= int(self.bet)

    def initial_deal(self):
        self.player.hand.add(self.deck.draw())
        self.dealer.hand.add(self.deck.draw())
        self.player.hand.add(self.deck.draw())
        self.dealer.hand.add(self.deck.draw())
        if self.player.hand.score() < 17:
            self.simulate_hit()

    def print_game(self):
        """print game output - player and dealer hands, cash and bet amounts and relevant probabilities"""
        print('________________________________________')
        print('Your cash: {} \t Current Bet: {}'.format(self.player.cash, self.bet))
        dealer_score = self.dealer.hand.score()
        player_score = self.player.hand.score()
        print('Dealer Hand: {}'.format(self.dealer.hand), end="")
        if self.dealer.hand.reveal == True: print('\t Score:{}'.format(dealer_score), end="")
        print('\nYour Hand: {} \t Score:{}'.format(self.player.hand, player_score))
        
        print('________________________________________')
        if player_score <= 21:
            self.dealer_sim()   
            print('Probabilty that the dealer goes bust: {:.2f}%'.format(self.calc_prob(22)))
        if player_score >= 17 and player_score < 21:
            print('Probability that the dealer scores {} or more: {:.2f}%'.format(player_score, (self.calc_prob(player_score) - self.calc_prob(22)) ))
        elif self.dealer.hand.reveal == False and player_score < 17: 
            print('Probability that next hit will bring your score to between 17 and 21: {:.2f}%'.format(self.sim_hit_prob * 100))
        print('________________________________________')
        input()
        
    def stand(self, prints = True):
        """
        execute logic after player has chosen to stand. Prints outcome of game

        Keyword arguments:
        prints -- boolean that determines whether player feedback should print to console     
        """
        self.dealer.hand.reveal = True
        if prints: self.print_game()

        while self.dealer.hand.score() < 17:
            self.dealer.hand.add(self.deck.draw())
            if prints: self.print_game()
        
        if prints:
            if self.dealer.hand.score() > 21:
                print('Dealer went bust! You win $', self.bet)            
                self.player.cash += int(self.bet) * 2
            elif self.dealer.hand.score() > self.player.hand.score():
                print('The dealer won! You lost $', self.bet)
            elif self.dealer.hand.score() < self.player.hand.score():
                print('You won! You win $', self.bet)
                self.player.cash += int(self.bet) * 2
            else:
                print('You both got {}! Push: You are returned your {}'.format(self.player.hand.score(), self.bet))
                self.player.cash += int(self.bet)
    
    def hit(self, prints = True):
        """
        execute logic after player has chosen to hit. Prints outcome of game if player goes bust
        
        Keyword arguments:
        prints -- boolean that determines whether player feedback should print to console       
        """
        self.player.hand.add(self.deck.draw())

        #recalculate next hit probabilities
        if self.player.hand.score() < 17:
            self.simulate_hit() 

        if prints: 
            self.print_game()
        
            if self.player.hand.score() > 21:
                print('You went bust! You lost $', self.bet)

        
    
    def dealer_sim(self):
        """simulate the possible outcomes for dealer, given current hand. Returns dict with count of outcomes"""

        #dict that stores count of given scores
        scores = {
            "17s": 0,
            "18s": 0,
            "19s": 0,
            "20s": 0,
            "21s": 0,
            "busts": 0,
        }
        for _ in range(self.sim_count):
            sim_deck = deepcopy(self.deck)
            sim_dealer_hand = Hand()
            if self.dealer.hand.reveal == False:
                sim_dealer_hand.add(deepcopy(self.dealer.hand.cards[-1]))
            else:
                for card in deepcopy(self.dealer.hand.cards):
                    sim_dealer_hand.add(card)
            while sim_dealer_hand.score() < 17:
                sim_dealer_hand.add(sim_deck.draw())

            score = sim_dealer_hand.score()
            if score == 17:
                scores['17s'] += 1
            elif score == 18:
                scores['18s'] += 1
            elif score == 19:
                scores['19s'] += 1
            elif score == 20:
                scores['20s'] += 1
            elif score == 21:
                scores['21s'] += 1
            else:
                scores['busts'] += 1
                
        self.dealer_sims = scores

        return scores

    def calc_prob(self, gte_value):
        """
        return probability (float) for greater than scenario, given scores have been simulated 

        Keyword arguments:
        gte_value -- greater than or equal to value (int)
        """
        scores = list(self.dealer_sims.values())
        numerator = sum(scores[gte_value - 17:])
        return (numerator / self.sim_count) * 100

    def simulate_hit(self):
        """simulate the possible outcomes for player in next hit. Sets sim_hit_prob to probability that next hit brings score to between 17 and 21 (float)"""
        count = 0
        for _ in range(self.sim_count):
            sim_deck = deepcopy(self.deck)
            if self.dealer.hand.reveal == False: sim_deck.cards.append(self.dealer.hand.cards[0]) #re-add hidden dealer card to deck
            sim_player_hand = Hand()
            for card in deepcopy(self.player.hand.cards):
                sim_player_hand.add(card)
            sim_player_hand.add(sim_deck.draw())
            if sim_player_hand.score() >= 17 and sim_player_hand.score() < 22:
                count += 1
        
        self.sim_hit_prob = count / self.sim_count

    def start(self):
        """execute logic of game"""

        print('Welcome to Blackjack. Type q anytime to quit')
        print('You begin with $', self.player.cash)
        self.placeBet()

        while self.bet != 'q':
            
            self.initial_deal()

            self.print_game()
            player_move = ''


            if self.player.hand.score() == 21 and self.dealer.hand.score() == 21:
                self.dealer.hand.reveal = True
                self.print_game()
                print('You both got Blackjack! Push: You are returned your {}'.format(self.bet))
                self.player.cash += int(self.bet)
            elif self.player.hand.score() == 21:
                self.dealer.hand.reveal = True
                self.print_game()
                print('Blackjack! You win ${}'.format(int(self.bet) * 1.5))
                self.player.cash += int(int(self.bet) * 2.5)
            elif self.dealer.hand.score() == 21:
                self.dealer.hand.reveal = True
                self.print_game()
                print('Dealer has Blackjack! You lost {}'.format(self.bet))

            else:
                    
                while player_move != 'q' and player_move != 'stand' and self.player.hand.score() <= 21:
                    print('What would you like to do?', end = ' ')
                    print("Type 'stand', 'hit' or 'double'") if len(self.player.hand.cards) == 2 else print("Type 'stand' or 'hit'")
                    player_move = input()
                    #input validation
                    if player_move == 'hit':
                        self.hit()
                    elif player_move == 'double':                        
                        self.player.cash -= int(self.bet)
                        self.bet = str(int(self.bet) * 2)
                        self.hit()
                        if self.player.hand.score() <= 21:
                            self.stand()
                            break
                    elif player_move == 'stand':
                        self.stand()
                    elif player_move == 'q':
                        self.bet = 'q'
                        break
                    else:
                        print("That isn't a recognized command! Try again or type 'q' to quit")
            if player_move != 'q':
                if self.player.cash == 0: 
                    print('You lost all your money!')
                    break
                self.deck = Deck()
                self.player.hand.reset()
                self.dealer = Dealer()
                self.placeBet()


