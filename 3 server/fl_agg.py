import numpy as np


# 求平均权重
def fl_average():
    model1 = np.load("./client_models/model1.npy", allow_pickle=True)
    model2 = np.load("./client_models/model2.npy", allow_pickle=True)
    fl_avg = np.add(model1, model2)
    fl_avg /= 2
    return fl_avg


# 模型权重聚合
def model_aggregation():
    mod_avg = fl_average()
    np.save('./agg_model/agg_model', mod_avg)
    print("模型更新已保存!")


if __name__ == '__main__':
    model_aggregation()
