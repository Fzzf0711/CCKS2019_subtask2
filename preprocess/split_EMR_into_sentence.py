import os, shutil
# from processExcel import writeData

def split_EMR_into_sentence(path):

    filenames = os.listdir(path)
    # print(len(filenames))

    parent_path = os.path.join('.','data/split_sentence')
    if os.path.exists(parent_path):
        shutil.rmtree(parent_path,True)
    os.mkdir(parent_path)

    for name in filenames:
        filepath = os.path.join(path,name)

        lines = []
        with open(filepath,'r',encoding='utf-8') as fr:
            lines = fr.readlines()

        content = ''
        for line in lines:
            content += line
        
        content = content.replace('。',',')
        content = content.replace('?',',')
        content = content.replace('？',',')
        content = content.replace(':',',')
        content = content.replace('：',',')
        content = content.replace('；',',')
        content = content.replace(';',',')
        content = content.replace('，',',')
        content = content.replace('1.',',')
        content = content.replace('2.',',')
        content = content.replace('3.',',')
        content = content.replace('4.',',')
        content = content.replace('5.',',')
        content = content.replace('6.',',')
        content = content.replace('7.',',')
        content = content.replace(' 1.',',')
        content = content.replace(' 2.',',')
        content = content.replace(' 3.',',')
        content = content.replace(' 4.',',')
        content = content.replace(' 5.',',')
        content = content.replace(' 6.',',')
        content = content.replace(' 7.',',')

        split_sentence = content.split(',')
        temp_sentence = []
        for sen in split_sentence:
            if len(sen.strip())>0:
                temp_sentence.append(sen.strip())

        split_sentence = temp_sentence    

        sentences = []
        
        for index in range(1,len(split_sentence)):
            list2 = []
            list3 = []
            daixie = '.'
            flag_index = index
            if '转移' in split_sentence[flag_index] or '骨质破坏' in split_sentence[flag_index]:
                flag_index = flag_index-1
                while '代谢活跃' in split_sentence[flag_index] and flag_index>-1:
                    daixie = ','+split_sentence[flag_index] + daixie
                    flag_index = flag_index-1
            daixie = daixie[1:]

            if '侵及' in split_sentence[index] and '癌' in split_sentence[index] and '并' in split_sentence[index]:
                if split_sentence[index].index('侵及') > split_sentence[index].index('癌') and split_sentence[index].index('侵及') < split_sentence[index].index('并'):
                    split_sentence[index] = split_sentence[index][split_sentence[index].index('并'):]
            if '累及' in split_sentence[index] and '癌' in split_sentence[index] and '并' in split_sentence[index]:
                if split_sentence[index].index('累及') > split_sentence[index].index('癌') and split_sentence[index].index('累及') < split_sentence[index].index('并'):
                    split_sentence[index] = split_sentence[index][split_sentence[index].index('并'):]
            if '侵犯' in split_sentence[index] and '癌' in split_sentence[index] and '并' in split_sentence[index]:
                if split_sentence[index].index('侵犯') > split_sentence[index].index('癌') and split_sentence[index].index('侵犯') < split_sentence[index].index('并'):
                    split_sentence[index] = split_sentence[index][split_sentence[index].index('并'):]

            if '转移' in split_sentence[index] and '转移' not in split_sentence[index-1]:
                list2.append(split_sentence[index-1])
                list2.append(split_sentence[index])

                if index>1 and '转移' not in split_sentence[index-2]:
                    list3.append(split_sentence[index-2])
                    list3.append(split_sentence[index-1])
                    list3.append(split_sentence[index])
            bi_sentence = ''
            tri_sentence = ''
            for ls in list2:
                bi_sentence = bi_sentence + ls + ','
            if len(bi_sentence)>0:
                bi_sentence = bi_sentence[:-1] + '.'
            for ls in list3:
                tri_sentence = tri_sentence + ls + ','
            if len(tri_sentence)>0:
                tri_sentence = tri_sentence[:-1] + '.'

            if len(daixie)>0:
                sentences.append(daixie)
            if len(bi_sentence)>0 and bi_sentence not in sentences:
                sentences.append(bi_sentence)
            
            if len(tri_sentence)>0 and tri_sentence not in sentences:
                sentences.append(tri_sentence)
            
            if '骨质破坏' in split_sentence[index] and '相邻胸骨' not in split_sentence[index] and '左侧第七后肋' not in split_sentence[index]:
                sentences.append(split_sentence[index-1]+','+split_sentence[index]+'.')
                sentences.append(split_sentence[index])
            
        sentence_path = os.path.join(parent_path,name)
        with open(sentence_path,'w',encoding='utf-8') as fr:
            for sen in sentences:
                fr.write(sen)
                fr.write('\n')

def get_single_sentence(path):
        lines = []
        
        with open(path,'r',encoding='utf-8') as fr:
            lines = fr.readlines()

        content = ''
        for line in lines:
            content += line
        
        content = content.replace('。',',')
        content = content.replace(':',',')
        content = content.replace('：',',')
        content = content.replace('；',',')
        content = content.replace(';',',')
        content = content.replace('，',',')
        content = content.replace('1.',',')
        content = content.replace('2.',',')
        content = content.replace('3.',',')
        content = content.replace('4.',',')
        content = content.replace('5.',',')
        content = content.replace('6.',',')
        content = content.replace('7.',',')
        content = content.replace(' 1.',',')
        content = content.replace(' 2.',',')
        content = content.replace(' 3.',',')
        content = content.replace(' 4.',',')
        content = content.replace(' 5.',',')
        content = content.replace(' 6.',',')
        content = content.replace(' 7.',',')

        split_sentence = content.split(',')
        temp_sentence = []
        for sen in split_sentence:
            if '转移' in sen:
                temp_sentence.append(sen.strip())
        return temp_sentence

if __name__=='__main__':
    Excelpath = os.path.join('.','data/CHIP2018测试数据.xlsx')
    path = os.path.join('.','data/EMR_info/EMR')
    split_EMR_into_sentence(path)