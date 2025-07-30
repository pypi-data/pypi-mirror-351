from copy import deepcopy

from .topk import TopK


class MRR(TopK):
    """
    MRR(Mean Reciprocal Rank)是链路预测中常用的评估指标之一，用于衡量模型预测的准确性。
    MRR是"平均倒数排名"的缩写，它通过计算预测结果中正确链接的排名的倒数来衡量模型性能。在链路预测中，MRR特别适用于评估模型对缺失链接的排序质量。

    MRR的计算步骤
    1. 对每个测试集中的正样本
    2. 确定正确边的排名
    3. 计算倒数排名
    4. 计算所有测试边的平均倒数排名

    """

    def __matmul__(self, k: int) -> float:
        values = []
        neg_predict = self.predict.filter(key=lambda x: self.true.has_edge(x).score == 0)
        if not neg_predict:
            return 0

        for key, edges in self.true.group('node1').items():
            r = 0
            predict = deepcopy(neg_predict)
            for idx, item in enumerate(edges.items(), start=1):
                if item.score == 1:
                    pos_edge = self.predict.has_edge(item)
                    predict.append(pos_edge)
                    predict_k = predict.sort(key=lambda x: x.score, reverse=True)[:k]

                    if not predict_k.has_edge(item):
                        continue

                    for index, pred in enumerate(predict_k, start=1):
                        if item.node1 == pred.node1 and item.node2 == pred.node2:
                            r = 1 / index
                            break

                if r:
                    break

            if self.exclude_zero and r == 0:
                continue

            values.append(r)

        return self.mean(values)
