import json
import ConMysql
from lxml import etree

from yq import mysql

with open('测试.json', 'r', encoding='utf-8') as fp:

    persons = json.load(fp)
    datas=persons['result']
    for data in datas:

        # 0股票代码 1股票简称 2现价 3涨跌幅 4主营产品 5总股本 6流通股本 7行业 8概念 9概念数量 10 流通市值 11流通占总股本比例
        # 12总市值 13净利润 14经营范围 15公司网站
        sql= """
                 insert into gp(id,gpdm,gpmc,xj,zdf,zycp,zgbnum,ltgbnum,hy,gn,gnsl,ltsz,ltzzgbbl,zsz,jlr,jyfw,gswz)
                 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
              """

        id=str(data[0])
        gpdm=str(data[0])
        gpmc=str(data[1])
        xj=str(data[2])
        zdf=str(data[3])
        zycp=str(data[4])
        zgbnum=str(data[5])
        ltgbnum=str(data[6])
        hy=str(data[7])
        gn=str(data[8])
        gnsl=str(data[9])
        ltsz=str(data[10])
        ltzzgbbl=str(data[11])
        zsz=str(data[12])
        jlr=str(data[13])
        jyfw=str(data[14])
        gswz=str(data[15])

        #记住元组对象不能赋值对象 hh=(1,2,3)这种是错误的
        mysql.inser_sql(sql,(id,gpdm,gpmc,xj,zdf,zycp,zgbnum,ltgbnum,hy,gn,gnsl,ltsz,ltzzgbbl,zsz,jlr,jyfw,gswz))

    conn = mysql.mysqlconnsingle().conn()
    conn.commit()
    conn.close()



    #with open('result.json', 'w', encoding='utf-8') as dp:
        #dp.write(json.dumps(persons, ensure_ascii=False))