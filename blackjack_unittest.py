from copy import deepcopy
import unittest
from blackjack.game import Deck, Hand, Game


class TestDeck(unittest.TestCase):
    def test_draw(self):
        deck = Deck()
        card = deck.draw()
        self.assertNotIn(card, deck.cards)
        self.assertEqual(len(deck.cards), 51)

class TestHand(unittest.TestCase):
    def test_add(self):
        hand = Hand()
        hand.add('2D')
        self.assertIn('2D', hand.cards)
        self.assertEqual(len(hand.cards), 1)
    
    def test_score(self):
        hand1 = Hand()
        hand1.add('2C')
        hand1.add('8D')
        hand2 = deepcopy(hand1)
        hand2.add('AD')
        hand3 = deepcopy(hand2)
        hand3.add('4S')

        self.assertEqual(hand1.score(), 10)
        self.assertEqual(hand2.score(), 21)
        self.assertEqual(hand3.score(), 15)

    def test_reset(self):
        hand = Hand()
        hand.add('AD')
        hand.reset()
        self.assertEqual(len(hand.cards), 0)

class TestGame(unittest.TestCase):
    def test_initial_deal(self):
        game = Game()
        game.initial_deal()
        self.assertEqual(len(game.player.hand.cards), 2)
        self.assertEqual(len(game.dealer.hand.cards), 2)
        self.assertEqual(len(game.deck.cards), 48)
    
    def test_stand(self):
        game = Game()
        game.initial_deal()
        game.stand(False)
        self.assertEqual(game.dealer.hand.reveal, True)
        self.assertGreaterEqual(game.dealer.hand.score(), 17)

    def test_hit(self):
        game = Game()
        game.player.hand.add('2D')
        game.player.hand.add('2H')
        game.dealer.hand.add('AD')
        game.dealer.hand.add('AH')
        game.hit(False)
        self.assertGreaterEqual(game.player.hand.score(), 6)
        self.assertLessEqual(game.player.hand.score(), 15)
        self.assertEqual(len(game.player.hand.cards), 3)

    def test_dealer_sim(self):
        game = Game()
        game.dealer.hand.add('10D')
        game.dealer.hand.add('6D')
        game.dealer.hand.reveal = True
        approx_prob_lt22 = 4/52 * 5 * 100
        game.dealer_sim()
        self.assertIsInstance(game.dealer_sims, dict)
        # self.assertGreaterEqual(game.calc_prob(17) - game.calc_prob(22), 0.0)
        # self.assertLessEqual(game.calc_prob(17) - game.calc_prob(22), 100.0)
        self.assertAlmostEqual(game.calc_prob(17) - game.calc_prob(22), approx_prob_lt22, delta=1.5)

    def test_calc_prob(self):
        game = Game()
        game.dealer_sims = {'17s':1000, '18s':1000, '19s': 500, '20s': 500, '21s': 500, 'busts': 1500}
        self.assertEqual(game.calc_prob(22), 1500/game.sim_count * 100)
        self.assertEqual(game.calc_prob(17), 100.0)
        self.assertEqual(game.calc_prob(17) - game.calc_prob(22), 3500/game.sim_count * 100)

    def test_simulate_hit(self):
        game = Game()
        game.player.hand.add('10S')
        game.player.hand.add('6S')
        game.dealer.hand.reveal = True #so that the sim deck remains unchanged in func
        approx_prob = 4/52 * 5
        game.simulate_hit()
        self.assertAlmostEqual(game.sim_hit_prob, approx_prob,delta=1.5)


if __name__ == '__main__':
    unittest.main()