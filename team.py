import scipy

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
