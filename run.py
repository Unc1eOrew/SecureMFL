import requests
import time


def loop():
    print("客户端开始训练...")
    r1 = requests.get("http://localhost:8001/model_train")

    print("客户端1密钥发送中...")
    r5 = requests.get("http://localhost:8001/send_key")
    if r5.status_code == 200:
        print("客户端1：", r5.text)
    else:
        print("客户端1：", r5.status_code)
        exit(0)
    print("客户端2已获取全部密钥！")

    r2 = requests.get("http://localhost:8002/model_train")
    if r1.status_code == 200 and r2.status_code == 200:
        print("客户端1：", r1.text)
        print("客户端2：", r2.text)
    else:
        print("客户端1：", r1.status_code)
        print("客户端2：", r2.status_code)
        exit(0)

    print("客户端状态发送中...")
    r1 = requests.get("http://localhost:8001/send_status")
    r2 = requests.get("http://localhost:8002/send_status")
    if r1.status_code == 200 and r2.status_code == 200:
        print("客户端1：", r1.text)
        print("客户端2：", r2.text)
    else:
        print("客户端1：", r1.status_code)
        print("客户端2：", r2.status_code)
        exit(0)

    print("客户端模型权重发送中...")
    time_start = time.time()  # 传输开始时间

    r1 = requests.get("http://localhost:8001/send_model")

    time_end = time.time()  # 传输结束时间
    time_sum = time_end - time_start
    print("传输所用总时间：%.4fs" % time_sum)

    r2 = requests.get("http://localhost:8002/send_model")
    if r1.status_code == 200 and r2.status_code == 200:
        print("客户端1：", r1.text)
        print("客户端2：", r2.text)
    else:
        print("客户端1：", r1.status_code)
        print("客户端2：", r2.status_code)
        exit(0)

    print("服务器权重聚合中...")
    r3 = requests.get("http://localhost:8000/aggregate_models")
    if r3.status_code == 200:
        print("服务器：", r3.text)
    else:
        print("服务器：", r3.status_code)
        exit(0)

    print("服务器权重更新发送中...")
    r4 = requests.get("http://localhost:8000/send_model")
    if r4.status_code == 200:
        print("服务器：", r4.text)
    else:
        print("服务器：", r4.status_code)
        exit(0)


if __name__ == "__main__":
    for i in range(100):
        print("\n当前轮次：", i + 1)
        time_start = time.time()    # 开始时间

        loop()

        time_end = time.time()      # 结束时间
        time_sum = time_end - time_start    # 时间差为该轮执行时间
        print("当前轮所用时间：%.4fs" % time_sum)
