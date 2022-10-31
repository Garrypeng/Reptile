import re
import gensim
import jieba
import numpy
import numpy as np
from scipy.linalg import norm
from sklearn.metrics.pairwise import cosine_similarity


# 对句子进行中文分词
def seg_depart(sentence):
    # 清除序号
    def clean_number(s):
        # 去除换行
        s = s.split('\n')
        # 去除排序数字
        pattern = '^[0-9]?'
        # 返回清洗好的数据
        doc = ''
        for item in s:
            doc = doc + re.sub(pattern, '', item)
        return doc

    # 剔除错误分词
    def delete_error(s, len_s):
        global delete_index, deleted_str
        item = ''
        try:
            for item in s:
                delete_index += 1
                if type(model[item]) == numpy.ndarray:
                    pass
        except KeyError:
            deleted_str.append(item)
        finally:
            if delete_index == len_s:
                return deleted_str
            else:
                return delete_error(s[delete_index:], len_s)

    # 进行中文分词
    sentence_depart = jieba.lcut(clean_number(sentence))
    # 创建一个停用词列表
    stopwords = [line.strip() for line in open('tencent/hit_stopwords.txt', encoding='UTF-8').readlines()]
    # 输出结果为outstr
    out_str = ''
    # 去停用词
    for word in sentence_depart:
        if word not in stopwords:
            if word != '\t':
                out_str += word
                out_str += ' '
    # 去除所有空格，并去重
    out_str = [item for item in jieba.lcut(out_str) if item != ' ']
    print(out_str)
    return delete_error(out_str, len(out_str))
    # [item for item in out_str if model[item] == numpy.ndarray]


# 计算文本相似度
def vector_similarity(s1, s2):
    def sentence_vector(words):
        # words = jieba.lcut(s)
        # v = np.zeros(100)
        v = 0
        for word in words:
            v += model[word]
        v /= len(words)
        return v

    v1, v2 = sentence_vector(s1), sentence_vector(s2)
    return np.dot(v1, v2) / (norm(v1) * norm(v2))


def word_avg(s1, s2):
    def sentence(words):
        return np.mean([model.get_vector(word) for word in words], axis=0)

    v1, v2 = sentence(s1), sentence(s2)
    return cosine_similarity(v1.reshape(1, -1), v2.reshape(1, -1))


model_file = 'tencent/TC-emd-zh-d100.bin'
model = gensim.models.KeyedVectors.load_word2vec_format(model_file, binary=True)
# 记录index
delete_index, deleted_str = 0, []

str_3 = '''
1、负责美团大众点评网该地区本地商户餐饮生态产品的销售，快速找到目标意向客户，再通过电话或面访的形式约见客户，为客户解决问题，达成合作协议。
2、执行公司的市场策略及政策，达成业绩考核及个人成长的各项目标
3、与公司各部门配合，及时处理用户的反馈、投诉和建议，提高用户满意度。
4、归档和更新所有目标商户拜访、协议、服务条款等有关的gg文件和数据，确保客户信息在数据库中得到正确的维护。
'''

str_4 = '''
1、具有较好的沟通能力能够引导话题，维护客户关系
2、利用网络在各大网站发布软文稿件
3、负责公司网上贸易平台的操作管理
4、了解和搜集网络上各同行及竞争产品的动态信息；
5、充分了解实时热点动态等相关信息（微信、微博、抖音、各大网媒平台等），各大平台热点热播等有关行业的热点资讯。
6、熟悉各种办公软件
7、通过网络进行渠道开发和业务拓展；
'''

print(seg_depart(str_3))
print(model.most_similar('python', topn=10))

# print(vector_similarity(seg_depart(str_3), seg_depart(str_4)))
# print(word_avg(seg_depart(str_3), seg_depart(str_4)))
