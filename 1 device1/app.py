from flask import Flask, request
import json
import requests
import ast
import time
import numpy as np
from phe import paillier
from model_train import train

app = Flask(__name__)


@app.route('/')
def hello():
    return "这是客户端1！"


# 发送设备状态
@app.route('/send_status', methods=['GET'])
def send_status():
    data = {'client_id': '8001'}
    r = requests.post(url='http://localhost:8000/get_status', json=data)

    if r.status_code == 200:
        print("客户端已就绪！")
    return "已就绪！"


# 向设备2发送密钥
@app.route('/send_key')
def send_key():
    # 发送公钥 n
    file = open("./key/public_key_n.txt", 'r')
    data = {'fname': 'public_key_n.txt', 'id': 'http://localhost:8001/'}
    files = {
        'json': ('json_data', json.dumps(data), 'application/json'),
        'key': ('public_key_n.txt', file, 'application/octet-stream')
    }
    req = requests.post(url='http://localhost:8002/get_key', files=files)

    # 发送私钥 p
    file = open("./key/private_key_p.txt", 'r')
    data = {'fname': 'private_key_p.txt', 'id': 'http://localhost:8001/'}
    files = {
        'json': ('json_data', json.dumps(data), 'application/json'),
        'key': ('private_key_p.txt', file, 'application/octet-stream')
    }
    req = requests.post(url='http://localhost:8002/get_key', files=files)

    # 发送私钥 q
    file = open("./key/private_key_q.txt", 'r')
    data = {'fname': 'private_key_q.txt', 'id': 'http://localhost:8001/'}
    files = {
        'json': ('json_data', json.dumps(data), 'application/json'),
        'key': ('private_key_q.txt', file, 'application/octet-stream')
    }
    req = requests.post(url='http://localhost:8002/get_key', files=files)
    return "密钥已全部发送！"


# 发送本地模型权重给服务器
@app.route('/send_model')
def send_model():
    file = open("./local_model/mod1.npy", 'rb')
    data = {'fname': 'model1.npy', 'id': 'http://localhost:8001/'}
    files = {
        'json': ('json_data', json.dumps(data), 'application/json'),
        'model': ('model1.npy', file, 'application/octet-stream')
    }
    req = requests.post(url='http://localhost:8000/get_model', files=files)
    return "模型已发送！"


# 获得更新后模型，并进行解密
@app.route('/get_agg_model', methods=['POST'])
def get_agg_model():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()
        fname = ast.literal_eval(fname.decode("utf-8"))
        fname = fname['fname']
        wfile = open("./model_update/" + fname, 'wb')
        wfile.write(file)

        time_start = time.time()  # 解密开始时间

        # 权重解密
        mod = np.load("./model_update/agg_model.npy", allow_pickle=True)
        # 读取上一轮密钥信息
        # 生成公钥
        f = open('./key/public_key_n.txt', 'r')
        fq = f.read()
        public_key = paillier.PaillierPublicKey(int(fq))
        # 生成私钥 p
        f = open('./key/private_key_p.txt', 'r')
        fq1 = f.read()
        # 生成私钥 q
        f = open('./key/private_key_q.txt', 'r')
        fq2 = f.read()
        private_key = paillier.PaillierPrivateKey(public_key, int(fq1), int(fq2))

        # (41, 128)
        for i in range(41):
            for j in range(128):
                mod[0][i][j] = private_key.decrypt(mod[0][i][j])
        # (128,)
        for i in range(128):
            mod[1][i] = private_key.decrypt(mod[1][i])
        # (128, 40)
        for i in range(128):
            for j in range(40):
                mod[2][i][j] = private_key.decrypt(mod[2][i][j])
        # (40,)
        for i in range(40):
            mod[3][i] = private_key.decrypt(mod[3][i])

        time_end = time.time()  # 解密结束时间
        time_sum = time_end - time_start
        print("解密所用时间：", time_sum)

        np.save('./model_update/agg_model', mod)
        return "已获得模型更新！"
    else:
        return "未获得模型更新！"


# 令设备1开始训练
@app.route('/model_train')
def model_train():
    train()
    return "训练完成！"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8001, debug=False, use_reloader=True)
