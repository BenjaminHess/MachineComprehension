import cPickle
import gzip
import os
import sys
sys.setrecursionlimit(6000)
sys.path.insert(0, 'Thang')
import time

import numpy
import theano
import theano.tensor as T
import theano.sandbox.neighbours as TSN
import time

from logistic_sgd import LogisticRegression
from WPDefined import ConvFoldPoolLayer, dropout_from_layer, shared_dataset, repeat_whole_matrix
from cis.deep.utils.theano import debug_print
from theano.tensor.signal import downsample
from theano.tensor.nnet import conv
from loadData import load_MCTest_corpus_new, load_word2vec_to_init
from word2embeddings.nn.util import zero_value, random_value_normal
from common_functions import Conv_with_input_para, Conv_with_input_para_one_col_featuremap, Average_Pooling_for_Top, create_conv_para, Average_Pooling, create_highw_para, Average_Pooling_Scan
from random import shuffle

from sklearn import svm
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import LinearRegression
from sklearn import linear_model
from scipy import linalg, mat, dot

#from preprocess_wikiQA import compute_map_mrr

#need to change
'''
1) rouge score
2) TF-KLD

4) paragraph vector

6) tokenized sentences : better
7) only use non-overlap pairs

9) length of nonoverlap : better




Doesnt work:
3) train+trial
10) no not use mt metrics
5) update word embeddings
8) nonoverlap emb used average
10) delete original sentence lengths

'''

def evaluate_lenet5(learning_rate=0.09,
                    n_epochs=2000,
                    nkerns=[50,50],
                    batch_size=1,
                    window_width=3,
                    maxSentLength=64,
                    maxDocLength=60,
                    emb_size=300,
                    hidden_size=200,
                    L2_weight=0.00065,
                    update_freq=1,
                    norm_threshold=5.0,
                    max_s_length=57,
                    max_d_length=59,
                    margin=0.3
):
    maxSentLength=max_s_length+2*(window_width-1)
    maxDocLength=max_d_length+2*(window_width-1)
    model_options = locals().copy()
    print "model options", model_options
    rootPath='../data/MCTest/';
    rng = numpy.random.RandomState(23455)
    train_data,train_size, test_data, test_size, vocab_size=load_MCTest_corpus_new(
        rootPath+'vocab.txt',
        rootPath+'mc500.train.tsv_standardlized.txt',
        rootPath+'mc500.test.tsv_standardlized.txt',
        max_s_length,
        maxSentLength,
        maxDocLength
    )#vocab_size contain train, dev and test

    #datasets_nonoverlap, vocab_size_nonoverlap=load_SICK_corpus(rootPath+'vocab_nonoverlap_train_plus_dev.txt', rootPath+'train_plus_dev_removed_overlap_as_training.txt', rootPath+'test_removed_overlap_as_training.txt', max_truncate_nonoverlap,maxSentLength_nonoverlap, entailment=True)
    #datasets, vocab_size=load_wikiQA_corpus(rootPath+'vocab_lower_in_word2vec.txt', rootPath+'WikiQA-train.txt', rootPath+'test_filtered.txt', maxSentLength)#vocab_size contain train, dev and test
    #mtPath='/mounts/data/proj/wenpeng/Dataset/WikiQACorpus/MT/BLEU_NIST/'
#     mt_train, mt_test=load_mts_wikiQA(rootPath+'Train_plus_dev_MT/concate_14mt_train.txt', rootPath+'Test_MT/concate_14mt_test.txt')
#     extra_train, extra_test=load_extra_features(rootPath+'train_plus_dev_rule_features_cosine_eucli_negation_len1_len2_syn_hyper1_hyper2_anto(newsimi0.4).txt', rootPath+'test_rule_features_cosine_eucli_negation_len1_len2_syn_hyper1_hyper2_anto(newsimi0.4).txt')
#     discri_train, discri_test=load_extra_features(rootPath+'train_plus_dev_discri_features_0.3.txt', rootPath+'test_discri_features_0.3.txt')
    #wm_train, wm_test=load_wmf_wikiQA(rootPath+'train_word_matching_scores.txt', rootPath+'test_word_matching_scores.txt')
    #wm_train, wm_test=load_wmf_wikiQA(rootPath+'train_word_matching_scores_normalized.txt', rootPath+'test_word_matching_scores_normalized.txt')

# results=[numpy.array(data_D), numpy.array(data_Q), numpy.array(data_A1), numpy.array(data_A2), numpy.array(data_A3), numpy.array(data_A4), numpy.array(Label),
#          numpy.array(Length_D),numpy.array(Length_D_s), numpy.array(Length_Q), numpy.array(Length_A1), numpy.array(Length_A2), numpy.array(Length_A3), numpy.array(Length_A4),
#         numpy.array(leftPad_D),numpy.array(leftPad_D_s), numpy.array(leftPad_Q), numpy.array(leftPad_A1), numpy.array(leftPad_A2), numpy.array(leftPad_A3), numpy.array(leftPad_A4),
#         numpy.array(rightPad_D),numpy.array(rightPad_D_s), numpy.array(rightPad_Q), numpy.array(rightPad_A1), numpy.array(rightPad_A2), numpy.array(rightPad_A3), numpy.array(rightPad_A4)]
# return results, line_control
    [train_data_D, train_data_Q, train_data_A1, train_data_A2, train_data_A3, train_data_A4, train_Label,
                 train_Length_D,train_Length_D_s, train_Length_Q, train_Length_A1, train_Length_A2, train_Length_A3, train_Length_A4,
                train_leftPad_D,train_leftPad_D_s, train_leftPad_Q, train_leftPad_A1, train_leftPad_A2, train_leftPad_A3, train_leftPad_A4,
                train_rightPad_D,train_rightPad_D_s, train_rightPad_Q, train_rightPad_A1, train_rightPad_A2, train_rightPad_A3, train_rightPad_A4]=train_data
    [test_data_D, test_data_Q, test_data_A1, test_data_A2, test_data_A3, test_data_A4, test_Label,
                 test_Length_D,test_Length_D_s, test_Length_Q, test_Length_A1, test_Length_A2, test_Length_A3, test_Length_A4,
                test_leftPad_D,test_leftPad_D_s, test_leftPad_Q, test_leftPad_A1, test_leftPad_A2, test_leftPad_A3, test_leftPad_A4,
                test_rightPad_D,test_rightPad_D_s, test_rightPad_Q, test_rightPad_A1, test_rightPad_A2, test_rightPad_A3, test_rightPad_A4]=test_data


    n_train_batches=train_size/batch_size
    n_test_batches=test_size/batch_size

    train_batch_start=list(numpy.arange(n_train_batches)*batch_size)
    test_batch_start=list(numpy.arange(n_test_batches)*batch_size)


#     indices_train_l=theano.shared(numpy.asarray(indices_train_l, dtype=theano.config.floatX), borrow=True)
#     indices_train_r=theano.shared(numpy.asarray(indices_train_r, dtype=theano.config.floatX), borrow=True)
#     indices_test_l=theano.shared(numpy.asarray(indices_test_l, dtype=theano.config.floatX), borrow=True)
#     indices_test_r=theano.shared(numpy.asarray(indices_test_r, dtype=theano.config.floatX), borrow=True)
#     indices_train_l=T.cast(indices_train_l, 'int64')
#     indices_train_r=T.cast(indices_train_r, 'int64')
#     indices_test_l=T.cast(indices_test_l, 'int64')
#     indices_test_r=T.cast(indices_test_r, 'int64')



    rand_values=random_value_normal((vocab_size+1, emb_size), theano.config.floatX, numpy.random.RandomState(1234))
    rand_values[0]=numpy.array(numpy.zeros(emb_size),dtype=theano.config.floatX)
    #rand_values[0]=numpy.array([1e-50]*emb_size)
    rand_values=load_word2vec_to_init(rand_values, rootPath+'vocab_embs_300d.txt')
    #rand_values=load_word2vec_to_init(rand_values, rootPath+'vocab_lower_in_word2vec_embs_300d.txt')
    embeddings=theano.shared(value=rand_values, borrow=True)

    #cost_tmp=0
    error_sum=0

    # allocate symbolic variables for the data
    index = T.lscalar()
    index_D = T.lmatrix()   # now, x is the index matrix, must be integer
    index_Q = T.lvector()
    index_A1= T.lvector()
    index_A2= T.lvector()
    index_A3= T.lvector()
    index_A4= T.lvector()
#     y = T.lvector()

    len_D=T.lscalar()
    len_D_s=T.lvector()
    len_Q=T.lscalar()
    len_A1=T.lscalar()
    len_A2=T.lscalar()
    len_A3=T.lscalar()
    len_A4=T.lscalar()

    left_D=T.lscalar()
    left_D_s=T.lvector()
    left_Q=T.lscalar()
    left_A1=T.lscalar()
    left_A2=T.lscalar()
    left_A3=T.lscalar()
    left_A4=T.lscalar()

    right_D=T.lscalar()
    right_D_s=T.lvector()
    right_Q=T.lscalar()
    right_A1=T.lscalar()
    right_A2=T.lscalar()
    right_A3=T.lscalar()
    right_A4=T.lscalar()



    #x=embeddings[x_index.flatten()].reshape(((batch_size*4),maxSentLength, emb_size)).transpose(0, 2, 1).flatten()
    ishape = (emb_size, maxSentLength)  # sentence shape
    dshape = (nkerns[0], maxDocLength) # doc shape
    filter_words=(emb_size,window_width)
    filter_sents=(nkerns[0], window_width)
    #poolsize1=(1, ishape[1]-filter_size[1]+1) #?????????????????????????????
#     length_after_wideConv=ishape[1]+filter_size[1]-1

    ######################
    # BUILD ACTUAL MODEL #
    ######################
    print '... building the model'

    # Reshape matrix of rasterized images of shape (batch_size,28*28)
    # to a 4D tensor, compatible with our LeNetConvPoolLayer
    #layer0_input = x.reshape(((batch_size*4), 1, ishape[0], ishape[1]))
    layer0_D_input = embeddings[index_D.flatten()].reshape((maxDocLength,maxSentLength, emb_size)).transpose(0, 2, 1).dimshuffle(0, 'x', 1, 2)
    layer0_Q_input = embeddings[index_Q.flatten()].reshape((batch_size,maxSentLength, emb_size)).transpose(0, 2, 1).dimshuffle(0, 'x', 1, 2)
    layer0_A1_input = embeddings[index_A1.flatten()].reshape((batch_size,maxSentLength, emb_size)).transpose(0, 2, 1).dimshuffle(0, 'x', 1, 2)
    layer0_A2_input = embeddings[index_A2.flatten()].reshape((batch_size,maxSentLength, emb_size)).transpose(0, 2, 1).dimshuffle(0, 'x', 1, 2)
    layer0_A3_input = embeddings[index_A3.flatten()].reshape((batch_size,maxSentLength, emb_size)).transpose(0, 2, 1).dimshuffle(0, 'x', 1, 2)
    layer0_A4_input = embeddings[index_A4.flatten()].reshape((batch_size,maxSentLength, emb_size)).transpose(0, 2, 1).dimshuffle(0, 'x', 1, 2)


    conv_W, conv_b=create_conv_para(rng, filter_shape=(nkerns[0], 1, filter_words[0], filter_words[1]))
#     load_model_for_conv1([conv_W, conv_b])

    layer0_D = Conv_with_input_para(rng, input=layer0_D_input,
            image_shape=(maxDocLength, 1, ishape[0], ishape[1]),
            filter_shape=(nkerns[0], 1, filter_words[0], filter_words[1]), W=conv_W, b=conv_b)
    layer0_Q = Conv_with_input_para(rng, input=layer0_Q_input,
            image_shape=(batch_size, 1, ishape[0], ishape[1]),
            filter_shape=(nkerns[0], 1, filter_words[0], filter_words[1]), W=conv_W, b=conv_b)
    layer0_A1 = Conv_with_input_para(rng, input=layer0_A1_input,
            image_shape=(batch_size, 1, ishape[0], ishape[1]),
            filter_shape=(nkerns[0], 1, filter_words[0], filter_words[1]), W=conv_W, b=conv_b)
    layer0_A2 = Conv_with_input_para(rng, input=layer0_A2_input,
            image_shape=(batch_size, 1, ishape[0], ishape[1]),
            filter_shape=(nkerns[0], 1, filter_words[0], filter_words[1]), W=conv_W, b=conv_b)
    layer0_A3 = Conv_with_input_para(rng, input=layer0_A3_input,
            image_shape=(batch_size, 1, ishape[0], ishape[1]),
            filter_shape=(nkerns[0], 1, filter_words[0], filter_words[1]), W=conv_W, b=conv_b)
    layer0_A4 = Conv_with_input_para(rng, input=layer0_A4_input,
            image_shape=(batch_size, 1, ishape[0], ishape[1]),
            filter_shape=(nkerns[0], 1, filter_words[0], filter_words[1]), W=conv_W, b=conv_b)

    layer0_D_output=debug_print(layer0_D.output, 'layer0_D.output')
    layer0_Q_output=debug_print(layer0_Q.output, 'layer0_Q.output')
    layer0_A1_output=debug_print(layer0_A1.output, 'layer0_A1.output')
    layer0_A2_output=debug_print(layer0_A2.output, 'layer0_A2.output')
    layer0_A3_output=debug_print(layer0_A3.output, 'layer0_A3.output')
    layer0_A4_output=debug_print(layer0_A4.output, 'layer0_A4.output')
    layer0_para=[conv_W, conv_b]

    layer1_DQ=Average_Pooling_Scan(rng, input_D=layer0_D_output, input_r=layer0_Q_output, kern=nkerns[0],
                                      left_D=left_D, right_D=right_D,
                     left_D_s=left_D_s, right_D_s=right_D_s, left_r=left_Q, right_r=right_Q,
                      length_D_s=len_D_s+filter_words[1]-1, length_r=len_Q+filter_words[1]-1,
                       dim=maxSentLength+filter_words[1]-1, doc_len=maxDocLength, topk=3)
    layer1_DA1=Average_Pooling_Scan(rng, input_D=layer0_D_output, input_r=layer0_A1_output, kern=nkerns[0],
                                      left_D=left_D, right_D=right_D,
                     left_D_s=left_D_s, right_D_s=right_D_s, left_r=left_A1, right_r=right_A1,
                      length_D_s=len_D_s+filter_words[1]-1, length_r=len_A1+filter_words[1]-1,
                       dim=maxSentLength+filter_words[1]-1, doc_len=maxDocLength, topk=3)
    layer1_DA2=Average_Pooling_Scan(rng, input_D=layer0_D_output, input_r=layer0_A2_output, kern=nkerns[0],
                                      left_D=left_D, right_D=right_D,
                     left_D_s=left_D_s, right_D_s=right_D_s, left_r=left_A2, right_r=right_A2,
                      length_D_s=len_D_s+filter_words[1]-1, length_r=len_A2+filter_words[1]-1,
                       dim=maxSentLength+filter_words[1]-1, doc_len=maxDocLength, topk=3)
    layer1_DA3=Average_Pooling_Scan(rng, input_D=layer0_D_output, input_r=layer0_A3_output, kern=nkerns[0],
                                      left_D=left_D, right_D=right_D,
                     left_D_s=left_D_s, right_D_s=right_D_s, left_r=left_A3, right_r=right_A3,
                      length_D_s=len_D_s+filter_words[1]-1, length_r=len_A3+filter_words[1]-1,
                       dim=maxSentLength+filter_words[1]-1, doc_len=maxDocLength, topk=3)
    layer1_DA4=Average_Pooling_Scan(rng, input_D=layer0_D_output, input_r=layer0_A4_output, kern=nkerns[0],
                                      left_D=left_D, right_D=right_D,
                     left_D_s=left_D_s, right_D_s=right_D_s, left_r=left_A4, right_r=right_A4,
                      length_D_s=len_D_s+filter_words[1]-1, length_r=len_A4+filter_words[1]-1,
                       dim=maxSentLength+filter_words[1]-1, doc_len=maxDocLength, topk=3)

    conv2_W, conv2_b=create_conv_para(rng, filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]))
    #load_model_for_conv2([conv2_W, conv2_b])#this can not be used, as the nkerns[0]!=filter_size[0]
    #conv from sentence to doc
    layer2_DQ = Conv_with_input_para(rng, input=layer1_DQ.output_D.reshape((batch_size, 1, nkerns[0], dshape[1])),
            image_shape=(batch_size, 1, nkerns[0], dshape[1]),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    layer2_DA1 = Conv_with_input_para(rng, input=layer1_DA1.output_D.reshape((batch_size, 1, nkerns[0], dshape[1])),
            image_shape=(batch_size, 1, nkerns[0], dshape[1]),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    layer2_DA2 = Conv_with_input_para(rng, input=layer1_DA2.output_D.reshape((batch_size, 1, nkerns[0], dshape[1])),
            image_shape=(batch_size, 1, nkerns[0], dshape[1]),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    layer2_DA3 = Conv_with_input_para(rng, input=layer1_DA3.output_D.reshape((batch_size, 1, nkerns[0], dshape[1])),
            image_shape=(batch_size, 1, nkerns[0], dshape[1]),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    layer2_DA4 = Conv_with_input_para(rng, input=layer1_DA4.output_D.reshape((batch_size, 1, nkerns[0], dshape[1])),
            image_shape=(batch_size, 1, nkerns[0], dshape[1]),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    #conv single Q and A into doc level with same conv weights
    layer2_Q = Conv_with_input_para_one_col_featuremap(rng, input=layer1_DQ.output_QA_sent_level_rep.reshape((batch_size, 1, nkerns[0], 1)),
            image_shape=(batch_size, 1, nkerns[0], 1),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    layer2_A1 = Conv_with_input_para_one_col_featuremap(rng, input=layer1_DA1.output_QA_sent_level_rep.reshape((batch_size, 1, nkerns[0], 1)),
            image_shape=(batch_size, 1, nkerns[0], 1),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    layer2_A2 = Conv_with_input_para_one_col_featuremap(rng, input=layer1_DA2.output_QA_sent_level_rep.reshape((batch_size, 1, nkerns[0], 1)),
            image_shape=(batch_size, 1, nkerns[0], 1),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    layer2_A3 = Conv_with_input_para_one_col_featuremap(rng, input=layer1_DA3.output_QA_sent_level_rep.reshape((batch_size, 1, nkerns[0], 1)),
            image_shape=(batch_size, 1, nkerns[0], 1),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    layer2_A4 = Conv_with_input_para_one_col_featuremap(rng, input=layer1_DA4.output_QA_sent_level_rep.reshape((batch_size, 1, nkerns[0], 1)),
            image_shape=(batch_size, 1, nkerns[0], 1),
            filter_shape=(nkerns[1], 1, nkerns[0], filter_sents[1]), W=conv2_W, b=conv2_b)
    layer2_Q_output_sent_rep_Dlevel=debug_print(layer2_Q.output_sent_rep_Dlevel, 'layer2_Q.output_sent_rep_Dlevel')
    layer2_A1_output_sent_rep_Dlevel=debug_print(layer2_A1.output_sent_rep_Dlevel, 'layer2_A1.output_sent_rep_Dlevel')
    layer2_A2_output_sent_rep_Dlevel=debug_print(layer2_A2.output_sent_rep_Dlevel, 'layer2_A2.output_sent_rep_Dlevel')
    layer2_A3_output_sent_rep_Dlevel=debug_print(layer2_A3.output_sent_rep_Dlevel, 'layer2_A3.output_sent_rep_Dlevel')
    layer2_A4_output_sent_rep_Dlevel=debug_print(layer2_A4.output_sent_rep_Dlevel, 'layer2_A4.output_sent_rep_Dlevel')
    layer2_para=[conv2_W, conv2_b]

    layer3_DQ=Average_Pooling_for_Top(rng, input_l=layer2_DQ.output, input_r=layer2_Q_output_sent_rep_Dlevel, kern=nkerns[1],
                     left_l=left_D, right_l=right_D, left_r=0, right_r=0,
                      length_l=len_D+filter_sents[1]-1, length_r=1,
                       dim=maxDocLength+filter_sents[1]-1, topk=3)
    layer3_DA1=Average_Pooling_for_Top(rng, input_l=layer2_DA1.output, input_r=layer2_A1_output_sent_rep_Dlevel, kern=nkerns[1],
                     left_l=left_D, right_l=right_D, left_r=0, right_r=0,
                      length_l=len_D+filter_sents[1]-1, length_r=1,
                       dim=maxDocLength+filter_sents[1]-1, topk=3)
    layer3_DA2=Average_Pooling_for_Top(rng, input_l=layer2_DA2.output, input_r=layer2_A2_output_sent_rep_Dlevel, kern=nkerns[1],
                     left_l=left_D, right_l=right_D, left_r=0, right_r=0,
                      length_l=len_D+filter_sents[1]-1, length_r=1,
                       dim=maxDocLength+filter_sents[1]-1, topk=3)
    layer3_DA3=Average_Pooling_for_Top(rng, input_l=layer2_DA3.output, input_r=layer2_A3_output_sent_rep_Dlevel, kern=nkerns[1],
                     left_l=left_D, right_l=right_D, left_r=0, right_r=0,
                      length_l=len_D+filter_sents[1]-1, length_r=1,
                       dim=maxDocLength+filter_sents[1]-1, topk=3)
    layer3_DA4=Average_Pooling_for_Top(rng, input_l=layer2_DA4.output, input_r=layer2_A4_output_sent_rep_Dlevel, kern=nkerns[1],
                     left_l=left_D, right_l=right_D, left_r=0, right_r=0,
                      length_l=len_D+filter_sents[1]-1, length_r=1,
                       dim=maxDocLength+filter_sents[1]-1, topk=3)

    #high-way
    high_W, high_b=create_highw_para(rng, nkerns[0], nkerns[1])
    transform_gate_DQ=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DQ.output_D_sent_level_rep) + high_b), 'transform_gate_DQ')
    transform_gate_DA1=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DA1.output_D_sent_level_rep) + high_b), 'transform_gate_DA1')
    transform_gate_DA2=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DA2.output_D_sent_level_rep) + high_b), 'transform_gate_DA2')
    transform_gate_DA3=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DA3.output_D_sent_level_rep) + high_b), 'transform_gate_DA3')
    transform_gate_DA4=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DA4.output_D_sent_level_rep) + high_b), 'transform_gate_DA4')
    transform_gate_Q=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DQ.output_QA_sent_level_rep) + high_b), 'transform_gate_Q')
    transform_gate_A1=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DA1.output_QA_sent_level_rep) + high_b), 'transform_gate_A1')
    transform_gate_A2=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DA2.output_QA_sent_level_rep) + high_b), 'transform_gate_A2')
    transform_gate_A3=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DA3.output_QA_sent_level_rep) + high_b), 'transform_gate_A3')
    transform_gate_A4=debug_print(T.nnet.sigmoid(T.dot(high_W, layer1_DA4.output_QA_sent_level_rep) + high_b), 'transform_gate_A4')
    highW_para=[high_W, high_b]

    overall_D_Q=debug_print((1.0-transform_gate_DQ)*layer1_DQ.output_D_sent_level_rep+transform_gate_DQ*layer3_DQ.output_D_doc_level_rep, 'overall_D_Q')
    overall_D_A1=(1.0-transform_gate_DA1)*layer1_DA1.output_D_sent_level_rep+transform_gate_DA1*layer3_DA1.output_D_doc_level_rep
    overall_D_A2=(1.0-transform_gate_DA2)*layer1_DA2.output_D_sent_level_rep+transform_gate_DA2*layer3_DA2.output_D_doc_level_rep
    overall_D_A3=(1.0-transform_gate_DA3)*layer1_DA3.output_D_sent_level_rep+transform_gate_DA3*layer3_DA3.output_D_doc_level_rep
    overall_D_A4=(1.0-transform_gate_DA4)*layer1_DA4.output_D_sent_level_rep+transform_gate_DA4*layer3_DA4.output_D_doc_level_rep

    overall_Q=(1.0-transform_gate_Q)*layer1_DQ.output_QA_sent_level_rep+transform_gate_Q*layer2_Q.output_sent_rep_Dlevel
    overall_A1=(1.0-transform_gate_A1)*layer1_DA1.output_QA_sent_level_rep+transform_gate_A1*layer2_A1.output_sent_rep_Dlevel
    overall_A2=(1.0-transform_gate_A2)*layer1_DA2.output_QA_sent_level_rep+transform_gate_A2*layer2_A2.output_sent_rep_Dlevel
    overall_A3=(1.0-transform_gate_A3)*layer1_DA3.output_QA_sent_level_rep+transform_gate_A3*layer2_A3.output_sent_rep_Dlevel
    overall_A4=(1.0-transform_gate_A4)*layer1_DA4.output_QA_sent_level_rep+transform_gate_A4*layer2_A4.output_sent_rep_Dlevel

#     simi_sent_level=debug_print(cosine(layer1_DQ.output_D_sent_level_rep+layer1_DA.output_D_sent_level_rep, layer1_DQ.output_QA_sent_level_rep+layer1_DA.output_QA_sent_level_rep), 'simi_sent_level')
#     simi_doc_level=debug_print(cosine(layer3_DQ.output_D_doc_level_rep+layer3_DA.output_D_doc_level_rep, layer2_Q.output_sent_rep_Dlevel+layer2_A.output_sent_rep_Dlevel), 'simi_doc_level')
    simi_overall_level1=debug_print(cosine(overall_D_Q+overall_D_A1, overall_Q+overall_A1), 'simi_overall_level1')
    simi_overall_level2=debug_print(cosine(overall_D_Q+overall_D_A2, overall_Q+overall_A2), 'simi_overall_level2')
    simi_overall_level3=debug_print(cosine(overall_D_Q+overall_D_A3, overall_Q+overall_A3), 'simi_overall_level3')
    simi_overall_level4=debug_print(cosine(overall_D_Q+overall_D_A4, overall_Q+overall_A4), 'simi_overall_level4')
#     simi_overall_level1=debug_print(1.0/(1.0+EUCLID(overall_D_Q+overall_D_A1, overall_Q+overall_A1)), 'simi_overall_level1')
#     simi_overall_level2=debug_print(1.0/(1.0+EUCLID(overall_D_Q+overall_D_A2, overall_Q+overall_A2)), 'simi_overall_level2')
#     simi_overall_level3=debug_print(1.0/(1.0+EUCLID(overall_D_Q+overall_D_A3, overall_Q+overall_A3)), 'simi_overall_level3')
#     simi_overall_level4=debug_print(1.0/(1.0+EUCLID(overall_D_Q+overall_D_A4, overall_Q+overall_A4)), 'simi_overall_level4')


#     eucli_1=1.0/(1.0+EUCLID(layer3_DQ.output_D+layer3_DA.output_D, layer3_DQ.output_QA+layer3_DA.output_QA))






#     layer4_input=debug_print(T.concatenate([simi_sent_level,
#                                 simi_doc_level,
#                                 simi_overall_level
#                                 ], axis=1), 'layer4_input')#, layer2.output, layer1.output_cosine], axis=1)
#     #layer3_input=T.concatenate([mts,eucli, uni_cosine, len_l, len_r, norm_uni_l-(norm_uni_l+norm_uni_r)/2], axis=1)
#     #layer3=LogisticRegression(rng, input=layer3_input, n_in=11, n_out=2)
#     layer4=LogisticRegression(rng, input=layer4_input, n_in=3, n_out=2)

    #L2_reg =(layer3.W** 2).sum()+(layer2.W** 2).sum()+(layer1.W** 2).sum()+(conv_W** 2).sum()
    L2_reg =debug_print((high_W**2).sum()+(conv2_W**2).sum()+(conv_W**2).sum(), 'L2_reg')#+(layer1.W** 2).sum()++(embeddings**2).sum()

    cost=T.maximum(0.0, margin+T.max([simi_overall_level2, simi_overall_level3, simi_overall_level4])-simi_overall_level1) # ranking loss: max(0, margin-nega+posi)
    cost=debug_print(cost+L2_weight*L2_reg, 'cost')
    #cost=debug_print((cost_this+cost_tmp)/update_freq, 'cost')

    posi_simi=simi_overall_level1
    nega_simi=T.max([simi_overall_level2, simi_overall_level3, simi_overall_level4])


    test_model = theano.function([index], [cost, posi_simi, nega_simi],
          givens={
            index_D: test_data_D[index], #a matrix
            index_Q: test_data_Q[index],
            index_A1: test_data_A1[index],
            index_A2: test_data_A2[index],
            index_A3: test_data_A3[index],
            index_A4: test_data_A4[index],

            len_D: test_Length_D[index],
            len_D_s: test_Length_D_s[index],
            len_Q: test_Length_Q[index],
            len_A1: test_Length_A1[index],
            len_A2: test_Length_A2[index],
            len_A3: test_Length_A3[index],
            len_A4: test_Length_A4[index],

            left_D: test_leftPad_D[index],
            left_D_s: test_leftPad_D_s[index],
            left_Q: test_leftPad_Q[index],
            left_A1: test_leftPad_A1[index],
            left_A2: test_leftPad_A2[index],
            left_A3: test_leftPad_A3[index],
            left_A4: test_leftPad_A4[index],

            right_D: test_rightPad_D[index],
            right_D_s: test_rightPad_D_s[index],
            right_Q: test_rightPad_Q[index],
            right_A1: test_rightPad_A1[index],
            right_A2: test_rightPad_A2[index],
            right_A3: test_rightPad_A3[index],
            right_A4: test_rightPad_A4[index]

            }, on_unused_input='ignore')


    #params = layer3.params + layer2.params + layer1.params+ [conv_W, conv_b]
    params = layer2_para+layer0_para+highW_para

    accumulator=[]
    for para_i in params:
        eps_p=numpy.zeros_like(para_i.get_value(borrow=True),dtype=theano.config.floatX)
        accumulator.append(theano.shared(eps_p, borrow=True))

    # create a list of gradients for all model parameters
    grads = T.grad(cost, params)

    updates = []
    for param_i, grad_i, acc_i in zip(params, grads, accumulator):
        grad_i=debug_print(grad_i,'grad_i')
        acc = acc_i + T.sqr(grad_i)
        updates.append((param_i, param_i - learning_rate * grad_i / T.sqrt(acc)))   #AdaGrad
        updates.append((acc_i, acc))



    train_model = theano.function([index], [cost, posi_simi, nega_simi], updates=updates,
          givens={
            index_D: train_data_D[index],
            index_Q: train_data_Q[index],
            index_A1: train_data_A1[index],
            index_A2: train_data_A2[index],
            index_A3: train_data_A3[index],
            index_A4: train_data_A4[index],

            len_D: train_Length_D[index],
            len_D_s: train_Length_D_s[index],
            len_Q: train_Length_Q[index],
            len_A1: train_Length_A1[index],
            len_A2: train_Length_A2[index],
            len_A3: train_Length_A3[index],
            len_A4: train_Length_A4[index],

            left_D: train_leftPad_D[index],
            left_D_s: train_leftPad_D_s[index],
            left_Q: train_leftPad_Q[index],
            left_A1: train_leftPad_A1[index],
            left_A2: train_leftPad_A2[index],
            left_A3: train_leftPad_A3[index],
            left_A4: train_leftPad_A4[index],

            right_D: train_rightPad_D[index],
            right_D_s: train_rightPad_D_s[index],
            right_Q: train_rightPad_Q[index],
            right_A1: train_rightPad_A1[index],
            right_A2: train_rightPad_A2[index],
            right_A3: train_rightPad_A3[index],
            right_A4: train_rightPad_A4[index]
            }, on_unused_input='ignore')

    train_model_predict = theano.function([index], [cost, posi_simi, nega_simi],
          givens={
            index_D: train_data_D[index],
            index_Q: train_data_Q[index],
            index_A1: train_data_A1[index],
            index_A2: train_data_A2[index],
            index_A3: train_data_A3[index],
            index_A4: train_data_A4[index],

            len_D: train_Length_D[index],
            len_D_s: train_Length_D_s[index],
            len_Q: train_Length_Q[index],
            len_A1: train_Length_A1[index],
            len_A2: train_Length_A2[index],
            len_A3: train_Length_A3[index],
            len_A4: train_Length_A4[index],

            left_D: train_leftPad_D[index],
            left_D_s: train_leftPad_D_s[index],
            left_Q: train_leftPad_Q[index],
            left_A1: train_leftPad_A1[index],
            left_A2: train_leftPad_A2[index],
            left_A3: train_leftPad_A3[index],
            left_A4: train_leftPad_A4[index],

            right_D: train_rightPad_D[index],
            right_D_s: train_rightPad_D_s[index],
            right_Q: train_rightPad_Q[index],
            right_A1: train_rightPad_A1[index],
            right_A2: train_rightPad_A2[index],
            right_A3: train_rightPad_A3[index],
            right_A4: train_rightPad_A4[index]
            }, on_unused_input='ignore')



    ###############
    # TRAIN MODEL #
    ###############
    print '... training'
    # early-stopping parameters
    patience = 500000000000000  # look as this many examples regardless
    patience_increase = 2  # wait this much longer when a new best is
                           # found
    improvement_threshold = 0.995  # a relative improvement of this much is
                                   # considered significant
    validation_frequency = min(n_train_batches, patience / 2)
                                  # go through this many
                                  # minibatche before checking the network
                                  # on the validation set; in this case we
                                  # check every epoch

    best_params = None
    best_validation_loss = numpy.inf
    best_iter = 0
    test_score = 0.
    start_time = time.clock()
    mid_time = start_time

    epoch = 0
    done_looping = False

    max_acc=0.0
    best_epoch=0

    while (epoch < n_epochs) and (not done_looping):
        epoch = epoch + 1
        #for minibatch_index in xrange(n_train_batches): # each batch
        minibatch_index=0
        #shuffle(train_batch_start)#shuffle training data

#         readfile=open('/mounts/data/proj/wenpeng/Dataset/SICK/train_plus_dev.txt', 'r')
#         train_pairs=[]
#         train_y=[]
#         for line in readfile:
#             tokens=line.strip().split('\t')
#             listt=tokens[0]+'\t'+tokens[1]
#             train_pairs.append(listt)
#             train_y.append(tokens[2])
#         readfile.close()
#         writefile=open('/mounts/data/proj/wenpeng/Dataset/SICK/weights_fine_tune.txt', 'w')
        corr_train=0
        for batch_start in train_batch_start:
            # iter means how many batches have been runed, taking into loop
            iter = (epoch - 1) * n_train_batches + minibatch_index +1
            sys.stdout.write( "Training :[%6f] %% complete!\r" % (batch_start*100.0/train_size) )
            sys.stdout.flush()
            minibatch_index=minibatch_index+1

            cost_average, posi_simi, nega_simi= train_model(batch_start)
            if posi_simi>nega_simi:
                corr_train+=1

            if iter % n_train_batches == 0:
                print 'training @ iter = '+str(iter)+' average cost: '+str(cost_average)+'corr rate:'+str(corr_train*100.0/train_size)


            if iter % validation_frequency == 0:
                corr_test=0
                for i in test_batch_start:
                    cost, posi_simi, nega_simi=test_model(i)
                    if posi_simi>nega_simi:
                        corr_test+=1

                #write_file.close()
                #test_score = numpy.mean(test_losses)
                test_acc=corr_test*1.0/test_size
                #test_acc=1-test_score
                print(('\t\t\tepoch %i, minibatch %i/%i, test acc of best '
                           'model %f %%') %
                          (epoch, minibatch_index, n_train_batches,test_acc * 100.))
                #now, see the results of LR
                #write_feature=open(rootPath+'feature_check.txt', 'w')



                find_better=False
                if test_acc > max_acc:
                    max_acc=test_acc
                    best_epoch=epoch
                    find_better=True
                print '\t\t\ttest_acc:', test_acc, 'max:',    max_acc,'(at',best_epoch,')'
                if find_better==True:
                    store_model_to_file(params, best_epoch, max_acc)
                    print 'Finished storing best params'

            if patience <= iter:
                done_looping = True
                break


        print 'Epoch ', epoch, 'uses ', (time.clock()-mid_time)/60.0, 'min'
        mid_time = time.clock()
        #writefile.close()

        #print 'Batch_size: ', update_freq
    end_time = time.clock()
    print('Optimization complete.')
    print('Best validation score of %f %% obtained at iteration %i,'\
          'with test performance %f %%' %
          (best_validation_loss * 100., best_iter + 1, test_score * 100.))
    print >> sys.stderr, ('The code for file ' +
                          os.path.split(__file__)[1] +
                          ' ran for %.2fm' % ((end_time - start_time) / 60.))


def store_model_to_file(best_params, best_epoch, best_acc):
    save_file = open('/mounts/data/proj/wenpeng/Dataset/MCTest/Best_Para_at'+str(best_epoch)+'_'+str(best_acc), 'wb')  # this will overwrite current contents
    for para in best_params:
        cPickle.dump(para.get_value(borrow=True), save_file, -1)  # the -1 is for HIGHEST_PROTOCOL
    save_file.close()

def cosine(vec1, vec2):
    vec1=debug_print(vec1, 'vec1')
    vec2=debug_print(vec2, 'vec2')
    norm_uni_l=T.sqrt((vec1**2).sum())
    norm_uni_r=T.sqrt((vec2**2).sum())

    dot=T.dot(vec1,vec2.T)

    simi=debug_print(dot/(norm_uni_l*norm_uni_r), 'uni-cosine')
    return simi#.reshape((1,1))
def Linear(sum_uni_l, sum_uni_r):
    return (T.dot(sum_uni_l,sum_uni_r.T)).reshape((1,1))
def Poly(sum_uni_l, sum_uni_r):
    dot=T.dot(sum_uni_l,sum_uni_r.T)
    poly=(0.5*dot+1)**3
    return poly.reshape((1,1))
def Sigmoid(sum_uni_l, sum_uni_r):
    dot=T.dot(sum_uni_l,sum_uni_r.T)
    return T.tanh(1.0*dot+1).reshape((1,1))
def RBF(sum_uni_l, sum_uni_r):
    eucli=T.sum((sum_uni_l-sum_uni_r)**2)
    return T.exp(-0.5*eucli).reshape((1,1))
def GESD (sum_uni_l, sum_uni_r):
    eucli=1/(1+T.sum((sum_uni_l-sum_uni_r)**2))
    kernel=1/(1+T.exp(-(T.dot(sum_uni_l,sum_uni_r.T)+1)))
    return (eucli*kernel).reshape((1,1))
def EUCLID(sum_uni_l, sum_uni_r):
    return T.sqrt(T.sqr(sum_uni_l-sum_uni_r).sum()+1e-20)#.reshape((1,1))
def load_model_for_conv1(params):
    #save_file = open('/mounts/data/proj/wenpeng/Dataset/WikiQACorpus/Best_Conv_Para')
    #save_file = open('/mounts/data/proj/wenpeng/Dataset/WikiQACorpus/Best_Conv_Para_at_18')
    save_file = open('/mounts/data/proj/wenpeng/Dataset/SICK/Best_Conv_Para_13')

    for para in params:
        para.set_value(cPickle.load(save_file), borrow=True)
    save_file.close()
def load_model_for_conv2(params):
    #save_file = open('/mounts/data/proj/wenpeng/Dataset/WikiQACorpus/Best_Conv_Para')
    #save_file = open('/mounts/data/proj/wenpeng/Dataset/WikiQACorpus/Best_Conv_Para_at_18')
    save_file = open('/mounts/data/proj/wenpeng/Dataset/SICK/Best_Conv2_Para_20')

    for para in params:
        para.set_value(cPickle.load(save_file), borrow=True)
    save_file.close()

def compute_test_acc(test_y, test_prop):
    size=len(test_y)
    batch=4
    n_batches=size/batch

    batch_start=list(numpy.arange(n_batches)*batch)
    corr=0
    for start in batch_start:
        sub_y=test_y[start:start+batch]
        sub_prop=test_prop[start:start+batch]
        big_posi=numpy.argmax(sub_prop)
        if sub_y[big_posi]==1:
            corr+=1
    return corr*1.0/n_batches


if __name__ == '__main__':
    evaluate_lenet5()
