"""
Rank 2 RoboCup Simulation 2D teams according to Bayesian inference.

Each team is associated with a parameter following a Beta(a, b) distribution.
This parameter represents the team's likelihood to win against its given opponent.
At first, a given number (prior_games) of games are observed and the parameter's distribution of
each team is updated according to the results.
Then, the teams are ranked according to the Highest Density Interval of their distribution.
Additional games are simulated until the teams can be statically ranked.

Refer to: John K. Kruschke, Bayesian estimation supersedes the t test, Journal of Experimental Psychology: General, May, 2012
"""

import scipy.stats
import scipy.optimize
import argparse
import numpy as np
import csv
from tqdm import tqdm

from utils import Dotdict

class Team():
    def __init__(self, a, b, confidence_mass, name, path):
        """
        Team constructor:
            a, b: Initial Beta distribution parameters (float > 0)
            confidence_mass: Highest Density Interval (HDI)'s span (float 0 < x < 1)
            name: Team name (string)
            path: path to the team's script
        """
        self.a = a
        self.b = b
        self.confidence_mass = confidence_mass
        self.distrib = scipy.stats.beta(a, b)
        self.hdi = self.get_hdi()
        self.up_bound = self.hdi[1]
        self.low_bound = self.hdi[0]
        self.name = name
        self.path = path

    def get_hdi(self):
        """
        Compute the Highest Density Interval of the team's distribution:
        Adapted from: https://stackoverflow.com/questions/22284502/highest-posterior-density-region-and-central-credible-region
        """
        inconfidence_mass = 1 - self.confidence_mass

        def get_interval_width(low_tail):
            interval_width = self.distrib.ppf(self.confidence_mass + low_tail) - self.distrib.ppf(low_tail)

            return interval_width

        hdi_low_tail = scipy.optimize.fmin(get_interval_width, inconfidence_mass, ftol=1e-8, disp=False)[0]
        hdi = self.distrib.ppf([hdi_low_tail, self.confidence_mass + hdi_low_tail])

        return hdi

    def update(self, n, z):
        """
        Update the Beta distribution:
            n: number of observed games
            z: number of won games
        """
        self.a += z
        self.b += n - z
        self.distrib = scipy.stats.beta(self.a, self.b)
        self.hdi = self.get_hdi()
        self.up_bound = self.hdi[1]
        self.low_bound = self.hdi[0]

def generate_game(theta, nb_samples):
    """
    Run a RoboCup Simulation 2D game involving the two given teams and return
    the result.
        left_team, right_team: Path to the team's script (string)

    Return a binary value (1: win, 0: lose) for both left_team and right_team
    """

    match = scipy.stats.bernoulli(theta)
    score = match.rvs(nb_samples)
    score_team_a = sum(score)
    score_team_b = nb_samples - sum(score)

    return score_team_a, score_team_b

def main(args, theta):
    #Global variables
    confidence_mass = round(args.cm, 2) #Runtime error occurs on the numpy side for numbers not rounded to 2
    assert (confidence_mass > 0 and confidence_mass < 1), "The confidence mass should be a number between 0 and 1"
    prior_games = args.pg
    assert (prior_games >= 0), "The number of prior games should be greater or equal than 0"
    max_game = args.mg
    assert (max_game >= 0), "The maximal number of games shoud be positive"
    a = args.a
    b = args.b
    assert (a > 0 and b > 0), "A Beta distribution is only defined for parameters greater than 0"
    games = 0
    ranked = False
    winner = None

    #Build the two teams
    team_a = Team(a, b, confidence_mass, "TeamA", "")
    team_b = Team(a, b, confidence_mass, "TeamB", "")

    #Make some prior simulations
    for i in range(prior_games):
        score_team_a, score_team_b = generate_game(theta, args.pg)
        team_a.update(args.nb_samples, score_team_a)
        team_b.update(args.nb_samples, score_team_b)

    #Start the ranking algorithm
    while not ranked:
        if team_a.low_bound > team_b.up_bound: #TeamA > TeamB
            winner = team_a
            ranked = True
        elif team_a.up_bound < team_b.low_bound: #TeamA < TeamB
            winner = team_b
            ranked = True
        elif games < max_game: #Too much uncertainty, observe one additional game
            score_team_a, score_team_b = generate_game(theta, args.nb_samples)
            team_a.update(args.nb_samples, score_team_a)
            team_b.update(args.nb_samples, score_team_b)
            games += 1
        else: #Too much uncertainty, but simulations number limit reached
            score_team_a, score_team_b = generate_game(theta, args.nb_samples)
            if score_team_a > score_team_b:
                winner = team_a
            elif score_team_a == score_team_b:
                winner = Team(a, b, confidence_mass, "None", "")
            else:
                winner = team_b
            ranked = True
    # if winner != None:
    #     print("Winner: %s"%(winner.name))
    # else:
    #     print("Teams have equivalent performance")
    # print("Evaluated among %d prior games plus %d additional games"%(prior_games, games))
    # print("%s won %d, %s won %d of %d games"%(team_a.name, team_a.a - 2, team_b.name, team_b.a - 2, (prior_games + games)))
    return [theta, team_a.a - 2, team_b.a - 2, games, winner.name]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Rank 2 RoboCup Simulation 2D teams according to Bayesian inference")
    parser.add_argument("--cm", type=float, default=0.95, help="Confidence mass")
    parser.add_argument("--pg", type=int, default=0, help="Number of prior games")
    parser.add_argument("--mg", type=int, default=100, help="Maximal number of games (doesn't include prior games)")
    parser.add_argument("--a", type=float, default=2, help="'a' parameter of the prior Beta distribution")
    parser.add_argument("--b", type=float, default=2, help="'b' parameter of the prior Beta distribution")
    parser.add_argument("--nbt", type=int, default=100, help="Number of test per theta")
    parser.add_argument("--step", type=float, default=0.05, help="Theta range's step")
    parser.add_argument("--nb_samples", type=int, default=1, help="Number of games generated at once")
    args = Dotdict(vars(parser.parse_args()))
    to_test = np.arange(0.0, 1.0 + args.step, args.step)
    csv_content = [["Theta", "Avg. A", "Avg. B", "Avg. generation", "Ratio A winner"]]
    for theta in to_test:
        print("Testing theta: %f ..."%(theta))
        avg_a = []
        avg_b = []
        avg_games = []
        ratio_winner_a = []
        for i in tqdm(range(args.nbt)):
            res = main(args, theta)
            avg_a.append(res[1])
            avg_b.append(res[2])
            avg_games.append(res[3])
            ratio_winner_a.append(res[4])
        avg_a = sum(avg_a) / len(avg_a)
        avg_b = sum(avg_b) / len(avg_b)
        avg_games = sum(avg_games) / len(avg_games)
        ratio_winner_a = (ratio_winner_a.count("TeamA") * 100) / args.nbt
        csv_content.append([theta, avg_a, avg_b, avg_games, ratio_winner_a])
        print([theta, avg_a, avg_b, avg_games, ratio_winner_a])
    with open("B%d%d_%d_%d_%f_%d_tests.csv"%(args.a, args.b, args.pg, args.nb_samples, args.step, args.nbt), "w") as f:
        writer = csv.writer(f, delimiter=";")
        for elt in csv_content:
            writer.writerow(elt)
