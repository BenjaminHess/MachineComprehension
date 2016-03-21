from nltk.tokenize import TreebankWordTokenizer
import nltk.data
import collections
import numpy


path='../data/MCTest/'

def tokenize(str):
    listt=TreebankWordTokenizer().tokenize(str)
    if listt[-1]=='.' or listt[-1]=='?':
        listt=listt[:-1]
    return ' '.join(listt)

def tokenize_answer(str):
    return ' '.join(TreebankWordTokenizer().tokenize(str))

def text2sents(text):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    text=text.replace('\\newline',' ').replace('\\tab',' ')
    sents=tokenizer.tokenize(text)
    new_text=''
    for sent in sents:
        tokenized_sent=tokenize(sent)
#         if tokenized_sent.find('Jimmy found more and more insects to add to his jar')>=0:
#             print tokenized_sent
#             print sent
#             print tokenized_sent.find('\\')
#             print sent.find('noise')
#             print sent[0], sent[1], sent[2], sent[3]
#             exit(0)
#         if tokenized_sent.find('\\newline')>=0:
#             print tokenized_sent
#             print tokenized_sent.replace('\newline','')
#             exit(0)
#         refined_sent=[]
#         for word in tokenized_sent.split():
#             if word=='?':
#                 continue
#             posi=word.find('.')
#             if posi>=0:
#                 if word[posi+1:posi+2].isupper() or (posi==len(word)-1 and word[0:1].islower()):
#                     word.replace('.','\t')
#             refined_sent.append(word)
#         tokenized_sent=' '.join(refined_sent)

        new_text+='\t'+tokenized_sent
    return new_text.strip()

def answer2sents(text):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    text=text.replace('\\newline',' ').replace('\\tab',' ')
    sents=tokenizer.tokenize(text)
    new_text=''
    for sent in sents:
        tokenized_sent=tokenize_answer(sent)
#         if tokenized_sent.find('Jimmy found more and more insects to add to his jar')>=0:
#             print tokenized_sent
#             print sent
#             print tokenized_sent.find('\\')
#             print sent.find('noise')
#             print sent[0], sent[1], sent[2], sent[3]
#             exit(0)
#         if tokenized_sent.find('\\newline')>=0:
#             print tokenized_sent
#             print tokenized_sent.replace('\newline','')
#             exit(0)
#         refined_sent=[]
#         for word in tokenized_sent.split():
#             if word=='?':
#                 continue
#             posi=word.find('.')
#             if posi>=0:
#                 if word[posi+1:posi+2].isupper() or (posi==len(word)-1 and word[0:1].islower()):
#                     word.replace('.','\t')
#             refined_sent.append(word)
#         tokenized_sent=' '.join(refined_sent)

        new_text+=' '+tokenized_sent
    words=new_text.strip().split()
    if words[-1]=='.' or words[-1]=='?':
        words=words[:-1]
    return ' '.join(words)

def standardlize(answerfile,inputfile):
    readfile=open(path+answerfile, 'r')
    answers=[]
    for line in readfile:
        answer=line.strip().split()
        int_answer=[]
        for ans in answer:
            if ans is 'A':
                int_answer.append(0)
            elif ans is 'B':
                int_answer.append(1)
            elif ans is 'C':
                int_answer.append(2)
            elif ans is 'D':
                int_answer.append(3)
        if len(int_answer)!=4:
            print 'len(int_answer)!=4'
            exit(0)
        answers.append(int_answer)
    readfile.close()
    readfile=open(path+inputfile, 'r')
    writefile=open(path+inputfile+'_standardlized.txt','w')
    line_no=0
    for line in readfile:
        parts=line.strip().split('\t')
        story=parts[2]
        QA1=parts[3:3+5]
        QA2=parts[8:8+5]
        QA3=parts[13:13+5]
        QA4=parts[18:18+5]
        corrent_answers=answers[line_no]
        for QA_ind, QA in enumerate([QA1, QA2, QA3, QA4]):
            colon=QA[0].index(':')
            label=QA[0][:colon]
            Q=QA[0][colon+1:].strip()
            label_int=1
            if label=='multiple':
                label_int=2
            for ans_ind, ans in enumerate(QA[1:]):
                if ans_ind==corrent_answers[QA_ind]:
                    writefile.write('1\t'+str(label_int)+'\t'+text2sents(story)+'\t'+answer2sents(Q)+'\t'+answer2sents(ans)+'\n')
                else:
                    writefile.write('0\t'+str(label_int)+'\t'+text2sents(story)+'\t'+answer2sents(Q)+'\t'+answer2sents(ans)+'\n')
        line_no+=1
    writefile.close()
    readfile.close()
    print 'reform over'

def length_sent_text():
    #max_sent_length 57 max_text_length 59
#     files=['mc500.train.tsv_standardlized.txt', 'mc500.dev.tsv_standardlized.txt','mc500.test.tsv_standardlized.txt','mc160.train.tsv_standardlized.txt', 'mc160.dev.tsv_standardlized.txt','mc160.test.tsv_standardlized.txt']
    #max_sent_length 57 max_text_length 59
#    files=['mc500.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt', 'mc500.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt','mc500.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt','mc160.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt', 'mc160.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt','mc160.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt']
    files=['mc500.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt', 'mc500.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt', 'mc500.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt',
           'mc160.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt', 'mc160.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt', 'mc160.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt']
    max_sent_length=0
    max_text_length=0
    sent_l2count=collections.defaultdict(int)
    for file in files:
        readfile=open(path+file,'r')
        for line in readfile:
            parts=line.strip().split('\t')
            text_l=len(parts)-5
            if text_l>max_text_length:
                max_text_length=text_l
            for sent in parts[1:]:
                sent_l=len(sent.strip().split())
                sent_l2count[sent_l]+=1
                if sent_l>max_sent_length:
                    max_sent_length=sent_l
        readfile.close()
    print 'max_sent_length',max_sent_length, 'max_text_length', max_text_length
#     print sent_l2count
def Extract_Vocab():
#    files=['mc500.train.tsv_standardlized.txt', 'mc500.dev.tsv_standardlized.txt','mc500.test.tsv_standardlized.txt','mc160.train.tsv_standardlized.txt', 'mc160.dev.tsv_standardlized.txt','mc160.test.tsv_standardlized.txt']
#    files=['mc500.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt', 'mc500.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt','mc500.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt','mc160.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt', 'mc160.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt','mc160.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt']
#     files=['mc500.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt', 'mc500.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt', 'mc500.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt',
#            'mc160.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt', 'mc160.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt', 'mc160.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_clean.txt']

    files=['mc500.train.tsv_standardlized.txt_DQAAAA.txt', 'mc500.dev.tsv_standardlized.txt_DQAAAA.txt', 'mc500.test.tsv_standardlized.txt_DQAAAA.txt',
           'mc160.train.tsv_standardlized.txt_DQAAAA.txt', 'mc160.dev.tsv_standardlized.txt_DQAAAA.txt', 'mc160.test.tsv_standardlized.txt_DQAAAA.txt']

    writeFile=open(path+'vocab_DQAAAA.txt', 'w')
    vocab={}
    count=0
    for file in files:
        readFile=open(path+file, 'r')
        for line in readFile:
            tokens=line.strip().lower().split('\t')#consider lowercase always
            sent_size=len(tokens)-1
            for i in range(sent_size):
                words=tokens[i+1].strip().split()
                for word in words:
                    key=vocab.get(word)
                    if key is None:
                        count+=1
                        vocab[word]=count
                        writeFile.write(str(count)+'\t'+word+'\n')

        readFile.close()
    writeFile.close()
    print 'total words: ', count

def transcate_word2vec():
    readFile=open('/mounts/data/proj/wenpeng/Dataset/word2vec_words_300d.txt', 'r')
    dim=300
    word2vec={}
    for line in readFile:
        tokens=line.strip().split()
        if len(tokens)<dim+1:
            continue
        else:
            word2vec[tokens[0]]=map(float, tokens[1:])
    readFile.close()
    print 'word2vec loaded over...'
    readFile=open(path+'vocab_DSSSS.txt', 'r')
    writeFile=open(path+'vocab_embs_300d_DSSSS.txt', 'w')
    random_emb=list(numpy.random.uniform(-0.01,0.01,dim))
    unk=0
    for line in readFile:
        tokens=line.strip().split()
        emb=word2vec.get(tokens[1])
        if emb is None:
            emb=word2vec.get(tokens[1].lower())
            if emb is None:
                emb=random_emb
                unk+=1
        writeFile.write(tokens[1]+'\t'+' '.join(map(str, emb))+'\n')
    writeFile.close()
    readFile.close()
    print 'word2vec trancate over, unk:', unk

def transcate_glove():
    readFile=open('/mounts/data/proj/wenpeng/Dataset/glove.6B.50d.txt', 'r')
    dim=50
    glove={}
    for line in readFile:
        tokens=line.strip().split()
        if len(tokens)<dim+1:
            continue
        else:
            glove[tokens[0]]=map(float, tokens[1:])
    readFile.close()
    print 'glove loaded over...'
    readFile=open(path+'vocab_DQAAAA.txt', 'r')
    writeFile=open(path+'vocab_DQAAAA_glove_50d.txt', 'w')
    #random_emb=list(numpy.random.uniform(-0.01,0.01,dim))
    unk=0
    for line in readFile:
        tokens=line.strip().split()
        emb=glove.get(tokens[1])
        if emb is None:
            emb=glove.get(tokens[1].lower())
            if emb is None:
                emb=list(numpy.random.uniform(-0.01,0.01,dim))
                unk+=1
        writeFile.write(tokens[1]+'\t'+' '.join(map(str, emb))+'\n')
    writeFile.close()
    readFile.close()
    print 'glove trancate over, unk:', unk

def change_DQA_into_DQAAAA():
    files=['mc500.train.tsv_standardlized.txt', 'mc500.dev.tsv_standardlized.txt', 'mc500.test.tsv_standardlized.txt',
           'mc160.train.tsv_standardlized.txt', 'mc160.dev.tsv_standardlized.txt', 'mc160.test.tsv_standardlized.txt']

    for filee in files:
        readfile=open(path+filee, 'r')
        writefile=open(path+filee+'_DQAAAA.txt', 'w')
        line_no=1
        batch=4
        posi=-1
        answers=[]
        for line in readfile:
            parts=line.strip().split('\t')
            y=parts[0]
            label=parts[1]
            D=parts[2:-2]
            Q=parts[-2]
            A=parts[-1]
            answers.append(A)
            if y=='1':
                posi=len(answers)-1
            if line_no%batch==1:
                writefile.write(label+'\t'+'\t'.join(D)+'\t'+Q+'\t')
            elif line_no%batch==0:#4 lines
                writefile.write(answers[posi])
                for index, answer in enumerate(answers):
                    if index!=posi:
                        writefile.write('\t'+answer)
                writefile.write('\n')
                del answers[:]
                posi=-1
            line_no+=1
        writefile.close()
        readfile.close()
    print 'over'


def change_DQAS_into_DSSSS(filee):
#    for filee in files:
        readfile=open(path+filee, 'r')
        writefile=open(path+filee+'_DSSSS.txt', 'w')
        line_no=1
        batch=4
        posi=-1
        answers=[]
        for line in readfile:
            parts=line.strip().split('\t')
            y=parts[0]
            label=parts[1]
            D=parts[2:-3]
#             Q=parts[-3]
            A=parts[-1]
            answers.append(A)
            if y=='1':
                posi=len(answers)-1
            if line_no%batch==1:
                writefile.write(label+'\t'+'\t'.join(D)+'\t')
            elif line_no%batch==0:#4 lines
                writefile.write(answers[posi])
                for index, answer in enumerate(answers):
                    if index!=posi:
                        writefile.write('\t'+answer)
                writefile.write('\n')
                del answers[:]
                posi=-1
            line_no+=1
        writefile.close()
        readfile.close()
    print 'over'

def combine_standardlize_statement(standfile, statefile):
    readstand=open(path+standfile, 'r')
    readstate=open(path+statefile, 'r')
    lines_stand=[]
    for line in readstand:
        lines_stand.append(line.strip())
    readstand.close()


    states=[]
    for line in readstate:
        parts=line.strip().split('\t')
        qa_part=parts[-20:]
        states_part=qa_part[1:1+4]+qa_part[6:6+4]+qa_part[11:11+4]+qa_part[16:16+4]
        states+=states_part
    readstate.close()
    writefile=open(path+standfile+'_with_state.txt', 'w')
    if len(lines_stand)!=len(states):
        print 'size not equal'
        exit(0)
    else:
        for i in range(len(lines_stand)):
            writefile.write(lines_stand[i]+'\t'+answer2sents(states[i])+'\n')
    writefile.close()
    print 'finished'

def change_DSSSS_to_DPN(inputfile):
    readfile=open(path+inputfile, 'r')
    writefile=open(path+inputfile+'_DPN.txt', 'w')
    for line in readfile:
        parts=line.strip().split('\t')
        head=parts[:-3]
        tail=parts[-3:]
        for i in range(3):
            writefile.write('\t'.join(head)+'\t'+tail[i]+'\n')
    writefile.close()
    readfile.close()
    print 'over'

def change_DPN_to_DPNQ(dpnfile, qfile):
    readfile=open(path+qfile, 'r')
    Q=[]
    line_no=0
    for line in readfile:
        q=line.strip().split('\t')[-3].strip()
        if line_no%4==0:
            Q.append(q)
        line_no+=1
    print 'len(Q):', len(Q)
    readfile.close()
    readfile=open(path+dpnfile, 'r')
    writefile=open(path+dpnfile+'_DPNQ.txt', 'w')
    line_no=0
    for line in readfile:
        writefile.write(line.strip()+'\t')
        q_index=line_no/3
        writefile.write(Q[q_index]+'\n')
        line_no+=1
    writefile.close()
    readfile.close
    print 'over'

def remove_noise_sents_DPN(infile):
    stopfile=open(path+'stopwords.txt', 'r')
    stops=set()
    for line in stopfile:
        stops.add(line.strip())
    stopfile.close()
    readfile=open(path+infile, 'r')
    writefile=open(path+infile+'_clean.txt', 'w')
    for line in readfile:
        parts=line.strip().lower().split('\t')  # from now, we use lowercase
        vocab=set(parts[-2].split()+parts[-1].split())-stops
        if len(vocab)==0:
            print 'all stop words in statements'
            print parts[-2], parts[-1]
            exit(0)
        writefile.write(parts[0].strip())
        valid_doc=False
        for sent in parts[1:-2]:
            sent_set=set(sent.split())-stops
            if len(sent_set & vocab)>0:
                writefile.write('\t'+sent)
                valid_doc=True
        if valid_doc is False:
            print 'empty doc', parts[-2], parts[-1]
            writefile.write('\t'+parts[1])# if all sentences are removed, only write the first one
        writefile.write('\t'+parts[-2]+'\t'+parts[-1]+'\n')
    writefile.close()
    readfile.close()
    print 'over'

def change_DPNQ_into_DPNQQClass():
    files=['mc500.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_DPNQ.txt',
           'mc500.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_DPNQ.txt',
           'mc500.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_DPNQ.txt',
           'mc160.train.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_DPNQ.txt',
           'mc160.dev.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_DPNQ.txt',
           'mc160.test.tsv_standardlized.txt_with_state.txt_DSSSS.txt_DPN.txt_DPNQ.txt']

    class2index={'how':0,'how much':1, 'how many':2, 'what':3,'who':4,'where':5,'which':6,'when':7,'whose':8,'why':9,'will':10} # totally 12 classes, including "other"


    for file in files:
        readfile=open(path+file, 'r')
        writefile=open(path+file+'__DPNQQClass.txt', 'w')
        for line in readfile:
            writefile.write(line.strip().lower())
            Q=line.strip().split('\t')[-1].lower()
            ind_set=[]
            for cls,index in class2index.iteritems():
                posi=Q.find(cls)
                if posi>=0:
                    ind_set.append(index)
            if len(ind_set)==0: # didnt find any indicator, then class is 'other':11
                ind_set.append(11)
            #remove some thing
            if len(ind_set)>=2:
                if 0 in ind_set and (1 in ind_set or 2 in ind_set):
                    ind_set.remove(0)
            writefile.write('\t'+str(ind_set[0])+'\n')
        readfile.close()
        writefile.close()
        print 'over'


def main():
    countLabels = ['mc160', 'mc500']
    stepLabels = ['train', 'dev', 'test']

    for countLabel in countLabels:
        for stepLabel in stepLabels:
            fname0 = path+'.'.join([countLabel, stepLabel, 'ans'])
            fname1 = fname0[:-3]+'tsv'
            standardlize(fname0, fname1) # prints 'reform over'
            fname2 = fname1+'_standardlized.txt'
            fname3 = path+''.join(['Statements/', cl, '.', sl, '.statements.tsv'])
            combine_standardlize_statement(fname2, fname3)
            fname4 = fname2+'_with_state.txt'
            change_DQAS_into_DSSSS(fname4) # appends '_DSSSS.txt'
            fname5 = fname4+'_DSSSS.txt'
            change_DSSSS_to_DPN(fname5)
            fname6 = fname5+'_DPN.txt'
            change_DPN_to_DPNQ(fname6, fname4)
            remove_noise_sents_DPN(fname6)

    length_sent_text()
    Extract_Vocab()
    transcate_word2vec()
    transcate_glove()
    change_DQA_into_DQAAAA()

    change_DPNQ_into_DPNQQClass()

if __name__ == '__main__':
    main()
