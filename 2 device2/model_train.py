from os import path
from phe import paillier
import pandas as pd
import tensorflow as tf
import numpy as np
import time


# 保存本地模型的更新信息
def save_local_model_update(model, public_key):
    time_start = time.time()  # 加密开始时间

    mod = model.get_weights()
    # 对模型权重进行同态加密
    # 将权重类型从 np.float32转换为 float用于加密
    mod[0] = mod[0].astype('float')
    mod[0] = list(mod[0])
    mod[1] = mod[1].astype('float')
    mod[1] = list(mod[1])
    mod[2] = mod[2].astype('float')
    mod[2] = list(mod[2])
    mod[3] = mod[3].astype('float')
    mod[3] = list(mod[3])

    # (41, 128)
    for i in range(41):
        mod[0][i] = mod[0][i].astype('float')
        mod[0][i] = list(mod[0][i])
        for j in range(128):
            mod[0][i][j] = public_key.encrypt(mod[0][i][j])
        # 加密后再将权重类型改回去用于训练
        mod[0][i] = np.array(mod[0][i])

    # (128,)
    for i in range(128):
        mod[1][i] = public_key.encrypt(float(mod[1][i]))

    # (128, 40)
    for i in range(128):
        mod[2][i] = mod[2][i].astype('float')
        mod[2][i] = list(mod[2][i])
        for j in range(40):
            mod[2][i][j] = public_key.encrypt(float(mod[2][i][j]))
        # 加密后再将权重类型改回去用于训练
        mod[2][i] = np.array(mod[2][i])

    # (40,)
    for i in range(40):
        mod[3][i] = public_key.encrypt(float(mod[3][i]))

    # 加密后再将权重类型改回去用于训练
    mod[0] = np.array(mod[0])
    mod[1] = np.array(mod[1])
    mod[2] = np.array(mod[2])
    mod[3] = np.array(mod[3])

    time_end = time.time()  # 加密结束时间
    time_sum = time_end - time_start
    print("加密所用时间：%.4fs" % time_sum)

    # 保存加密后的权重信息
    np.save('./local_model/mod2', mod)
    print("本地模型已保存！")


def train():
    # 读取密钥信息
    # 生成公钥
    f = open('./key/public_key_n.txt', 'r')
    fq = f.read()
    for i in fq:
        if i == 'b':
            fq = fq.replace(i, '')
        elif i == '\'':
            fq = fq.replace(i, '')
    public_key = paillier.PaillierPublicKey(int(fq))

    # 生成私钥 p
    f = open('./key/private_key_p.txt', 'r')
    fq1 = f.read()
    for i in fq1:
        if i == 'b':
            fq1 = fq1.replace(i, '')
        elif i == '\'':
            fq1 = fq1.replace(i, '')
    # 生成私钥 q
    f = open('./key/private_key_q.txt', 'r')
    fq2 = f.read()
    for i in fq2:
        if i == 'b':
            fq2 = fq2.replace(i, '')
        elif i == '\'':
            fq2 = fq2.replace(i, '')
    private_key = paillier.PaillierPrivateKey(public_key, int(fq1), int(fq2))

    time_start = time.time()  # 训练开始时间

    print("数据处理中...")
    x_train = pd.read_csv('./kdd99_data/train_x.csv', header=None).values
    y_train = pd.read_csv('./kdd99_data/train_y.csv', header=None).values
    x_test = pd.read_csv('./kdd99_data/test_x.csv', header=None).values
    y_test = pd.read_csv('./kdd99_data/test_y.csv', header=None).values

    x_train = x_train.reshape(x_train.shape[0], 41, 1)
    x_test = x_test.reshape(x_test.shape[0], 41, 1)

    # sequential序贯模型:多个网络层的线性堆叠
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(41, 1)),  # 拉直层，把多维数据一维化
        tf.keras.layers.Dense(128, activation='relu'),  # 全连接层，设置128个神经元，激活函数为 relu，较快收敛
        tf.keras.layers.Dropout(0.3),  # 随机断开输入神经元的概率为 0.3，由于该层神经元过多，dropout正则化，防止过拟合
        tf.keras.layers.Dense(40, activation='softmax')  # softmax层，设置40个类别，激活函数为 softmax，适合分类
    ])

    model.compile(
        optimizer=tf.keras.optimizers.SGD(learning_rate=0.0001),  # 优化函数：sgd
        loss='categorical_crossentropy',  # 配置损失函数，多类对数损失，用于多分类问题
        metrics=['categorical_accuracy'])  # 评价指标为准确率

    if path.exists("./model_update/agg_model.npy"):
        print("模型已存在，载入模型权重...")
        mod = np.load("./model_update/agg_model.npy", allow_pickle=True)
        model.set_weights(mod)
    else:
        print("模型不存在，建立模型...")

    # 训练模型
    model.fit(x_train, y_train, batch_size=128, epochs=1)
    # 评估模型
    test_score = model.evaluate(x_test, y_test, batch_size=128)
    print("test loss：%.4f" % test_score[0])
    print("test accuracy：%.4f" % test_score[1])

    time_end = time.time()  # 训练结束时间
    time_sum = time_end - time_start
    print("训练所用时间：%.4fs" % time_sum)

    # 保存本地模型的更新信息
    save_local_model_update(model, public_key)


if __name__ == '__main__':
    train()
