import numpy as np
import os
from keras.preprocessing import image

def extract_data_from_lst(lst, preprocess=True):
    x = []
    for file in lst:
        x += [read_input_img(file)]
    x = np.array(x)
    if preprocess:
        x = img_process(x)
    return x


def generate_train_lst(dire):
    x = []
    y = []
    cam = []
    for file in os.listdir(dire):
        if file.endswith('.jpg'):
            x += [dire + file]
            if file.startswith('-'):
                y += [-1]
                cam += [int(file[4])]
            else:
                y += [int(file[:4])]
                cam += [int(file[6])]

    return x,y,cam

def read_input_img(file):
    im = image.load_img(file, target_size=(224,224,))
    im = image.img_to_array(im)
    return im

def img_process(imgs, shift = (97.10,99.23,105.45)):
    imgs[:,:,:,0] -= shift[0]
    imgs[:,:,:,1] -= shift[1]
    imgs[:,:,:,2] -= shift[2]
   # imgs[:,:,:,0] /= 255
   # imgs[:,:,:,1] /= 255
   # imgs[:,:,:,2] /= 255
    return imgs


def create_pairs(x,y):
    '''Positive and negative pair creation.
    Alternates between positive and negative pairs.
    '''
    neg_size = 3
    clss = np.unique(y)
    num_clss = len(clss)
    digit_indices = [np.where(y == c)[0] for c in clss]
    pairs = []
    labels = []
    for d in range(num_clss):
        n = len(digit_indices[d])
        for i in range(n):
            inc = random.randrange(1,n)
            dn = (i + inc) % n
            z1, z2 = digit_indices[d][i], digit_indices[d][dn]
            l1 = to_categorical(d, num_clss).squeeze()
            pairs += [[x[z1], x[z2]]]
            labels += [[1, l1, l1]]
            incs = np.random.randint(1, num_clss, neg_size)
            dns = (incs + d) % num_clss
            dxs = [random.randrange(len(digit_indices[dn])) for dn in dns]
            for idx1, idx2 in zip(dns, dxs):
                z1, z2 = digit_indices[idx1],digit_indices[idx2]
                l2 = to_categorical(idx1, num_clss).squeeze()
                pairs += [[x[z1], x[z2]]]
                labels += [[0, l1, l2]]
    s = np.arange(pairs.shape[0])
    np.random.shuffle(s)
    pairs,labels = pairs[s], labels[s]
    return np.array(pairs), np.array(labels)



if __name__ == '__main__':
    train_dire = '/home/zqx/Desktop/flowerfan/data/Market-1501-v15.09.15/bounding_box_train/'
    test_dire = '/home/zqx/Desktop/flowerfan/data/Market-1501-v15.09.15/bounding_box_test/'
    query_dire = '/home/zqx/Desktop/flowerfan/data/Market-1501-v15.09.15/query/'


    x_train, y_train, cam_train = generate_train_lst(train_dire)
    x_test, y_test, cam_test = generate_train_lst(test_dire)
    x_query, y_query, cam_query = generate_train_lst(query_dire)

    np.savez('../data/train.lst', data=x_train, label=y_train, cam=cam_train)
    np.savez('../data/test.lst', data=x_test, label=y_test, cam=cam_test)
    np.savez('../data/query.lst', data=x_query, label=y_query, cam=cam_query)

    s = np.arange(y_train.shape[0])
    np.random.shuffle(s)
    x_train, y_train = x_train[s], y_train[s]
    lst_pairs, y = create_pairs(x_train, y_train)
    np.savez('../data/input.lst', pair=lst_pairs, label=y)
