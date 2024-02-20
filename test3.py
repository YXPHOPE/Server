from requests import get
url = 'https://book.sciencereading.cn/shop/book/Booksimple/offlineDownload.do?id=B5BB69820C73385D8E053020B0A0A140C000&readMark=1'
Headers = {
    'Cookie':'pgv_pvid=3522705104; __qc_wId=50; default_user=b09f6960ba5240a4aa6c8dae772aed1b; JSESSIONID=4DFB47BC770D68B670A3CF6692C017C1; userType=sso; JSESSIONID=7C991C4FFAC19B6BEE06F358F999A7F2; userIp=219.142.99.16; userName=yxp0; userAgency=%E5%8C%97%E4%BA%AC%E5%B8%88%E8%8C%83%E5%A4%A7%E5%AD%A6'
}
g = get(url,headers=Headers)
print(g.headers)
with open('1.pdf','wb') as f:
    f.write(g.content)