from flask import Flask, request
import requests, json
import ast
from fl_agg import model_aggregation

app = Flask(__name__)


@app.route('/')
def hello():
    return "这是参数服务器！"


# 判断客户端状态
@app.route('/get_status', methods=['GET', 'POST'])
def client_status():
    if request.method == 'POST':
        client_port = request.json['client_id']

        if client_port:
            server_ack = {'server_ack': '1'}
            return str(server_ack)
        else:
            return "客户端未就绪！"
    else:
        return "客户端均已就绪！"


# 获得客户端模型
@app.route('/get_model', methods=['POST'])
def getmodel():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()
        fname = ast.literal_eval(fname.decode("utf-8"))
        fname = fname['fname']
#       print(fname)

        wfile = open("./client_models/" + fname, 'wb')
        wfile.write(file)
        return "模型权重已获取！"
    else:
        return "模型权重获取失败！"


# 求平均权重
@app.route('/aggregate_models')
def perform_model_aggregation():
    model_aggregation()
    return "已获取模型平均权重！"


# 向客户端发送模型更新
@app.route('/send_model')
def send_model():
    with open('./clients.txt', 'r') as f:
        clients = f.read()
    clients = clients.split('\n')

    for c in clients:
        if c != '':
            file = open("./agg_model/agg_model.npy", 'rb')
            data = {'fname': 'agg_model.npy'}
            files = {
                'json': ('json_data', json.dumps(data), 'application/json'),
                'model': ('agg_model.npy', file, 'application/octet-stream')
            }
            req = requests.post(url=c + 'get_agg_model', files=files)
    return "权重更新已发送！"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=True)
