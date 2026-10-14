import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import load_model
import keras
from keras import layers 
from keras.callbacks import ModelCheckpoint
from keras.models import Sequential 
import os
import h5py
import glob
import tensorflow as tf
from tqdm import tqdm
import random
from scipy import stats
import sys
sys.path.insert(0, r"F:\13_科研数据\FarSCAD_new")
from transformer_layers import TransformerEncoder, PositionalEncoding

####################################
#Pre-defined matrix
####################################
AES_Sbox = np.array([
            0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
            0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
            0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
            0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
            0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
            0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
            0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
            0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
            0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
            0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
            0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
            0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
            0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
            0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
            0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
            0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16])

SM4_Sbox = np.array([
            0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05,
            0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99,
            0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed, 0xcf, 0xac, 0x62,
            0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa, 0x75, 0x8f, 0x3f, 0xa6,
            0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c, 0x19, 0xe6, 0x85, 0x4f, 0xa8,
            0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb, 0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35,
            0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25, 0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87,
            0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52, 0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e,
            0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38, 0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1,
            0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34, 0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3,
            0x1d, 0xf6, 0xe2, 0x2e, 0x82, 0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f,
            0xd5, 0xdb, 0x37, 0x45, 0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51,
            0x8d, 0x1b, 0xaf, 0x92, 0xbb, 0xdd, 0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8,
            0x0a, 0xc1, 0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd, 0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0,
            0x89, 0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84,
            0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39, 0x48])

FK = np.array([0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc])

CK = np.array([
            0x00070e15,0x1c232a31,0x383f464d,0x545b6269,
            0x70777e85,0x8c939aa1,0xa8afb6bd,0xc4cbd2d9,
            0xe0e7eef5,0xfc030a11,0x181f262d,0x343b4249,
            0x50575e65,0x6c737a81,0x888f969d,0xa4abb2b9,
            0xc0c7ced5,0xdce3eaf1,0xf8ff060d,0x141b2229,
            0x30373e45,0x4c535a61,0x686f767d,0x848b9299,
            0xa0a7aeb5,0xbcc3cad1,0xd8dfe6ed,0xf4fb0209,
            0x10171e25,0x2c333a41,0x484f565d,0x646b7279])
			
			
def load_AES_traces(T_path,C_path,K_path):    

    traces = np.load(T_path)
    ct_name = np.load(C_path)      
    key_name = np.load(K_path)  
    key = key_name.astype(int)
    ct = ct_name.astype(int)

    
    labels=np.bitwise_xor(ct,key)
    #indices = np.arange(label.shape[0]) 
    #np.random.shuffle(indices)
    #label = label[indices]
    #traces = traces[indices, :]
    
    return traces, ct, key, labels

def load_SM4_traces(T_path,C_path,K_path):    

    traces = np.load(T_path)
    ct_name = np.load(C_path)      
    key_name = np.load(K_path)  
    key = key_name.astype(int)
    ct = ct_name.astype(int)

    rk_bytes = key[28:32,:]
    C0 = ct[:,0:4]
    C1 = ct[:,4:8]
    C2 = ct[:,8:12]
    C3 = ct[:,12:16]
    tmp = C3 ^ C2 ^ C1 ^ rk_bytes[3]
    sout = SM4_Sbox[tmp]
    
    labels= sout
    indices = np.arange(labels.shape[0]) 
    
    #np.random.shuffle(indices)
    labels = labels[indices, :]
    traces = traces[indices, :]
    
    return traces, ct, key, labels

def load_Kyber_traces(T_path,C_path,K_path):    

    traces = np.load(T_path)
    #message_name = np.load(C_path)      
    message = np.load(K_path)  

    labels= message
    #indices = np.arange(labels.shape[0]) 
    #np.random.shuffle(indices)
    #labels = labels[indices, :]
    #traces = traces[indices, :]
    
    return traces, message, message, labels
	
def load_sca_model(model_file):
    try:
        model = load_model(model_file)
    except:
        print("Error: can't load Keras model file '%s'" % model_file)
        sys.exit(-1)
    return model
	
def get_prediction(model, Traces):
    input_layer_shape = model.input_shape
    input_data = Traces.reshape((Traces.shape[0],) + input_layer_shape[1:])
    predictions = model.predict(input_data, verbose=0)
    return predictions
	
def rank_cal(selected_probabilities, key_interest, num_trace):
    rank = []
    total_pro = np.zeros(256)

    for i in range(num_trace):
        total_pro += np.log(selected_probabilities[i] + 1e-12)
        sorted_proba = np.array(list(map(lambda a: total_pro[a], total_pro.argsort()[::-1])))
        real_key_rank = np.where(sorted_proba == total_pro[key_interest])[0][0]
        rank.append(real_key_rank)
    rank = np.array(rank)

    return rank
	
def AES_prediction_to_probability(selected_cts_interest, selected_predictions, num_trace):
    
    probabilities_array = []
    
    for i in range(num_trace):
        probabilities=np.zeros(256)
        for j in range(256):
            sbox_out= selected_cts_interest[i]^j
            value = sbox_out
            probabilities[j] = selected_predictions[i][value]
        probabilities_array.append(probabilities)
    probabilities_array = np.array(probabilities_array)

    for i in range(len(probabilities_array)):
        if np.count_nonzero(probabilities_array[i]) != 256:
            none_zero_predictions = [a for a in probabilities_array[i] if a != 0]
            min_v = min(none_zero_predictions)
            probabilities_array[i] = probabilities_array[i] + min_v**2	
    
    return probabilities_array

def AES_pge_test(model, Traces, key, ct, num_trace, target_byte, average, plot_on=False, print_on=False):
    
    key_interest = key[0, target_byte]
    cts_interest = ct[:, target_byte]
    predictions = get_prediction(model, Traces)

    ranks_array = []

    for pge in tqdm(range(average)):
        select = random.sample(range(len(Traces)), num_trace)
        selected_cts_interest = cts_interest[select]
        selected_predictions = predictions[select]
        
        probabilities = AES_prediction_to_probability(selected_cts_interest, selected_predictions, num_trace)
        ranks = rank_cal(probabilities, key_interest, num_trace)
        ranks_array.append(ranks)

    ranks_array = np.array(ranks_array)

    for pge_0 in range(ranks_array.shape[1]):
        if np.count_nonzero(ranks_array[:, pge_0]) < int(average* 0.5):
            #print(pge_1+1)
            break
    
    average_ranks = np.sum(ranks_array, axis=0) / average
    pge_32 = next((i + 1 for i, rank in enumerate(average_ranks) if rank < 32), None)
    pge_5 = next((i + 1 for i, rank in enumerate(average_ranks) if rank < 5), None)
    pge_1 = next((i + 1 for i, rank in enumerate(average_ranks) if rank < 1.2), None)
    
    if plot_on:
        plt.figure()
        plt.plot(average_ranks)
        plt.xlabel('Number of Traces')
        plt.ylabel('PGE')
        plt.show()

    if print_on:
        print("the point which makes half of test to reach PGE=0:", pge_0)
        print("the point which makes average PGE<1:", pge_1)
        print("the point which makes average PGE<5:", pge_5)
        print("the point which makes average PGE<32:", pge_32)
        
    return average_ranks
	
def SM4_prediction_to_probability(selected_cts_interest, selected_predictions, num_trace):

    probabilities_array = []
    
    for i in range(num_trace):
        probabilities=np.zeros(256)
        for j in range(256):
            tmp= selected_cts_interest[i]^j
            sbox_out = SM4_Sbox[tmp]
            value = sbox_out
            probabilities[j] = selected_predictions[i][value]
        probabilities_array.append(probabilities)
    probabilities_array = np.array(probabilities_array)

    for i in range(len(probabilities_array)):
        if np.count_nonzero(probabilities_array[i]) != 256:
            none_zero_predictions = [a for a in probabilities_array[i] if a != 0]
            min_v = min(none_zero_predictions)
            probabilities_array[i] = probabilities_array[i] + min_v**2	
    
    return probabilities_array

def SM4_pge_test(model, Traces, key, ct, num_trace, target_byte, average, plot_on=False, print_on=False):
    C0 = ct[:,0:4]
    C1 = ct[:,4:8]
    C2 = ct[:,8:12]
    C3 = ct[:,12:16]
    C_ALL = C3 ^ C2 ^ C1
    rk_bytes = key[31,:]
    
    cts_interest = C_ALL[:, target_byte]
    key_interest = rk_bytes[target_byte]
    predictions = get_prediction(model, Traces)

    ranks_array = []

    for pge in tqdm(range(average)):
        select = random.sample(range(len(Traces)), num_trace)
        selected_cts_interest = cts_interest[select]
        selected_predictions = predictions[select]
        
        probabilities = SM4_prediction_to_probability(selected_cts_interest, selected_predictions, num_trace)
        ranks = rank_cal(probabilities, key_interest, num_trace)
        ranks_array.append(ranks)

    ranks_array = np.array(ranks_array)

    for pge_0 in range(ranks_array.shape[1]):
        if np.count_nonzero(ranks_array[:, pge_0]) < int(average* 0.5):
            #print(pge_1+1)
            break
    
    average_ranks = np.sum(ranks_array, axis=0) / average
    pge_32 = next((i + 1 for i, rank in enumerate(average_ranks) if rank < 32), None)
    pge_5 = next((i + 1 for i, rank in enumerate(average_ranks) if rank < 5), None)
    pge_1 = next((i + 1 for i, rank in enumerate(average_ranks) if rank < 1.1), None)
    
    if plot_on:
        plt.figure()
        plt.plot(average_ranks)
        plt.xlabel('Number of Traces')
        plt.ylabel('PGE')
        plt.show()

    if print_on:
        print("the point which makes half of test to reach PGE=0:", pge_0)
        print("the point which makes average PGE<1:", pge_1)
        print("the point which makes average PGE<5:", pge_5)
        print("the point which makes average PGE<32:", pge_32)
        
    return average_ranks
    
    
if __name__ == "__main__":
# --------------------------------
# Test for AES and SM4
# --------------------------------
    T_path="data\\aes\\desync_0\\test\\D9\\5m\\1_traces_maxmin.npy"
    C_path="data\\aes\\desync_0\\test\\D9\\5m\\ct.npy"
    K_path="data\\aes\\desync_0\\test\\D9\\5m\\rk.npy"
    model_path ="data\\aes\\model\\DAR-NN_tifs_Byte0_190-210.h5"

    num_trace =2500
    target_byte = 0
    test_num=50
    plot_sign = True
    print_sign = True

    model = load_model(model_path, compile=False)
    traces, ct, key, labels = load_AES_traces(T_path,C_path,K_path)
    
    start, end = model_path.split("_")[-1].replace(".h5", "").split("-")
    start, end = int(start), int(end)
    traces = traces[:, start:end]
    average_ranks = AES_pge_test(model, traces, key, ct, num_trace, target_byte, average=test_num, plot_on=plot_sign, print_on=print_sign)
    
    
