###########################################################
import pandas as pd
import numpy as np
import math
import scipy.stats as st
from sklearn.preprocessing import MinMaxScaler

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 500)
#pd.set_option('display.width', 10)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df = pd.read_csv("amazon_review.csv")

def check_df(dataframe, head=5):
    print("############### Shape ################")
    print(dataframe.shape)
    print("########### Types ###############")
    print(dataframe.dtypes)
    print("########### Head ###############")
    print (dataframe.head(head))
    print ("########### Tail ###############" )
    print ( dataframe.tail(head))
    print ( "########### NA ###############" )
    print ( dataframe.isnull().sum())
    print ( "########### Quantiles ###############" )
    print ( dataframe.describe([0, 0.25, 0.50, 0.75]).T )


check_df(df)
df.columns


#Görev 1: Average Rating’i güncel yorumlara göre hesaplayınız ve var olan average rating ile kıyaslayınız.

#Paylaşılan veri setinde kullanıcılar bir ürüne puanlar vermiş ve yorumlar yapmıştır. Bu görevde amacımız verilen puanları tarihe göre
#ağırlıklandırarak değerlendirmektir. İlk ortalama puan ile elde edilecek tarihe göre ağırlıklı puanın karşılaştırılması gerekmektedir.
#Adım 1: Ürünün ortalama puanını hesaplayınız.

df["overall"].mean()

#Adım 2: Tarihe göre ağırlıklı puan ortalamasını hesaplayınız.
#reviewTime değişkenini tarih değişkeni olarak tanıtmanız

df["reviewTime"] = pd.to_datetime(df["reviewTime"])
df.info()

#reviewTime'ın max değerini current_date olarak kabul etmeniz
current_date = pd.to_datetime(df["reviewTime"].max())

#her bir puan-yorum tarihi ile current_date'in farkını gün cinsinden ifade ederek yeni değişken oluşturmanız ve gün cinsinden ifade edilen
#değişkeni quantile fonksiyonu ile 4'e bölüp (3 çeyrek verilirse 4 parça çıkar) çeyrekliklerden gelen değerlere göre ağırlıklandırma yapmanız
#gerekir. Örneğin q1 = 12 ise ağırlıklandırırken 12 günden az süre önce yapılan yorumların ortalamasını alıp bunlara yüksek ağırlık vermek gibi.

df["days"]= (current_date - df["reviewTime"]).dt.days

q1 = df["days"].quantile(0.25)
q1 #280
q2 = df["days"].quantile(0.50)
q2 #430
q3 = df["days"].quantile(0.75)
q3 #600
q4 = df["days"].quantile(1)
q4#1063

def time_based_weighted_average(dataframe, w1=30, w2=26, w3=24, w4=20):
    return dataframe.loc[dataframe["days"] <= 280, "overall"].mean() * w1 / 100 + \
           dataframe.loc[(dataframe["days"] > 280) & (dataframe["days"] <= 430), "overall"].mean() * w2 / 100 + \
           dataframe.loc[(dataframe["days"] > 430) & (dataframe["days"] <= 600), "overall"].mean() * w3 / 100 + \
           dataframe.loc[(dataframe["days"] > 600), "overall"].mean() * w4 / 100

time_based_weighted_average(df)


#Adım 3: Ağırlıklandırılmış puanlamada her bir zaman diliminin ortalamasını karşılaştırıp yorumlayını
df.loc[df["days"] <= 280, "overall"].mean()
df.loc[(df["days"] > 280) & (df["days"] <= 430), "overall"].mean()
df.loc[(df["days"] > 430) & (df["days"] <= 600), "overall"].mean()
df.loc[(df["days"] > 600), "overall"].mean()

df.loc[df["days"] <= 280, "overall"].count()
df.loc[(df["days"] > 280) & (df["days"] <= 430), "overall"].count()
df.loc[(df["days"] > 430) & (df["days"] <= 600), "overall"].count()
df.loc[(df["days"] > 600), "overall"].count()
#güncel yorumların ortalaması daha yüksek, bu üründe süreç içerisinde iyileştirme yapılmış olabilirve
#teknolojik ürün olduğuna göre yazılım güncellemeleri ya da yeni sürümler üretilmiş olabilir.
#daha güncel olan yorumları daha çok ağırlıklandırdık. dolayısıyla ağırlıklı ortalamaya katkıları daha yüksek

#####Görev 2: Ürün için ürün detay sayfasında görüntülenecek 20 review’i belirleyiniz
#Adım 1: helpful_no değişkenini üretini
#total_vote bir yoruma verilen toplam up-down sayısıdır.
#• up, helpful demektir.
#• Veri setinde helpful_no değişkeni yoktur, var olan değişkenler üzerinden üretilmesi gerekmektedir.
#• Toplam oy sayısından (total_vote) yararlı oy sayısı (helpful_yes) çıkarılarak yararlı bulunmayan oy sayılarını (helpful_no) bulunuz

#olumsuz yorumların sayısı datasette yoksa bunları çıkarmamız ve değerlendirmede kullanmamız gerekir.
df["helpful_no"] = df["total_vote"] - df["helpful_yes"]
df.head()
df.columns
####Adım 2: score_pos_neg_diff, score_average_rating ve wilson_lower_bound skorlarını hesaplayıp veriye ekleyiniz.
#• score_pos_neg_diff, score_average_rating ve wilson_lower_bound skorlarını hesaplayabilmek için score_pos_neg_diff,
#score_average_rating ve wilson_lower_bound fonksiyonlarını tanımlayınız.

#• score_pos_neg_diff'a göre skorlar oluşturunuz. Ardından; df içerisinde score_pos_neg_diff ismiyle kaydediniz.
def score_pos_neg_diff(helpful_yes, helpful_no):
    return helpful_yes - helpful_no

df["score_pos_neg_diff"] = df.apply(lambda x: score_pos_neg_diff(x["helpful_yes"],
                                                                   x["helpful_no"]), axis=1)
df.columns

#• score_average_rating'a göre skorlar oluşturunuz. Ardından; df içerisinde score_average_rating ismiyle kaydediniz.
def score_average_rating(helpful_yes, helpful_no):
    if (helpful_yes + helpful_no) == 0:
        return 0
    return helpful_yes / (helpful_yes + helpful_no)

df["score_average_rating"] = df.apply(lambda x: score_average_rating(x["helpful_yes"],
                                                                   x["helpful_no"]), axis=1)
df.columns


#• wilson_lower_bound'a göre skorlar oluşturunuz. Ardından; df içerisinde wilson_lower_bound ismiyle kaydediniz
def wilson_lower_bound(helpful_yes, helpful_no, confidence=0.95):
    n = helpful_yes + helpful_no
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * helpful_yes / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"],
                                                                   x["helpful_no"]), axis=1)
df["wilson_lower_bound"].unique()
df["wilson_lower_bound"].nunique()
df.columns

###Adım 3: 20 Yorumu belirleyiniz ve sonuçları Yorumlayını
#• wilson_lower_bound'a göre ilk 20 yorumu belirleyip sıralayanız.
#• Sonuçları yorumlayınız

df.sort_values("wilson_lower_bound", ascending=False).head(20)

#toplam oy sayısına göre göre değerlendirdiğimizde oy sayısı yüksek olan ürünlerin wlb değerinin de üst sıralarda olduğunu görüyoruz.
#bu hesaplamalrda en önemli olan sosyal ispat noktasını doğru yansıtmak olduğu için bu sıralama ve wlb değeri uyumlu gözükmektedir.
