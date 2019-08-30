import tensorflow as tf
import numpy as np
import os, argparse, time, shutil, re
from LSTM_for_tumer.model import BiLSTM_CRF
from LSTM_for_tumer.utils import str2bool, get_logger, get_Tumer_entity, postprocess_tumerlist
from LSTM_for_tumer.datas import read_corpus, read_dictionary_random, read_dictionary_pretrain, tag2label, random_embedding, read_testdata, output_data, get_pretrained_embedding

## Session configuration
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # default: 0
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.2  # need ~700MB GPU memory


## hyperparameters
parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
parser.add_argument('--train_data', type=str, default='./LSTM_for_tumer/data_path', help='train data source')
parser.add_argument('--test_data', type=str, default='./LSTM_for_tumer/data_path', help='test data source')
parser.add_argument('--data_source', type=str, default='./data/EMR_info/EMR', help='test data file')
parser.add_argument('--output_source', type=str, default='./data/TUMER_SITE', help='test data file')
parser.add_argument('--batch_size', type=int, default=1, help='#sample of each minibatch')
parser.add_argument('--epoch', type=int, default=300, help='#epoch of training')
parser.add_argument('--hidden_dim', type=int, default=300, help='#dim of hidden state')   #原CHIP任务中10，使用12250模型时注意改回
parser.add_argument('--optimizer', type=str, default='Adam', help='Adam/Adadelta/Adagrad/RMSProp/Momentum/SGD')
parser.add_argument('--CRF', type=str2bool, default=True, help='use CRF at the top layer. if False, use Softmax')
parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
parser.add_argument('--clip', type=float, default=5.0, help='gradient clipping')
parser.add_argument('--dropout', type=float, default=0.5, help='dropout keep_prob')
parser.add_argument('--update_embedding', type=str2bool, default=True, help='update embedding during training')
parser.add_argument('--pretrain_embedding', type=str, default='random', help='use pretrained char embedding or init it randomly')
parser.add_argument('--embedding_dim', type=int, default=300, help='random init char embedding_dim')
parser.add_argument('--shuffle', type=str2bool, default=True, help='shuffle training data before each epoch')
parser.add_argument('--mode', type=str, default='demo', help='train/test/demo')
# parser.add_argument('--demo_model', type=str, default='1561619024', help='model for test and demo')
parser.add_argument('--demo_model', type=str, default='1559872221', help='model for test and demo')
args = parser.parse_args()

word2id = {}
## get char embeddings: randomly initilized character embeddings
if args.pretrain_embedding == 'random':
    word2id = read_dictionary_random(os.path.join('.', args.train_data, 'word2id.pkl'))
    embeddings = random_embedding(word2id, args.embedding_dim)
else:
    word2id = read_dictionary_pretrain(os.path.join('.', args.train_data, 'word2id2.pkl'))
    embedding_path = os.path.join('.', args.train_data, 'pretrain_embedding.npy')
    embeddings = get_pretrained_embedding(embedding_path, args.embedding_dim)
if args.mode != 'demo':
    train_path = os.path.join('.', args.train_data, 'train_data')
    test_path = os.path.join('.', args.test_data, 'test_data')
    train_data = read_corpus(train_path)
    test_data = read_corpus(test_path); test_size = len(test_data)


## paths setting
paths = {}
timestamp = str(int(time.time())) if args.mode == 'train' else args.demo_model
output_path = os.path.join('.', args.train_data+"_save", timestamp)
if not os.path.exists(output_path): os.makedirs(output_path)
summary_path = os.path.join(output_path, "summaries")
paths['summary_path'] = summary_path
if not os.path.exists(summary_path): os.makedirs(summary_path)

model_path = os.path.join(output_path, "checkpoints/")
if not os.path.exists(model_path): os.makedirs(model_path)
ckpt_prefix = os.path.join(model_path, "model")
paths['model_path'] = ckpt_prefix
result_path = os.path.join(output_path, "results")
paths['result_path'] = result_path
if not os.path.exists(result_path): os.makedirs(result_path)
log_path = os.path.join(result_path, "log.txt")
print(log_path)
paths['log_path'] = log_path
get_logger(log_path).info(str(args))

if args.mode == 'train':
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    model.train(train=train_data, dev=test_data)  # use test_data as the dev_data to see overfitting phenomena

elif args.mode == 'demo':
    ckpt_file = tf.train.latest_checkpoint(model_path)
    paths['model_path'] = ckpt_file
    
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    saver = tf.train.Saver()
    with tf.Session(config=config) as sess:
        saver.restore(sess, ckpt_file)

        if os.path.exists(args.data_source):

            filenames = os.listdir(args.data_source)
            
            if os.path.exists(args.output_source):
                shutil.rmtree(args.output_source,True)
            os.mkdir(args.output_source)

            flag = 0

            for f in filenames:

                seq = re.search('\d\d?\d?',f).group(0)
                f1 = 'tumer-'+seq+'.txt'

                EMR_path = './data/EMR_info/EMR/record-'+seq+'.txt'

                content = ''
                with open(EMR_path,'r',encoding='utf-8') as fr:
                    lines = fr.readlines()
                    for line in lines:
                        content += line
                fr.close

                testdata_path = os.path.join('.', args.data_source, f)
                outputdata_path = os.path.join('.', args.output_source, f1)
                
                demo_sent = read_testdata(testdata_path)
                demo_sent = demo_sent.replace('CA','MT')
                EMR = ''
                EMR += demo_sent
                
                demo_sent = list(demo_sent.strip())
                demo_data = [(demo_sent, ['O'] * len(demo_sent))]
                tag = model.demo_one(sess, demo_data)
                TUMER = get_Tumer_entity(tag, demo_sent)

                if len(TUMER)>0:
                    for tu in TUMER:
                        if '肺' in tu and tu.endswith('腺'):
                            TUMER.append(tu[:-2])
                            TUMER.remove(tu)
                        if tu.endswith('肠肠') or tu.endswith('叶叶') or tu.endswith('肉') or tu.endswith('管管'):
                            TUMER.append(tu[:-2])
                            if tu in TUMER:
                                TUMER.remove(tu)
                        if tu.endswith('近纵隔旁'):
                            TUMER.append(tu[:-4])
                            if tu in TUMER:
                                TUMER.remove(tu)
                        if tu.endswith('支气管'):
                            TUMER.append(tu[:-3])
                            if tu in TUMER:
                                TUMER.remove(tu)
                if len(TUMER)>0:
                    for tu in TUMER:
                        if tu.endswith('纵隔旁'):
                            TUMER.append(tu[:-3])
                            if tu in TUMER:
                                TUMER.remove(tu)
                        if '附件' in tu:
                            if tu in TUMER:
                                TUMER.remove(tu)

                TUMER_model = postprocess_tumerlist(TUMER)
                
                predict = TUMER_model
                temp_predict = []
                temp_predict.extend(predict)

                if len(predict)>1:
                    for p_comparing in temp_predict:
                        compos_comparing = set(p_comparing)
                        len_comparing = len(compos_comparing)
                        for p_compared in temp_predict:
                            compos_compared = set(p_compared)
                            len_compared = len(compos_compared)
                            merged = compos_compared | compos_comparing
                            len_merged = len(merged)
                            if len_merged > len_comparing and len_merged == len_compared:
                                if p_comparing in predict:
                                    predict.remove(p_comparing)
               
                cancer = ['肺']
                #,'肝','胃','肠','胰','食','卵'

                if len(predict)==2:
                    tumer1 = predict[0]
                    tumer2 = predict[1]
                    for c in cancer:
                        if c in tumer1 and c in tumer2:
                            if (tumer1+'癌') in EMR and not (tumer2+'癌') in EMR and tumer2 in predict:
                                predict.remove(tumer2)
                            if (tumer2+'癌') in EMR and not (tumer1+'癌') in EMR and tumer1 in predict:
                                predict.remove(tumer1)
                            if (tumer1+'中心型肺癌') in EMR and not (tumer2+'中心型肺癌') in EMR and tumer2 in predict:
                                predict.remove(tumer2)
                            if (tumer2+'中心型肺癌') in EMR and not (tumer1+'中心型肺癌') in EMR and tumer1 in predict:
                                predict.remove(tumer1)

                if len(predict)>0:
                    temp_list1 = []
                    temp_list2 = []
                    for tum in predict:
                        if '肺' in tum and len(tum)>3:
                            pattern = re.compile(tum+'\S?\S?\S?段')
                            m = pattern.findall(EMR)
                    
                            if len(m)>0:
                                flag = flag+1
                                if '，' not in m[0] and '、' not in m[0]:
                                    temp_list1.append(tum)
                                    temp_list2.append(m[0])

                    if len(temp_list1)>0:
                        for tum in temp_list1:
                            predict.remove(tum)
                        predict.extend(temp_list2)

                if len(predict)>0:
                    for p in predict:
                        if '肺' in p:
                            if (p+'切除') in EMR and p in predict:
                                predict.remove(p)
                        if p == '肝':
                            if '肝内' in EMR and p in predict:
                                predict.remove(p)
                                predict.append('肝内')

                if len(predict)>0:
                    for tumer in predict:
                        output_data(tumer, outputdata_path)
                else:
                    output_data('', outputdata_path)
            # print(flag)  
        else:
            print('原始电子病例不存在')

            
