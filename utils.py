class Dotdict(dict):
     """
     dot.notation access to dictionary attributes
     From: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
     """
     __getattr__ = dict.get
     __setattr__ = dict.__setitem__
     __delattr__ = dict.__delitem__

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
