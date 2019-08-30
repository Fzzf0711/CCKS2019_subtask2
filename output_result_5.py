import xlwt, os, shutil

def fileload_test(path1, path2, path3,path4):
    
    book = xlwt.Workbook(encoding = 'utf-8') #创建一个Excel对象
    sheet1 = book.add_sheet('sheet1') #添加一个名为sheet1的sheet
    style = xlwt.XFStyle()
    
    sheet1.write(0, 0, '原文') #在索引为i, j处写入content
    sheet1.write(0, 1, '肿瘤原发部位') #在索引为i, j处写入content
    sheet1.write(0, 2, '原发病灶大小') #在索引为i, j处写入content
    sheet1.write(0, 3, '转移部位') #在索引为i, j处写入content
    total = 0
    
    for index in range(400):
        EMR_path = path1+'record-'+str(index+1)+'.txt'
        TUMOR_path = path2+'tumer-'+str(index+1)+'.txt'
        FOCUS_path = path3+'focus-'+str(index+1)+'.txt'
        METASTATIC_path = path4+'metastatic-'+str(index+1)+'.txt'

        EMR = []
        TUMOR = []
        FOCUS = []
        METASTATIC = []

        with open(EMR_path, encoding='utf-8') as fr1:
            lines = fr1.readlines()
            for line in lines:
                if len(line)>0:
                    EMR.append(line)
        fr1.close
        
        with open(TUMOR_path, encoding='utf-8') as fr2:
            lines = fr2.readlines()
            for line in lines:
                line = line.replace('\n','')
                if len(line)>0:
                    TUMOR.append(line)
        fr2.close
        
        
        with open(FOCUS_path, encoding='utf-8') as fr3:
            lines = fr3.readlines()
            for line in lines:
                line = line.replace('\n','')
                if len(line)>0:
                    FOCUS.append(line)
        fr3.close
        
        
        with open(METASTATIC_path, encoding='utf-8') as fr4:
            lines = fr4.readlines()
            for line in lines:
                line = line.replace('\n','')
                if len(line)>0:
                    METASTATIC.append(line)
        fr4.close

        TUMOR = list(set(TUMOR))
        FOCUS = list(set(FOCUS))
        METASTATIC = list(set(METASTATIC))
        total += ((len(TUMOR)+len(FOCUS)+len(METASTATIC)))
        
        if len(EMR)>0:
            sheet1.write(index+1, 0, EMR[0])
        if len(TUMOR)>0:
            tu = ''
            for t in TUMOR:
                tu = tu + t + ','
            tu = tu[:-1]
            sheet1.write(index+1, 1, tu)
        if len(FOCUS)>0:
            fo = ''
            for f in FOCUS:
                fo = fo + f + ','
            fo = fo[:-1]
            sheet1.write(index+1, 2, fo)
        if len(METASTATIC)>0:
            me = ''
            for m in METASTATIC:
                me = me + m +','
            me = me[:-1]
            sheet1.write(index+1, 3, me)
    print(total)
    book.save("output.xls") # 保存

if __name__ == '__main__':
    path1 = os.path.join('.','data/EMR_info/EMR/')   
    path2 = os.path.join('.','data/TUMER_SITE/')   
    path3 = os.path.join('.','data/FOCUS/')   
    path4 = os.path.join('.','data/METASTATIC_SITE/')   
    fileload_test(path1, path2, path3, path4)

