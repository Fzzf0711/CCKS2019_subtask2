import logging, sys, argparse, re


def str2bool(v):
    # copy from StackOverflow
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
        
def get_Tumer_entity(tag_seq, char_seq):
    length = len(char_seq)
    TUMER = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-TU':
            if 'tumer' in locals().keys():
                TUMER.append(tumer)
                del tumer
            tumer = str(i) + ' ' + char
            if i+1 == length:
                TUMER.append(tumer)
#            print(tumer)
        if tag == 'I-TU':
            if 'tumer' in locals().keys():
                tumer += char
            else: tumer = char
            
            if i+1 == length:
                TUMER.append(tumer)
        if tag not in ['I-TU', 'B-TU']:
            if 'tumer' in locals().keys():
                TUMER.append(tumer)
                del tumer
            continue
    return TUMER

def postprocess_tumerlist(TUMER):
    TUMER_post = []
    for tumer in TUMER:
        if len(tumer)>0:
            tumer_split = tumer.split(' ')
            if len(tumer_split)>1:
                TUMER_post.append(tumer_split[1])
            else:
                TUMER_post.append(tumer_split[0])
                
    tumer_set = set(TUMER_post)
    tumer_list = list(tumer_set)
    return tumer_list

def get_logger(filename):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    return logger
