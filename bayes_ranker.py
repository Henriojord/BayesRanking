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
import os
import glob
import subprocess

from utils import Dotdict
import robocup_utils as rc
import team

def generate_game(left_team, right_team, number_games, fast_mode, log_dir):
    """
    Run a RoboCup Simulation 2D game involving the two given teams and return
    the result.
        left_team, right_team: Path to the team's script (string)

    Return the number of won games for both left_team and right_team
    """

    team_a = 0
    team_b = 0
    for i in range(number_games):
        rc.launch_simulation(left_team, right_team, log_dir, fast_mode)
        #Get the logs of the last (most recent) simulation
        logs = glob.glob(os.path.join(log_dir, '*.rcg'))
        latest_log_file = max(logs, key=os.path.getctime)
        #Get results
        team_l, team_r = rc.extract_results(latest_log_file)
        if team_l > team_r:
            team_a += 1
        elif team_l < team_r:
            team_b += 1

    return team_a, team_b

def main(args):
    #Global variables
    confidence_mass = round(args.cm, 2) #Runtime error occurs on the numpy side for numbers not rounded to 2
    assert (confidence_mass > 0 and confidence_mass < 1), "The confidence mass should be a number between 0 and 1"
    prior_games = args.pg
    assert (prior_games >= 0), "The number of prior games should be greater or equal than 0"
    max_try = args.mt
    print(max_try)
    assert (max_try >= 0), "The maximal number of games should be positive"
    a = args.a
    b = args.b
    assert (a > 0 and b > 0), "A Beta distribution is only defined for parameters greater than 0"
    games = 0
    ranked = False
    winner = team.Team(2, 2, confidence_mass, 'None', '')
    add = 0
    hist_a = []
    hist_b = []

    #Build the two teams
    team_a = team.Team(2, 2, confidence_mass, args.ln, args.lb)
    team_b = team.Team(2, 2, confidence_mass, args.rn, args.rb)

    #Make some prior simulations
    score_team_a, score_team_b = generate_game(team_a.path, team_b.path, args.pg, args.fastm, args.logdir)
    hist_a.append(score_team_a)
    hist_b.append(score_team_b)
    team_a.update(args.pg, score_team_a)
    team_b.update(args.pg, score_team_b)

    #Start the ranking algorithm
    while not ranked:
        if team_a.low_bound > team_b.up_bound: #TeamA > TeamB
            winner = team_a
            ranked = True
        elif team_a.up_bound < team_b.low_bound: #TeamA < TeamB
            winner = team_b
            ranked = True
        elif games < max_try: #Too much uncertainty, observe one additional game
            score_team_a, score_team_b = generate_game(team_a.path, team_b.path, args.pg, args.fastm, args.logdir)
            hist_a.append(score_team_a)
            hist_b.append(score_team_b)
            team_a.update(args.pg, score_team_a)
            team_b.update(args.pg, score_team_b)
            games += args.pg
        else: #Too much uncertainty, but simulations number limit reached
            add = 1
            score_team_a, score_team_b = generate_game(team_a.path, team_b.path, 1, args.fastm, args.logdir)
            hist_a.append(score_team_a)
            hist_b.append(score_team_b)
            if score_team_a > score_team_b:
                winner = team_a
            elif score_team_a < score_team_b:
                winner = team_b
            else:
                winner = None
            ranked = True
            print("Teams have equivalent performance. Ran a decisive game")
    print("Evaluated among %d games plus %d additional games"%(games, add))
    if winner != None:
        print("Winner: %s"%(winner.name))
    else:
        print("No winner.")
    print("%s won %d, %s won %d of %d games"%(team_a.name, team_a.a - 2, team_b.name, team_b.a - 2, (prior_games + games)))
    # with open(os.path.join(args.logdir, 'bayes_results'), 'a') as f:
    #     f.write('%s\t%d\t%d\t%d\t%d\t%d\n'%(winner.name, team_a.a - 2, team_b.a - 2, prior_games, games, add))
    return winner

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Rank 2 RoboCup Simulation 2D teams according to Bayesian inference")
    parser.add_argument("--lb", type=str, default="/home/scom/Documents/robocup/environment/helios-10Singapore/start.sh", help="Path of the left team's script")
    parser.add_argument("--ln", type=str, default="Helios2010", help="Name of the left team")
    parser.add_argument("--rb", type=str, default="/home/scom/Documents/robocup/environment/agent2d-3.1.1/src/start.sh", help="Path of the right team's script")
    parser.add_argument("--rn", type=str, default="Agent2D", help="Name of the right team")
    parser.add_argument("--cm", type=float, default=0.95, help="Confidence mass")
    parser.add_argument("--pg", type=int, default=10, help="Number of prior games")
    parser.add_argument("--mt", type=int, default=10, help="Maximal number of tries (results in tries * prior games) (doesn't include first prior games)")
    parser.add_argument("--a", type=float, default=2, help="'a' parameter of the prior Beta distribution")
    parser.add_argument("--b", type=float, default=2, help="'b' parameter of the prior Beta distribution")
    parser.add_argument("--fastm", type=bool, default=True, help="Boolean controling simulation fast mode")
    parser.add_argument("--logdir", type=str, default="logs", help="Path to the directory for storing resulting log files")
    args = Dotdict(vars(parser.parse_args()))
    winner = main(args)
    return winner
