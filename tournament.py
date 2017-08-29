import json
from operator import itemgetter
import argparse

import bayes_ranker as br

def main(args):
    #Loads tournament settings
    with open('tournaments/2016.json', 'r') as f:
        targs = json.load(f)
    #some variables
    rounds = ['seeds', 'preliminary-rounds', 'pre-qualifying-rounds', 'post-qualifying-rounds', 'consolation-playoff', 'semi-finals', 'final-playoff']
    teams = {t:0 for t in targs['teams']}
    tournament_dict = {}
    ##Seed tournament
    seed_dict = {}
    for group in sorted(targs['seeds']):
        l = len(targs['seeds'][group])
        seed_dict[group] = {i:0 for i in targs['seeds'][group]} #Create a dictionnary representing the ranking inside the groups
        #Run Bayesian ranker for each possible couple of teams in the group
        print(seed_dict)
        for i in range(l):
            for j in range(i + 1, l):
                team_l = targs['seeds'][group][i]
                team_r = targs['seeds'][group][j]
                bin_team_l = targs['teams'][team_l]
                bin_team_r = targs['teams'][team_r]
                args.lb = bin_team_l
                args.ln = team_l
                args.rb = bin_team_r
                args.rn = team_r
                #Call Bayesian ranker
                wt = br.main(args)
                #Update score in teams
                if wt != None:
                    teams[wt.name] += targs['points'][0]
                    seed_dict[group][wt.name] += targs['points'][0]
                else:
                    teams[team_l] += targs['points'][1]
                    teams[team_r] += targs['points'][1]
                    seed_dict[group][team_l] += targs['points'][1]
                    seed_dict[group][team_r] += targs['points'][1]
    tournament_dict['seeds'] = seed_dict
    #Write seeds ranking in files
    for s in tournament_dict['seeds']:
        with open('textres/seeds_{}'.format(s), 'w') as f:
            sort = sorted(tournament_dict['seeds'][s].items(), key=itemgetter(1), reverse=True)
            for so in sort:
                f.write('{}\t{}\n'.format(so[0], so[1]))
    ##Process each round
    for r in range(1, len(rounds)):
        print('------')
        print(rounds[r])
        print('------')
        round_dict = {}
        for group in sorted(targs[rounds[r]]):
            teams_group = [t for t in targs[rounds[r]][group]] #Round_Group_Rank specified teams
            #Fetch teams
            tmp = []
            for t in teams_group:
                split = t.split('_')
                team = sorted(tournament_dict[split[0]][split[1]].items(), key=itemgetter(1), reverse=True)[int(split[2]) - 1][0]
                tmp.append(team)
            print(teams_group)
            round_dict[group] = {t:0 for t in tmp}
            teams_group = [k for k in round_dict[group].keys()]
            l = len(teams_group)
            #Run Bayesian ranker for each possible couple of teams in the group
            for i in range(l):
                for j in range(i + 1, l):
                    team_l = teams_group[i]
                    team_r = teams_group[j]
                    bin_team_l = targs['teams'][team_l]
                    bin_team_r = targs['teams'][team_r]
                    args.lb = bin_team_l
                    args.ln = team_l
                    args.rb = bin_team_r
                    args.rn = team_r
                    #Call Bayesian ranker
                    wt = br.main(args)
                    #Update score in teams
                    if wt != None:
                        teams[wt.name] += targs['points'][0]
                        round_dict[group][wt.name] += targs['points'][0]
                    else:
                        teams[team_l] += targs['points'][1]
                        teams[team_r] += targs['points'][1]
                        round_dict[group][team_l] += targs['points'][1]
                        round_dict[group][team_r] += targs['points'][1]
        tournament_dict[rounds[r]] = round_dict
        #Write groups ranking in files
        for s in tournament_dict[rounds[r]]:
            with open('textres/{}_{}'.format(rounds[r], s), 'w') as f:
                sort = sorted(tournament_dict[rounds[r]][s].items(), key=itemgetter(1), reverse=True)
                for so in sort:
                    f.write('{}\t{}\n'.format(so[0], so[1]))
    #Print the final ranking
    print(sorted(teams.items(), key=itemgetter(1), reverse=True))
    #Write the final ranking into a file
    with open('textres/final', 'w') as f:
        for t in sorted(teams.items(), key=itemgetter(1), reverse=True):
            f.write('{}\t{}\n'.format(t[0], t[1]))

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
    main(args)
