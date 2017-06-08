import scipy.stats
import scipy.optimize

class Team():
    def __init__(self, a, b, confidence_mass, name, path):
        """
        Team constructor:
            a, b: Initial Beta distribution parameters (float > 0)
            confidence_mass: Highest Density Interval (HDI)'s span (float 0 <= x <= 1)
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

def generate_game(left_team, right_team):
    """
    Run a RoboCup Simulation 2D game involving the two given teams and return
    the result.
        left_team, right_team: Path to the team's script (string)

    Return a binary value (1: win, 0: lose) for both left_team and right_team
    """
    #TODO: Generate some random data
    #TODO: Generate true games
    return 1, 0

confidence_mass = 0.95
prior_games = 1
games = 0
ranked = False
max_game = 200
team_a = Team(2, 2, confidence_mass, "TeamA", "")
team_b = Team(2, 2, confidence_mass, "TeamB", "")
for i in range(prior_games): #Make some prior simulations
    score_team_a, score_team_b = generate_game(team_a.path, team_b.path)
    team_a.update(1, score_team_a)
    team_b.update(1, score_team_b)
while not ranked:
    if team_a.low_bound > team_b.up_bound: #TeamA > TeamB
        winner = team_a
        ranked = True
    elif team_a.up_bound < team_b.low_bound: #TeamA < TeamB
        winner = team_b
        ranked = True
    elif games < max_game: #Too much uncertainty
        score_team_a, score_team_b = generate_game(team_a.path, team_b.path)
        team_a.update(1, score_team_a)
        team_b.update(1, score_team_b)
        games += 1
    else: #Too much uncertainty, but simulations number limit reached
        score_team_a, score_team_b = generate_game(team_a.path, team_b.path)
        if score_team_a > score_team_b:
            winner = team_a
        elif score_team_a == score_team_b:
            winner = None
        else:
            winner = team_b
        ranked = True
if winner != None:
    print("Winner: %s"%(winner.name))
else:
    print("Teams have equivalent performance")
print("Evaluated among %d prior games plus %d additional games"%(prior_games, games))
print("%s won %d, %s won %d of %d games"%(team_a.name, team_a.a - 2, team_b.name, team_b.a - 2, (prior_games + games)))
