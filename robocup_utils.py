import time
import os

def launch_simulation(l_team, r_team, log_dir, fast_m = False):
    """
    Launch n_sim simulations opposing l_team and r_team distributed over n_proc processes.
    Call launch_match.
    """

    if fast_m == True:
        synch_mode = "true"
    else:
        synch_mode = "false"
    command = ' '.join(["rcssserver",
                        "server::auto_mode=1",
                        "server::synch_mode={}".format(synch_mode),
                        "server::team_l_start={}".format(l_team),
                        "server::team_r_start={}".format(r_team),
                        "server::kick_off_wait=50",
                        "server::half_time=300",
                        "server::nr_normal_halfs=1",
                        "server::nr_extra_halfs=0",
                        "server::penalty_shoot_outs=0",
                        "server::game_logging=1",
                        "server::text_logging=0",
                        "server::log_date_format=%Y%m%d%H%M%S-",
                        "server::game_log_dir={}".format(log_dir),
                        "server::text_log_dir={}".format(log_dir)])
    os.system(command)

def extract_results(log):
    """
    """

    score = log.split("-vs-")
    team_l = int(score[0].split('_')[-1])
    team_r = int(score[1][:-4].split('_')[-1])

    return (team_l, team_r)
