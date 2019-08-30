import logging, sys, argparse, re


def str2bool(v):
    # copy from StackOverflow
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_entity(tag_seq, char_seq):
    BODY = get_BODY_entity(tag_seq, char_seq)
    SURGERY = get_SURGERY_entity(tag_seq, char_seq)
    DRUG = get_DRUG_entity(tag_seq, char_seq)
    SYMPTOMD = get_SYMPTOMD_entity(tag_seq, char_seq)
    ISYMPTOM = get_ISYMPTOM_entity(tag_seq, char_seq)
    return BODY, SURGERY, DRUG, SYMPTOMD, ISYMPTOM

def post_process_metastatic(result):
    meta_post = []
    for r in result:
        ss = r.split(' ',1)
        if len(ss[1])>0:
            m = ss[1]
            if m.endswith(','):
                # print(r)
                if len(m[:-1].strip())>0:
                    meta_post.append(ss[0]+' '+m[:-1].strip())
                #     print(ss[0]+' '+m[:-1].strip())
                # print('as\n')
            elif m.endswith('，'):
                # print(r)
                if len(m[:-1].strip())>0:
                    meta_post.append(ss[0]+' '+m[:-1].strip())
                #     print(ss[0]+' '+m[:-1].strip())
                # print('\n')
            elif m.startswith(','):
                # print(r)
                if len(m[1:].strip())>0:
                    meta_post.append(str(int(ss[0])+1)+' '+m[1:].strip())
                #     print(str(int(ss[0])+1)+' '+m[1:].strip())
                # print('\n')
            elif m.endswith('、'):
                # print(r)
                if len(m[:-1].strip())>0:
                    meta_post.append(ss[0]+' '+m[:-1].strip())
                #     print(ss[0]+' '+m[:-1].strip())
                # print('\n')
            else:
                meta_post.append(r)
        # else:
        #     print(r)
    
    for mp in meta_post:
        if ',' in mp:
            # print(mp)
            # print('df\n')
            meta_post.remove(mp)
            
            index = mp.split(' ',1)[0]
            
            mp = mp.split(' ',1)[1]
            
            tsplit = mp.split(',')
            for ts in tsplit:
                if len(ts)==0:
                    tsplit.remove(ts)
            
            tsplits = []
            tsplits.append(index)

            if len(tsplit)>1:
                for num in range(len(tsplit)):
                    meta_post.append(str(int(index)+mp.index(tsplit[num]))+' '+tsplit[num].strip())
            else:
                meta_post.append(mp)
    return meta_post

def remove_number(result,content,seq):
    meta_post = []
    for m in result:
        if len(m)>0:
            split_meta = m.split(' ',1)
            if len(split_meta)>1:
                if split_meta[1].endswith(','):
                    meta_post.append(split_meta[1][:-1].strip())
                else:
                    meta_post.append(split_meta[1].strip())
    for mp in meta_post:
        if ',' in mp:
            tsplit = mp.split(',')
            meta_post.remove(mp)
            for ts in tsplit:
                if ts not in meta_post:
                    meta_post.append(ts.strip())

    for mp in meta_post:
        if mp.endswith('('):
            mp1 = mp[:-1]
            meta_post.append(mp1)
            if mp in meta_post:
                meta_post.remove(mp)

    for mp in meta_post:
        if '(' in mp and not ')' in mp:
            # print(mp)
            st1 = mp[:mp.index('(')]
            st2 = mp[mp.index('(')+1:]
            st = '('+st1+'\('+st2+'\S?\S?\S?\)'+')'
            # print(st)
            pattern = re.compile(st)
            m = pattern.findall(content)
            if len(m)>0:
                # print(m[0])
                meta_post.append(m[0])
                if mp in meta_post:
                    meta_post.remove(mp)
        if mp == '网膜':
            st = '大网膜'
            # print(st)
            pattern = re.compile(st)
            m = pattern.findall(content)
            if len(m)>0:
                # print(m[0])
                meta_post.append(m[0])
                if mp in meta_post:
                    meta_post.remove(mp)
        if mp == '腹膜':
            st = '盆底腹膜'
            # print(st)
            pattern = re.compile(st)
            m = pattern.findall(content)
            if len(m)>0:
                # print(m[0])
                meta_post.append(m[0])
                if mp in meta_post:
                    meta_post.remove(mp)

    item1 = ['术后','盆底','全身','静脉','双侧卵巢']
    for it in item1:
        if it in meta_post:
            meta_post.remove(it)
    
    item2 = ['右下气管淋巴结','右髂总血管淋巴结','右上气管淋巴结']
    for it in item2:
        if it in meta_post and (it[:-3]+'旁') in content:
            meta_post[meta_post.index(it)] = it[:-3]+'旁淋巴结'
    
    item3 = ['胸骨骨','胸椎骨','右侧肱骨骨','左股骨上段骨','左侧髂骨骨','第9胸椎体骨','腰骶椎骨','胸椎T11骨','T9椎体内','腰椎骨','左乳内','右侧髂骨骨']
    for it in item3:
        if it in meta_post:
            meta_post[meta_post.index(it)] = it[:-1]
    
    item4 = ['胸腔']
    for it in item4:
        for mp in meta_post:
            if it in mp:
                meta_post.remove(mp)
    
    item5 = ['双侧肋骨']
    for it in item5:
        for mp in meta_post:
            if it in mp and mp in it:
                meta_post.remove(mp)
                meta_post.append(it[2:])
    
    item6 = ['骨质']
    for it in item6:
        for mp in meta_post:
            if mp.endswith(it):
                meta_post.remove(mp)
                meta_post.append(mp[:-2])

    item7 = ['右侧','骨骼','双侧','肺炎','全身多处','远端']
    for it in item7:
        for mp in meta_post:
            if mp == it:
                meta_post.remove(mp)
            if mp.endswith(it):
                if mp in meta_post:
                    meta_post.remove(mp)
                    meta_post.append(mp[:-2])

    item7 = ['肝肺']
    for it in item7:
        for mp in meta_post:
            if mp == it:
                meta_post.remove(mp)
                meta_post.append(mp[:1])
                meta_post.append(mp[1:])

    for mp in meta_post:
        if mp.startswith('移'):
            meta_post[meta_post.index(mp)] = mp[1:]
    for mp in meta_post:
        if mp.endswith('示'):
            meta_post[meta_post.index(mp)] = mp[:-1]
    for mp in meta_post:
        if mp == '腹膜网膜':
            # print(mp)
            meta_post.remove(mp)
            meta_post.append('腹膜')
            meta_post.append('网膜')

    if '淋巴结' in meta_post:
        for mp in meta_post:
            if '淋巴结' in mp and not mp in '淋巴结':
                if '淋巴结' in meta_post:
                    meta_post.remove('淋巴结')

            
    return meta_post

def pattern_completion(result,data,seq):
    results = []
    if (len(result)>1):
        item = ['肝肺','肝','右胸壁','胸膜','胸壁','骨','全身骨骼','右侧胸膜','左侧胸膜','左侧乳头','右侧乳头','肝脏','胸3椎体','左侧内乳','脑','肺炎','双侧肾上腺']
        #'双肺','右肺',
        indice = []
        judge = []
        complementary = []

        # if seq=='300':
        #     print(result)

        for index in range(1,len(result)):
            bias1 = 7
            bias2 = 4
            temp_indice = []

            if (result[index].endswith('淋巴结') and not result[index].split(' ')[1]=='淋巴结') or (result[index].endswith('淋巴') and not result[index].split(' ')[1]=='淋巴'):
                start = int(result[index].split(' ')[0])
                end = int(result[index-1].split(' ')[0])+len(result[index-1].split(' ')[1])
                temp_indice.append(index)

                if start<end+bias1 and start>end:
                    if not result[index-1].endswith('淋巴结') and result[index-1].split(' ')[1] not in item:
                        result[index-1] = result[index-1]+'淋巴结'
                        # print(result[index-1])
                        temp_indice.append(index-1)
                    flag = index-1
                    
                    while flag>-1:
                        # temp_indice.append(flag)
                        start1 = int(result[flag].split(' ')[0])
                        end1 = int(result[flag-1].split(' ')[0])+len(result[flag-1].split(' ')[1])
                        if start1<end1+bias2 and start1>end1:
                            if not result[flag-1].endswith('淋巴结') and result[flag-1].split(' ')[1] not in item:
                                result[flag-1] = result[flag-1]+'淋巴结'
                                temp_indice.append(flag-1)
                            flag = flag-1
                        else:
                            break
                
            
            elif result[index].split(' ')[1].strip()=='淋巴结':
                start = int(result[index].split(' ')[0])
                end = int(result[index-1].split(' ')[0])+len(result[index-1].split(' ')[1])
                temp_indice.append(index)
                
                if start<end+bias1 and start>end:
                    if not result[index-1].endswith('淋巴结') and result[index-1].split(' ')[1] not in item:
                        result[index-1] = result[index-1]+'淋巴结'
                        temp_indice.append(index-1)
                    flag = index-1
                    indice.append(index)
                    
                    while flag>-1:
                        # temp_indice.append(flag)
                        start1 = int(result[flag].split(' ')[0])
                        end1 = int(result[flag-1].split(' ')[0])+len(result[flag-1].split(' ')[1])
                        if start1<end1+bias2 and start1>=end1:
                            if not result[flag-1].endswith('淋巴结') and result[flag-1].split(' ')[1] not in item:
                                result[flag-1] = result[flag-1]+'淋巴结'
                                temp_indice.append(flag-1)
                            flag = flag-1
                        else:
                            break

            if len(temp_indice)>0:
                judge.extend(temp_indice)
                e = int(result[temp_indice[0]].split(' ')[0]) + len(result[temp_indice[0]].split(' ')[1])
                s = int(result[temp_indice[len(temp_indice)-1]].split(' ')[0])
                entity = '12 '+data[s:e]
                complementary.append(entity)


        under_delete = []
        for index in judge:
            under_delete.append(result[index])

        for ud in under_delete:
            result.remove(ud)

        if len(complementary)>0:
            result.extend(complementary)

        results = result

    else:
        results = result

    return results


def get_BODY_entity(tag_seq, char_seq):
    length = len(char_seq)
    BODY = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-BO':
            if 'body' in locals().keys():
                BODY.append(body)
                del body
            body = str(i) + ' ' + char
            if i+1 == length:
                BODY.append(body)
        if tag == 'I-BO':
            if 'body' in locals().keys():
                body += char
            else: body = (str(i) + ' ' +char)
            
            if i+1 == length:
                BODY.append(body)
        if tag not in ['I-BO', 'B-BO']:
            if 'body' in locals().keys():
                BODY.append(body)
                del body
            continue
    return BODY

def get_SURGERY_entity(tag_seq, char_seq):
    length = len(char_seq)
    SURGERY = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-SU':
            if 'sur' in locals().keys():
                SURGERY.append(sur)
                del sur
            sur = str(i) + ' ' + char
            if i+1 == length:
                SURGERY.append(sur)
        if tag == 'I-SU':
            if 'sur' in locals().keys():
                sur += char
            else: sur = char
            if i+1 == length:
                SURGERY.append(sur)
        if tag not in ['I-SU', 'B-SU']:
            if 'sur' in locals().keys():
                SURGERY.append(sur)
                del sur
            continue
    return SURGERY

def get_DRUG_entity(tag_seq, char_seq):
    length = len(char_seq)
    DRUG = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-DR':
            if 'dru' in locals().keys():
                DRUG.append(dru)
                del dru
            dru = str(i) + ' ' + char
            if i+1 == length:
                DRUG.append(dru)
        if tag == 'I-DR':
            if 'dru' in locals().keys():
                dru += char
            else: dru = char
            if i+1 == length:
                DRUG.append(dru)
        if tag not in ['I-DR', 'B-DR']:
            if 'dru' in locals().keys():
                DRUG.append(dru)
                del dru
            continue
    return DRUG

def get_SYMPTOMD_entity(tag_seq, char_seq):
    length = len(char_seq)
    SYMPTOMD = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-SD':
            if 'syd' in locals().keys():
                SYMPTOMD.append(syd)
                del syd
            syd = str(i) + ' ' + char
            if i+1 == length:
                SYMPTOMD.append(syd)
        if tag == 'I-SD':
            if 'syd' in locals().keys():
                syd += char
            else: syd = char
            if i+1 == length:
                SYMPTOMD.append(syd)
        if tag not in ['I-SD', 'B-SD']:
            if 'syd' in locals().keys():
                SYMPTOMD.append(syd)
                del syd
            continue
    return SYMPTOMD

def get_ISYMPTOM_entity(tag_seq, char_seq):
    length = len(char_seq)
    ISYMPTOM = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-IS':
            if 'isy' in locals().keys():
                ISYMPTOM.append(isy)
                del isy
            isy = str(i) + ' ' + char
            if i+1 == length:
                ISYMPTOM.append(isy)
        if tag == 'I-IS':
            if 'isy' in locals().keys():
                isy += char
            else: isy = char
            if i+1 == length:
                ISYMPTOM.append(isy)
        if tag not in ['I-IS', 'B-IS']:
            if 'isy' in locals().keys():
                ISYMPTOM.append(isy)
                del isy
            continue
    return ISYMPTOM


def get_logger(filename):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    return logger
