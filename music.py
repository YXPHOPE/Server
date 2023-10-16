from requests import get
Head = {
"Host": "opqnext.com",
"Pragma": "no-cache",
"Referer": "http://opqnext.com/",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62}"}
def getLrcList(q,singer=''):
    r = get('http://opqnext.com/search.html?q='+q+' '+singer,headers=Head).text
    s = r.find('<div class="media position-relative">')
    e = r.rfind('"content_right"')-74
    r = r[s:e].split('<hr>')
    print(r)
    res = []
    bol = 0
    print(q,singer)
    try:
        for i in r:
            o = {'img':'','name':'','artist':'','album':'','duration':0,'url':''}
            s = i.find('http://')
            e = i.find('"',s)
            o['img'] = i[s:e]
            s = i.find('small> ',e)+7
            e = i.find('</',s)
            song = i[s:e]
            song = song.split(' - ')
            o['name'] = song[0]
            o['artist'] = song[1] if len(song)==2 else ''
            s = i.find('专辑: 《',e)+5
            e = i.find('》',s)
            o['album'] = i[s:e]
            s = i.find('</',e)
            o['duration'] = i[e+6:s]
            s = i.find('/edit',s)
            e = i.find('"',s)
            o['url'] = 'http://opqnext.com'+i[s:e]
            if o['name']==q and o['artist']==singer:
                o['lrc'] = getLrc(o['url'])
                bol=1
            res.append(o)
    except Exception as e:
        print('getLrcList Error:',str(e))
    if not bol:
        for i in res:
            if i['name']==q:
                i['lrc'] = getLrc(o['url'])
                break
    return res
def getLrc(u):
    r = get(u,headers=Head).text
    s = r.find('lyric-textarea" rows="12">')+26
    e = r.find('</textarea>',s)
    return r[s:e]
def Lrc(p):
    s = p.rfind('/')
    if s<0: s = p.rfind('\\')
    e = p.rfind('.')
    nm = p[s+1:e].split(' - ')
    singer = nm[0]
    name = nm[1] if len(nm)==2 else ''
    return getLrcList(name,singer)
print(Lrc('D:/Media/Music/Music/Ed Sheeran - Shape of You.mp3'))
print('')