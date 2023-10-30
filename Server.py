from socket import socket, AF_INET, AF_INET6, SOCK_STREAM, gethostname, gethostbyname  # TCP服务器、常量
from json import loads, dumps  # json解析和封装
from threading import Thread  # 多线程
from sys import argv  # 命令行参数
from time import strftime, time, gmtime, sleep  # 格式化的时间
from platform import system as getOS
from mimetypes import guess_type
# 命令行：color、title
from os import getcwd, system, rename, remove, path, chdir, makedirs, scandir,_exit
from shutil import rmtree
from urllib.parse import unquote
from subprocess import Popen, PIPE, DEVNULL
from re import sub
from chardet import detect
from hashlib import sha1  # 建立websocket时握手需要，真tm没事找事做
from base64 import b64encode
from requests import get # 其实可以socket，但我不想弄SSL
from PIL import ImageGrab
from io import BytesIO
# 以下为windows用，linux不行
from pynput import mouse,keyboard
from win32api import GetConsoleTitle
from win32gui import FindWindow,ShowWindow
TM = FindWindow(0,GetConsoleTitle())
ShowWindow(TM,0)
ST = 0
Lim = 300*1024*1024
def showTM():
    global ST
    ST = 0 if ST==9 else 9
    ShowWindow(TM,ST)
# ShowWindow(HWND,int状态码0代表隐藏窗口)
Mouse = mouse.Controller()
Key = keyboard.Controller()
Magic = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
# 默认监听 0.0.0.0:80 改成 127.0.0.1的话需要在主函数中修改
Buffer = 1024
port = 80  # 默认端口
ADDRESS = ('0.0.0.0', port)  # 绑定地址 绑定失败会抛出异常: OSError
# :: 只有在socket(AF_INET6, SOCK_STREAM)绑定IPv6地址时有效，表示IPv6回环地址，且支持IPv4访问
# 127.0.0.1 环回地址，域名localhost默认指向它，只能在本机访问
# 0.0.0.0   服务器端，通过0.0.0.0匹配所有服务器IP，如果进程监听0.0.0.0，则可以接受来自其他IP的访问，对外开放
PWD = 981350 # 密码
PWD = str(PWD ^ 0x66666666)
noPWD = False
i = __file__.rfind('\\')
if i<0:i = __file__.rfind('/')
if i>0:chdir(__file__[:i])
Local = getcwd()  # 相对路径地址
Tokens = {}
Share = None # 共享地址(不用密码)
rmtIMG = BytesIO()
SL = 0
Win = getOS()
B = [1, 256, 256**2, 256**3, 256**4, 256**5, 256**6, 256**7]
LOG = True
AutoSleep = False
if Win == 'Windows':
    Win = True
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(2)
    windll.kernel32.SetThreadExecutionState(0x80000001)
else:
    Win = False
if Win:
    system("color")  # Windows CMD 颜色刷新
socket_server = None  # 负责监听的socket
conn_pool = []  # 连接池
ip_pool = {} #ip 池 限制同一ip连接数不超过16个，以及记录密码错误
Pipes = []  # 子程序池
Files = {}  # 文件池 {path:{last,file}}
AutoCloseSub = True
HP_ARG = {
    'listen port': 'number[0-65536]',
    'work folder': 'path'
}
HP_RUN = {
    '-c': 'connected clients number',
    '-h': 'show help infomation',
    '-l': 'toggle log status',
    '-p': 'show all pipes info',
    '-r': 'remove the closed pipes',
    '-s': 'toggle sleep',
    '-i': 'show connected IP',
    '-b': 'background',
    'n': 'show the nth pipe\'s stdout(100 lmt)',
    'kill n': 'kill the nth subprocess',
    'show n': 'show all stdout of the nth pipe',
    '"/Share/Path"': 'Share the absolute path without password'
}
__err = '\033[1;31mError\033[0m  '
CTjson = {"Content-Type": "application/json; charset=utf-8"}


def Help():
    s = ''
    if socket_server:
        hostname = gethostname()
        ip_address = gethostbyname(hostname)
        s += 'Listening '+ ADDRESS+ '    IP: '+ ip_address+'\n'
        s+='Runtime:\n'
        for i in HP_RUN:
            s+='  %8s  %s\n' % (i, HP_RUN[i])
    else:
        s+='Argument:\n'
        for i in HP_ARG:
            s+='  %12s  %s\n' % (i, HP_ARG[i])
    return s


Head = {"Host": "opqnext.com", "Pragma": "no-cache", "Referer": "http://opqnext.com/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62}"}

class IP:
    def __init__(self,addr) -> None:
        self.ip = addr
        self.qpwd = 0
        self.lastqpwd = 0
        self.conn = 0
def getLrcList(q, singer=''):
    r = get('http://opqnext.com/search.html?q=' + q+' '+singer, headers=Head).text
    s = r.find('<div class="media position-relative">')
    e = r.rfind('"content_right"')-74
    r = r[s:e].split('<hr>')
    res = []
    bol = 0
    # print(q,singer)
    try:
        for i in r:
            o = {'img': '', 'name': '', 'artist': '', 'album': '', 'duration': 0, 'url': ''}
            s = i.find('http://')
            e = i.find('"', s)
            o['img'] = i[s:e]
            s = i.find('small> ', e)+7
            e = i.find('</', s)
            song = i[s:e]
            song = song.split(' - ')
            o['name'] = song[0]
            o['artist'] = song[1] if len(song) == 2 else ''
            s = i.find('专辑: 《', e)+5
            e = i.find('》', s)
            o['album'] = i[s:e]
            s = i.find('</', e)
            o['duration'] = i[e+6:s]
            s = i.find('/edit', s)
            e = i.find('"', s)
            o['url'] = 'http://opqnext.com'+i[s:e]
            if not bol and o['name'] == q and o['artist'] == singer:
                o['lrc'] = getLrc(o['url'])
                bol = 1
            res.append(o)
    except Exception as e:
        print('getLrcList Error:', str(e))
    if not bol:
        for i in res:
            if i['name'] == q:
                i['lrc'] = getLrc(o['url'])
                break
    return res


def getLrc(u):
    r = get(u, headers=Head).text
    s = r.find('lyric-textarea" rows="12">')+26
    e = r.find('</textarea>', s)
    return r[s:e]


def Lrc(p):
    s = p.rfind('/')
    if s < 0:
        s = p.rfind('\\')
    e = p.rfind('.')
    nm = p[s+1:e].split(' - ')
    singer = nm[0]
    name = nm[1] if len(nm) == 2 else ''
    return getLrcList(name, singer)


class Chat:
    def __init__(self) -> None:
        self.chat = []
        self.clients = {}

    def con(self, ip, client):
        log('Chat   %-21s connected' % (ip))
        self.clients[ip] = client

    def push(self, dat={'name': '', 'chat': ''}, ip=''):
        dat['ip'] = ip
        dat['time'] = time()
        self.chat.append(dat)
        dat = packMes(dumps(dat))
        try:
            for k in self.clients:
                self.clients[k].socket.send(dat)
        except:
            pass

    def get(self, client, t=0):
        for i in self.chat:
            if i['time'] > t:
                client.socket.send(packMes(dumps(i)))

    def close(self, ip):
        log('Chat   %-21s disconnected' % (ip))
        self.clients.pop(ip)


CHAT = Chat()


class Client:
    def __init__(self, skt, address) -> None:
        self.socket = skt
        self.host = address[0]
        self.port = address[1]
        self.address = f'{address[0]}:{address[1]}'
        self.ws = False
        self.open = True
        self.req_pool = []
        self.file = None
        self.path = None
        ip_pool[self.host].conn+=1

    def close(self, client=0):
        self.open = False
        self.socket.close()
        ip_pool[self.host].conn-=1
        if self.file:
            self.file.close()
        if self.ws:
            CHAT.close(self.address)
        if client:
            client.req_pool.remove(self)
        else:
            conn_pool.remove(self)
        log('Client %-21s disconnected' % (self.address))


def toutf(s=b''):
    # 因为Popen的编码问题设计的函数，后来直接通过其参数encoding解决了
    if not isinstance(s, bytes):
        s = s.encode('utf-8')
    enc = detect(s)['encoding'].lower()
    if enc != 'utf-8':
        s = s.decode(enc).encode('utf-8')
    return s


def Kill(proc, timeout, client):
    sleep(timeout)
    proc.kill()
    if proc.poll() == None:
        proc.kill()
    if client.open:
        client.socket.send(b'0\r\n\r\n')
        client.close()


def newkill(proc, client, timeout=5):
    thr = Thread(target=Kill, args=(proc, timeout, client,))
    thr.start()


def T():
    sec = str(time())
    sec = sec[sec.find('.'):][:4]
    return strftime('[%H:%M:%S'+sec+'] ')


def log(s):
    if LOG:
        print(T()+s+'\n', end='')


def parse_url(url=''):
    res = {"port": 80, "path": "/"}
    i = url.find('://', 0, 10)
    if i > 0:
        res['protocal'] = url[:i]
        if res['protocal'] == 'https':
            res['port'] = 443
        url = url[i+3:]
    s = url.find('/')
    if s < 0:
        s = len(url)
    else:
        res['path'] = url[s:]
    i = url.find(':', 0, s)
    if i > 0:
        res['host'] = url[:i]
        res['port'] = int(url[i+1:s])
    else:
        res['host'] = url[:s]
    return res

def parse_head(head=b''):
    header = {}
    if isinstance(head, bytes):
        head = head.decode()
    head = head.split('\r\n')
    head[0] = head[0].split()
    header['Method'] = head[0][0]
    header['path'] = unquote(head[0][1][1:])
    header['params'] = {}
    header['token'] = None
    if header['path'].rfind('?')>0:
        header['path'],param = header['path'].split('?')
        param = param.split('&')
        ps = {}
        for i in param:
            k,v = i.split('=')
            ps[k]=v
        if ps.get('token'):header['token'] = ps['token']
        header['params'] = ps
    head.pop(0)
    head = [i.split(': ', 1) for i in head]
    i = 0
    while i < len(head):
        if head[i][0] != '':
            header[head[i][0]] = head[i][1]
        i += 1
    if not header['token']:header['token'] = header.get('Token')
    if header.get('Cookie'):
        h = header['Cookie'].split('; ')
        ps = {}
        for i in h:
            k,v = i.split('=',)
            ps[k]=v
        header['Cookie'] = ps
        if ps.get('token') and not header['token']:header['token'] = ps['token']
    return header


def pack(method='', url='', header={}, data='', res=''):
    # 打包完整的 HTTP 请求
    dat = r''
    if res:
        # 作为服务器返回信息
        dat += res+'\r\n'
    else:
        # 作为客户端请求信息
        dat += method.upper()+' '
        m = url.find('://', 0, 10)
        if m > 0:
            url = url[m+3:]
        m = url.find('/')
        if (m > 0):
            host = url[0:m]
            dat += url[m:]
        else:
            host = url
            dat += '/'
        dat += f' HTTP/1.1\r\nHost: {host}\r\n'
        if isinstance(header, dict):
            if 'Connection' not in header:
                header['Connection'] = 'close'
    # 设置 内容大小 ，连接 data
    if not isinstance(data, bytes):
        data = data.encode()
    header['Content-Length'] = len(data)
    header['Access-Control-Allow-Origin'] = '*'
    for i in header:
        dat += f'{i}: {header[i]}\r\n'
    dat += '\r\n'
    # 返回二进制的内容
    return dat.encode()+data


def packMes(d=b'',text = True):
    if not isinstance(d, bytes):
        d = d.encode()
    dat = b'\x81' if text else b'\x82'
    msglen = len(d)
    if msglen < 126:
        dat += msglen.to_bytes(1, 'big')
    elif msglen < 65535:
        dat += b'\x7e'+msglen.to_bytes(2, 'big')
    else:
        dat += b'\x7f'+msglen.to_bytes(8, 'big')
    dat += d
    return dat


def getLen(m=b''):
    offset = 2
    # fin = m[0]&0b10000000 # 假设全部正确
    # mask = m[1] & 0b10000000 # 掩码：客户端来的消息必须经过格式化=1，向客户端发送帧时，不要对其进行掩码
    # opcode = m[0] & 0b00001111 # 操作码：0x0 表示延续，0x1 表示文本 (总是用 UTF-8 编码)，0x2 表示二进制 0x8表示关闭
    # if mask==0:fin=0
    msglen = m[1] & 0b01111111
    if msglen == 126:
        msglen = m[3]+m[2]*B[1]
        offset = 4
    elif msglen == 127:
        msglen = m[9]+m[8]*B[1]+m[7]*B[2]+m[6]*B[3]+m[5]*B[4]+m[4]*B[5]+m[3]*B[6]+m[2]*B[7]
        offset = 10
    return (msglen, offset)


def parseMes(m=b'', msglen=0, offset=0):
    dec = b''
    if msglen != 0:
        masks = m[offset:offset+4]
        offset += 4
        for i in range(msglen):
            dec += (m[offset+i] ^ masks[i % 4]).to_bytes(1, 'big')
    return dec
# 不管，必须一帧发完消息，需要拼接的懒得做


UnknownErr = pack(res="HTTP/1.1 400 Bad Request", header=CTjson, data=dumps({"code": 400, "message": "Unknown Error"}))
pwdErr = pack(res="HTTP/1.1 403 Forbidden", header=CTjson, data=dumps({"code": 403, "message": "Wrong password"}))
etgFavi = '63ef9902779b131f8d48cb2c4f6cd083'
favi = pack(res='HTTP/1.1 200 OK', header={'Content-Type': 'image/svg+xml', 'Cache-Control': 'public, max-age=31536000', 'ETag': etgFavi}, data='<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.90472 0.00013087C7.24498 0.00316295 6.61493 0.0588153 6.06056 0.15584C4.42744 0.441207 4.13093 1.0385 4.13093 2.14002V3.59479H7.99018V4.07971H4.13093H2.68259C1.56098 4.07971 0.578874 4.7465 0.271682 6.01495C-0.0826595 7.4689 -0.0983765 8.37618 0.271682 9.89434C0.546011 11.0244 1.20115 11.8296 2.32275 11.8296H3.64965V10.0856C3.64965 8.82574 4.75178 7.71441 6.06056 7.71441H9.91531C10.9883 7.71441 11.8449 6.84056 11.8449 5.77472V2.14002C11.8449 1.10556 10.9626 0.328486 9.91531 0.15584C9.25235 0.046687 8.56447 -0.00290121 7.90472 0.00013087ZM5.81767 1.17017C6.2163 1.17017 6.54184 1.49742 6.54184 1.89978C6.54184 2.30072 6.2163 2.62494 5.81767 2.62494C5.41761 2.62494 5.0935 2.30072 5.0935 1.89978C5.0935 1.49742 5.41761 1.17017 5.81767 1.17017Z" fill="url(#paint0_linear)"/><path d="M12.3262 4.07971V5.77472C12.3262 7.08883 11.1998 8.19488 9.9153 8.19488H6.06055C5.00466 8.19488 4.13092 9.0887 4.13092 10.1346V13.7693C4.13092 14.8037 5.04038 15.4122 6.06055 15.709C7.28217 16.0642 8.45364 16.1285 9.9153 15.709C10.8869 15.4307 11.8449 14.8708 11.8449 13.7693V12.3145H7.99017V11.8296H11.8449H13.7746C14.8962 11.8296 15.3141 11.0558 15.7042 9.89434C16.1071 8.69865 16.09 7.5488 15.7042 6.01495C15.427 4.91058 14.8976 4.07971 13.7746 4.07971H12.3262ZM10.1582 13.2843C10.5583 13.2843 10.8824 13.6086 10.8824 14.0095C10.8824 14.4119 10.5583 14.7391 10.1582 14.7391C9.75955 14.7391 9.43402 14.4119 9.43402 14.0095C9.43402 13.6086 9.75955 13.2843 10.1582 13.2843Z" fill="url(#paint1_linear)"/><defs><linearGradient id="paint0_linear" x1="1.25961e-08" y1="1.08223e-08" x2="8.81664" y2="7.59597" gradientUnits="userSpaceOnUse"><stop stop-color="#5A9FD4"/><stop offset="1" stop-color="#306998"/></linearGradient><linearGradient id="paint1_linear" x1="10.0654" y1="13.8872" x2="6.91912" y2="9.42957" gradientUnits="userSpaceOnUse"><stop stop-color="#FFD43B"/><stop offset="1" stop-color="#FFE873"/></linearGradient></defs></svg>')
faviSame = pack(res='HTTP/1.1 304 Not Modified', header={'Content-Type': 'image/svg+xml', 'Cache-Control': 'public, max-age=31536000', 'ETag': etgFavi})
index = pack(res='HTTP/1.1 200 OK', header={"Content-Type": "text/html; charset=utf-8", 'Cache-Control': 'public, max-age=31536000'}, data="""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta http-equiv="refresh" content="0; url=/index.html"></head><body></body></html>""")
successResp = pack(res='HTTP/1.1 200 OK', header=CTjson, data=dumps({"code": 200, "message": "success"}))

Diskdir = {'folder': [], 'file': [], 'dir': ''}
for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    disk = c+':'
    if path.isdir(disk):
        Diskdir['folder'].append({"name": disk, "mtime": "", "mts": ""})

def checkPWD(p=''):
    p = str(p)
    return noPWD or p==PWD or Tokens.get(p,0)>0


def getFile(loc, head=False, rang='', pETag='', token=0):
    resp = UnknownErr
    if rang:
        rang = rang[rang.find('=')+1:]
    cache = True
    rg = rang
    if loc == "":
        return index
    elif loc == "*":
        dir = Diskdir
        resp = pack(res='HTTP/1.1 200 OK', header={'Content-Type': 'application/json'}, data=dumps(dir))
        return resp
    elif loc != 'favicon.ico' or path.isfile(path.abspath(loc)):
        loc = path.abspath(loc).replace('\\','/')
    else:
        if pETag == etgFavi:
            return faviSame
        else:
            return favi
    if path.isdir(loc):
        # 列出具体目录
        if not checkPWD(token):
            if Share and loc[:SL]==Share:
                pass
            else:
                return pwdErr
        # html = loc
        # if html[-1] != '/':
        #     html += '/'
        # html += 'index.html'
        # if path.isfile(html):
        #     loc = html
        #     resp = pack(res='HTTP/1.1 200 OK', header={'Content-Type': 'text/html'}, data='<!doctype html><html><head><meta http-equiv="refresh" content="0; url=/'+loc+'"><title>Redirect...</title></head></html>')
        # else:
        log('%-7s%-21s %s' % ('GET', 'listDir', loc))
        # 返回目录信息
        try:
            filelist = scandir(loc)
            dir = {'folder': [], 'file': [], 'dir': loc.replace('\\', '/')}
            for i in filelist:
                s = i.stat()
                f = {'name': i.name, 'mtime': s.st_mtime, 'mts': strftime('%Y/%m/%d %H:%M', gmtime(s.st_mtime))[2:]}
                if i.is_file():
                    f['size'] = s.st_size
                    f['type'] = guess_type(i.name)[0]
                    if f['type']:
                        f['type'] = f['type'][:f['type'].find('/')]
                    dir['file'].append(f)
                else:
                    dir['folder'].append(f)
            resp = pack(res='HTTP/1.1 200 OK', header=CTjson, data=dumps(dir))
        except Exception as e:
            resp = pack(res="HTTP/1.1 400 Bad Request", header=CTjson, data=dumps({"code": 400, "message": str(e)}))
    elif path.isfile(loc):
        if loc.find(Local)!=0 and not checkPWD(token) and loc[:SL]!=Share:
            return pwdErr
        size = path.getsize(loc)
        if size < 20971520:
            cache = False
        curMod = path.getmtime(loc)
        ETag = f'W/"{size}-{curMod}"'
        header = {'Content-Length': size, 'Content-Type': guess_type(loc)[0], 'Accept-Ranges': 'bytes', 'Last-Modified': strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime(curMod)), "Cache-Control": "public, max-age=31536000", 'ETag': ETag}
        if pETag == ETag:
            resp = pack(res='HTTP/1.1 304 Not Modified', header=header)
        elif head:
            resp = pack(res='HTTP/1.1 200 OK', header=header)
        else:
            if rang:  # 只接受一组值，多组的特喵的自己再请求一次...别改这里，下大文件很容易出错
                rang = rang.split(', ')[0].split('-')
                if rang[0] == '':
                    rang[1] = int(rang[1])
                    rang[0] = size-rang[1]
                    rang[1] = size
                elif rang[1] == '':
                    rang[0] = int(rang[0])
                    maxs = rang[0]+2097151  # 2Mb
                    rang[1] = size-1 if (not cache) or size - rang[0] < maxs else rang[0]+maxs
                else:
                    rang[0] = int(rang[0])
                    rang[1] = int(rang[1])
                rang.append(rang[1]-rang[0]+1)
                if rang[0] < 0 or rang[1] < rang[0] or rang[1] > size:
                    resp = pack(res='HTTP/1.1 416 Range Not Satisfiable', data='')
            else:
                rang = [0,size-1,size]
            if rang[2]>Lim:
                rang[1] = rang[0]+Lim-1
                rang[2] = Lim
            try:
                file = None
                if cache:
                    if not Files.get(loc):
                        file = open(loc, 'rb')
                        Files[loc] = {"last": time(), "file": file}
                        log('\033[1;33m%-7s\033[0m%-21s %s' % ('GET', (rg if rg else 'whole')+('  HEAD' if head else ''), loc))
                    else:
                        file = Files[loc]['file']
                        Files[loc]['last'] = time()
                else:
                    file = open(loc, 'rb')
                    log('\033[1;33m%-7s\033[0m%-21s %s' % ('GET', (rg if rg else 'whole')+('  HEAD' if head else ''), loc))
                end = 0
                # 小心截断，100-200指起始为0，从100-200中的101个字节，包括首尾，如果不加1，你永远缺那么一个字节哈哈   下面先找到起始位置，再读取长度
                file.seek(rang[0])
                c = file.read(rang[2])
                header['Content-Length'] = rang[2]
                header['Content-Range'] = f'bytes {rang[0]}-{rang[1]}/{size}'
                a = '206 Partial Content' if rang[2]<size else '200 OK'
                resp = pack(res='HTTP/1.1 '+a, header=header, data=c)
                if not cache:
                    file.close()
            except Exception as e:
                resp = pack(res="HTTP/1.1 400 Bad Request", header=CTjson, data=dumps({"code": 400, "message": str(e)}))
                log('\033[1;33m%-7s\033[0m%-21s %s' % ('GET', (rg if rg else 'whole') +
                    ('  HEAD' if head else ''), loc+" Fail: "+str(e)))
    else:
        resp = pack(res='HTTP/1.1 404 Not Found', data='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>404</title></head><body style="padding: 5%;width: 500px;margin: 0 auto;"><div style="font: 700 32px/60px Sans-serif">404 Not Fount</div><div>Message: The page you are looking for is not found, click <a href="/">here</a> to go back to the homepage.</div><div style="padding: 10px 0;">Server: Python</div></body></html>')
        log('\033[1;33m%-7s\033[0m%-21s %s' % ('GET', (rg if rg else 'whole')+('  HEAD' if head else ''), loc+" Not Found"))
    return resp


def accept_client():
    # 线程1：监听连接
    while True:
        try:
            # 阻塞，等待客户端连接，当 socket_server 关闭时，会抛出异常
            skt, address = socket_server.accept()
        except:
            return
        # 加入连接池
        if not ip_pool.get(address[0]):
            ip_pool[address[0]] = IP(address[0])
        client = Client(skt, address)
        conn_pool.append(client)
        # 同一IP连接数大于16则拒绝连接
        if ip_pool[address[0]].conn>16:
            client.close()
            continue
        # 子线程：对每个连接的数据进行处理, args=tuple(arg1, arg2, ... , )
        thread = Thread(target=message_handle, args=(client,))
        # 设置成守护线程
        thread.setDaemon(True)
        thread.start()

def message_handle(client):
    log('Client %-21s connected' % (client.address))
    # 循环等待请求
    msg = 'Unknown Error'
    wsl = (0, 0)
    while client.open:
        resp = ''
        # 接收数据头head与数据主体data
        data = b''
        head = ''
        l = 0  # recv的总长度
        m = 0 if client.ws else -1   # 请求头与内容的分隔位置
        # 根据请求头的长度及时跳出循环，防阻塞
        buf = Buffer
        lenth = 0x7FFFFFFF
        try:
            while l <= lenth:
                rec = client.socket.recv(buf)
                if client.ws:
                    wsl = getLen(rec[:10])
                    lenth = wsl[0]+wsl[1]
                elif len(rec) == 0:
                    client.close()
                    return  # 断开连接时，长度为0（都被断开了，也就没必要再响应了）
                data += rec
                l += len(rec)
                if m < 0:
                    m = data.find(b'\r\n\r\n')
                    if m > 0:
                        head = data[0:m].decode()
                        lenth = head.find('Content-Length: ')
                        if lenth > 0:
                            e = head.find('\r\n', lenth)
                            if e == -1:
                                lenth = head[lenth+16:]
                            else:
                                lenth = head[lenth+16:e]
                            lenth = int(lenth)+len(head)+3
                        else:
                            lenth = 0  # 已经收完了header部分却没有lenth说明没有正文
                if l > 1047552:  # >1024*1023也即达到1KB 每次收取到的rec长度并不一定等buffer
                    buf = 16384  # 16KB
        except:
            break
        # 解析请求头
        if client.ws:
            dat = parseMes(data, wsl[0], wsl[1])
            if dat == b'\x03\xe9':
                client.close()
            elif (wsl[0]):
                try:
                    # 收发数据还是以json格式 {name:,chat,time}
                    dat = dat.decode()
                    dat = loads(dat)
                    if dat.get('frame')!=None:
                        img = ImageGrab.grab()
                        rmtIMG.seek(0)
                        img.save(rmtIMG,"JPEG")
                        rmtIMG.seek(0)
                        client.socket.send(packMes(rmtIMG.read(),0))
                    elif dat.get('control'):
                        typ = dat.get('type')
                        xy = dat.get('xy')
                        key = dat.get('key')
                        if xy:
                            xy = (xy[0],xy[1])
                        if typ=='move':
                            Mouse.position = xy
                        elif typ=='click':
                            Mouse.position = xy
                            Mouse.click(mouse.Button.left)
                        elif typ=='wheel':
                            Mouse.position = xy
                            dxy = dat.get('dxy',[0,0])
                            Mouse.scroll(dxy[0],dxy[1])
                        elif typ=='mousedown':
                            Mouse.position = xy
                            Mouse.press(mouse.Button.left)
                        elif typ=='mouseup':
                            Mouse.position = xy
                            Mouse.release(mouse.Button.left)
                        elif typ=='context':
                            Mouse.position = xy
                            Mouse.press(mouse.Button.right)
                            Mouse.release(mouse.Button.right)
                        elif typ=='keydown':
                            if len(key)>1:
                                Key.press(keyboard.Key.__getitem__(key))
                            else: Key.press(key)
                        elif typ=='keyup':
                            if len(key)>1:
                                Key.release(keyboard.Key.__getitem__(key))
                            else: Key.release(key)
                        elif typ=='tap':
                            if len(key)>1:
                                Key.tap(keyboard.Key.__getitem__(key))
                            else: Key.tap(key)
                    elif dat.get('time', -1) != -1:
                        CHAT.get(client, dat['time'])
                    elif dat.get('chat'):
                        CHAT.push(dat, client.address)
                except Exception as e:
                    client.socket.send(packMes(dumps({'message': 'Error: '+str(e)})))
            else:
                client.socket.send(b'\x880')
                client.close()
                break
            continue
        head = parse_head(head)
        data = data[m+4:]
        if head['Method'].upper() == "GET":
            if head.get('Upgrade') == 'websocket':
                if head['path'] == ':chat' or (head['path']==':remote' and checkPWD(head['token'])):
                    client.ws = head['path']
                    key = head.get('Sec-WebSocket-Key').encode()+Magic
                    key = b64encode(sha1(key).digest())
                    CHAT.con(client.address, client)
                    resp = b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nServer: WebSocket++/0.7.0\r\nSec-WebSocket-Accept: '+key+b'\r\n\r\n'
                else:
                    resp = UnknownErr
            elif head['path']==':getWH':
                wh = ImageGrab.grab().size
                resp = pack(res='HTTP/1.1 200 OK',data=f'{wh[0]},{wh[1]}')
            else:
                resp = getFile(head['path'], rang=head.get('Range'), pETag=head.get('If-None-Match'), token=head.get('token'))
        elif head['Method'].upper() == "POST":
            if data[:15]!=b'{"oprt":"token"' and head['path'][:SL]!=Share and  not checkPWD(head['token']):
                resp = pwdErr
            elif head['path'] and head.get('Content-Type') == 'application/octet-stream':
                log("Post   File %-16s %s" %
                    (head['Content-Length'], head['path']))
                try:
                    f = open(head['path'], 'wb')
                    f.write(data)
                    f.close()
                    resp = successResp
                except Exception as e:
                    msg = str(e)
            elif head.get('Content-Type') == "application/json" and len(data) > 0:
                try:
                    data = loads(data.decode())
                except:
                    msg = 'Invalid Data'
                    break
                oprt = data.get('oprt')
                if oprt == 'cmd':
                    if data.get('cmd'):
                        cmd = data['cmd']
                        cmds = cmd+' '
                        cmds = cmd if len(cmd) <= 50 else cmds[:cmds.rfind(' ', 0, 60)]
                        if data.get('return'):
                            tm = data.get('timeout', 3)
                            log('\033[35mcmd   \033[0m return  timeout=%-5d %s' %
                                (tm, cmds))
                            # 设置timeout默认为3s
                            # 可交互的终端太难了，依托答辩，还是依靠ssh吧
                            try:
                                process = Popen(cmd, shell=True, bufsize=1, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True, encoding='utf-8')
                                Pipes.append(process)
                                newkill(process, client, tm)
                                # 去除退格\x08和ESC控制符
                                output = sub(r'\x08|(\x1B\[\??\d*(;\d+)*[mA-Ksulh])', '', process.stdout.readline()).encode()
                                # 要用16进制表示每个节的大小
                                resp = b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n' + \
                                    ('%x\r\n' % (len(output))
                                     ).encode()+output+b'\r\n'
                                client.socket.send(resp)
                                while output or process.poll() == None:
                                    output = sub(r'\x08|(\x1B\[\??\d*(;\d+)*[mA-Ksulh])', '', process.stdout.readline()).encode()
                                    resp = (f'{hex(len(output))[2:]}\r\n').encode()+output+b'\r\n'
                                    client.socket.send(resp)
                                if client.open:
                                    client.socket.send(b'0\r\n\r\n')
                                    client.close()
                                break
                            except Exception as e:
                                msg = str(e)
                        else:
                            log('\033[35mcmd\033[0m    no return             '+cmds)
                            try:
                                proc = Popen(cmd, shell=True, bufsize=0, stdout=PIPE, stderr=PIPE, encoding='utf-8')
                                Pipes.append(proc)
                                # 默认等待2s，如果结束了就返回结果
                                sleep(2)
                                dat = ''
                                if proc.poll() != None:
                                    dat = proc.stdout.read()
                                if dat == '':
                                    dat = 'start '+cmd
                                resp = pack(res='HTTP/1.1 200 OK', header={"Content-Type": "text/plain; charset=utf-8"}, data=dat)
                            except Exception as e:
                                msg = str(e)
                    else:
                        msg = "Parameter Error (expect key of 'cmd')"
                elif oprt == 'token':
                    ip = ip_pool[client.host]
                    ip.lastqpwd = time()
                    ip.qpwd +=1
                    if ip.qpwd>3:
                        msg = "Please wait for a moment and try again later."
                    elif data.get('pwd') and str(data['pwd'])==PWD:
                        tok = str(int(ip.lastqpwd * time()* (ip.lastqpwd%9)/9))
                        Tokens[tok] = ip.lastqpwd
                        resp = pack(res='HTTP/1.1 200 OK',header = CTjson,data=dumps({'code':200,'token':tok}))
                    else:
                        msg = "No pwd or the password is incorrect!"
                elif oprt == 'get':
                    if data.get('file'):
                        resp = getFile(data['file'])
                    else:
                        msg = "Parameter Error (expect key of 'file')"
                    pass
                elif oprt == 'delete':
                    if data.get('type') == 'folder':
                        rmtree(data.get('path'))
                        resp = successResp
                    elif data.get('type') == 'file':
                        remove(data.get('path'))
                        resp = successResp
                    else:
                        msg = "No type param or Wrong type"
                elif oprt == 'rename':
                    try:
                        rename(data.get('path'), data.get('name'))
                        resp = successResp
                    except Exception as e:
                        msg = str(e)
                elif oprt == 'new':
                    if data.get('type') == 'folder':
                        makedirs(data.get('path'))
                    elif data.get('type') == 'file':
                        f = open(data.get('path'))
                        f.close()
                    else:
                        msg = "No type param or Wrong type"
                elif oprt == 'lrc':
                    if data.get('path'):
                        p = data['path']
                        p = p[:p.rfind('.')]+'.lrc'
                        if path.exists(p):
                            resp = getFile(p,token=head['token'])
                        else:
                            try:
                                res = Lrc(data['path'])
                                resp = pack(res='HTTP/1.1 200 OK', header=CTjson, data=dumps(res))
                            except Exception as e:
                                msg = str(e)
                    elif data.get('url'):
                        try:
                            l = getLrc(data['url'])
                            resp = pack(res='HTTP/1.1 200 OK', header={"Content-Type": "text/plain; charset=utf-8"}, data=l)
                        except Exception as e:
                            msg = str(e)
                    else:
                        msg = "Parameter Error (expect key of 'path')"
                else:
                    msg = 'Unsupport Operation'
            else:
                msg = 'Unsupport Content'
        elif head['Method'].upper() == "HEAD":
            resp = getFile(head['path'], head=True)
        elif head['Method'].upper() == 'OPTIONS':
            # 恶心巴拉的跨域CORS，恶心的预检请求
            resp = b'HTTP/1.1 204 No Content\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: POST, GET, HEAD, OPTIONS\r\nAccess-Control-Allow-Headers: *\r\nAccess-Control-Expose-Headers: *\r\nAccess-Control-Max-Age: 31536000\r\nAllow: OPTIONS, GET, HEAD, POST\r\nServer: python\r\n\r\n'
        else:
            msg = 'Unsupport Method'
        try:
            if resp:
                client.socket.send(resp)
                if client.ws==':chat':
                    client.socket.send(packMes(client.address))
            else:
                resp = pack(res="HTTP/1.1 400 Bad Request", header=CTjson, data=dumps({"code": 400, "message": msg}))
                client.socket.send(resp)
        except:
            client.close()
    if client.open:
        try:
            if resp:
                client.socket.send(resp)
            else:
                resp = pack(res="HTTP/1.1 400 Bad Request", header=CTjson, data=dumps({"code": 400, "message": msg}))
                client.socket.send(resp)
        except:
            pass
        client.close()
    del client


def maintain():
    while True:
        sleep(120)
        now = time()
        w = []
        for i in Files:
            if now-Files[i]['last'] > 60:
                Files[i]['file'].close()
                w.append(i)
                # Files.pop(i) 遍历的同时pop会不会出问题？RuntimeError: dictionary changed size during iteration
                # 只能用这种损失性能的办法（两次遍历，n次查找）
        for i in w:
            log('\033[33mFile   \033[0m%-21s \033[0m%s' % ('closed', i))
            Files.pop(i)
        w = []
        for i in ip_pool:
            p = ip_pool[i]
            if p.conn==0 and now-p.lastqpwd>120:
                w.append(i)
            elif p.qpwd and now-p.lastqpwd>60:
                p.qpwd=0
        for i in w:
            ip_pool.pop(i)
        w = []
        for i in Tokens:
            if now-Tokens[i]>43200:w.append(i)
        for i in w:
            Tokens.pop(i)
def Manage(cmd):
    f = ''
    p = 0
    global Files, Pipes, AutoCloseSub, AutoSleep
    if len(cmd) > 5:
        if cmd[5:].isdigit():
            f = cmd[:4]
            p = int(cmd[5:])-1
            if p < 0 or p >= len(Pipes):
                return "Out of Pipes range"
    if cmd == '-c':
        return "Online clients: "+str(len(conn_pool))
    elif cmd == '-h':
        return Help()
    elif cmd == "-l":
        global LOG
        LOG = not LOG
        if LOG:
            return "log enabled."
        else:
            return "log disabled."
    elif cmd == '-f':
        s = ''
        for i in Files:
            s+=str(i)+'\n'
        return s
    elif cmd=='-i':
        s = ''
        for i in ip_pool:
            s+=ip_pool[i].ip+' '+str(ip_pool[i].conn)+'\n'
        return s
    elif cmd == '-a':
        s = ''
        for i in Pipes:
            if i.poll() != None:
                s+= 'closed\n'
            try:
                out = i.stdout.read(i.stdout.seek(0, 2))
                if out[151] < ' ' or out[151] > 'z':
                    out[151] = ' '
                if out[152] < ' ' or out[152] > 'z':
                    out[152] = ' '
                l = len(out)
                if l < 150:
                    s+=out
                else:
                    s+=out[l-100:]
            except:
                pass
        return s
    elif cmd == '':
        if input("\033[1A\033[1;31m    One more time to confirm exit\033[0m ") == '':
            return False
    elif cmd == '-p':
        l = len(Pipes)
        if l == 0:
            return 'No pipes'
        else:
            s = ''
            for i in range(l):
                s+=str(i+1)+ ' running' if Pipes[i].poll() != None else ' closed'+ Pipes[i].args+'\n'
            return s
    elif cmd == '-r':
        l = len(Pipes)
        n = 0
        p = []
        for i in range(l):
            if Pipes[i].poll() != None:
                n += 1
            else:
                p.append(Pipes[i])
        Pipes = p
        return f'Pipes {l}, closed {n}, remaining {l-n}'
    elif len(cmd)>2 and (cmd[0]=="/" or cmd[1]==":"):
        global SL,Share
        if Win :cmd = cmd.replace('/','\\')
        if not Share:
            Diskdir['folder'].append({})
        if path.isdir(cmd):
            cmd = cmd.replace('\\','/')
            if cmd[-1]=='/':
                cmd = cmd[:-1]
            Share = cmd
            Diskdir['folder'][-1] = {"name": Share, "mtime": "", "mts": ""}
            SL = len(cmd)
            return "Sharing Path: "+Share
        else:
            return cmd+' is not an existing or valid path!'
    elif cmd.isdigit():
        i = int(cmd)
        if i > 0 and i <= len(Pipes):
            i -= 1
            out = Pipes[i].stdout.read(Pipes[i].stdout.seek(0, 2))
            l = len(out)
            if l < 150:
                return out
            else:
                return out[l-100:]
        else:
            return 'Out of Pipes range'
    elif cmd == '-k':
        AutoCloseSub = not AutoCloseSub
        if AutoCloseSub:
            return 'Auto close subprocess before exit'
        else:
            return 'Keep the subprocess after exit'
    elif cmd=='-b':
        ShowWindow(TM,0)
        return 'Background running...'
    elif cmd == '-s':
        AutoSleep = not AutoSleep
        if Win:
            if AutoSleep:
                windll.kernel32.SetThreadExecutionState(0x80000000)
                return 'Auto sleep when leave for certain period'
            else:
                windll.kernel32.SetThreadExecutionState(0x80000001)
                return 'Wake locked, computer will not sleep.'
        else:
            return 'This is not a windows system, sleep has no supported yet.'
    elif f == 'show':
        s = f'Pipes[{p+1}]\n'
        out = Pipes[p].stdout.read(Pipes[p].stdout.seek(0, 2))
        if out[151] < 34 or out[151] > 122:
            out[151] = ' '
        if out[152] < 34 or out[152] > 122:
            out[152] = ' '
        return s+out
    elif f == 'kill':
        Pipes[p].kill()
        return f'Killed Pipes[{p+1}]'
def close():
    socket_server.close()
    log(f'Server {ADDRESS} closed.')
    if Win: windll.kernel32.SetThreadExecutionState(0x80000000)
    for i in Files:
        Files[i]['file'].close()
    if AutoCloseSub and len(Pipes):
        log(f'Closing subprocess...')
        for i in Pipes:
            if i.poll() != None:
                i.kill()
        log(f'Closed')
    print('\033[1;31mExit.\033[0m')
    _exit(0)
def thshow():
    with keyboard.GlobalHotKeys({'<ctrl>+<shift>+p': showTM}) as h:
        h.join()
def thquit():
    with keyboard.GlobalHotKeys({'<ctrl>+<shift>+q': close}) as h:
        h.join()
def init():
    global socket_server, ADDRESS, Local, AutoCloseSub, Pipes, LOG, CHAT, AutoSleep,Share,SL
    print('\033[1;33mPython Server\033[0m')
    for i in range(len(argv)):
        if i == 0:
            continue
        if argv[i].isdigit():
            port = int(argv[i])
            ADDRESS = (ADDRESS[0], port)
        elif argv[i] == '-h' or argv[i] == '/?':
            print(Help())
            return
        elif path.isdir(argv[i]):
            chdir(argv[i])
            Local = path.abspath(argv[i])
    try:
        socket_server = socket(AF_INET, SOCK_STREAM)  # 创建 socket 对象
        socket_server.bind(ADDRESS)
        socket_server.listen(16)  # 等待未处理请求数（有很多人理解为最大连接数，其实是错误的）
    except Exception as e:
        log(__err+str(e))
        return
    ADDRESS = f'{ADDRESS[0]}:{ADDRESS[1]}'
    hostname = gethostname()
    ip_address = gethostbyname(hostname)
    print(strftime('Date: %Y/%m/%d %a'), '   IP:', ip_address)
    Local = Local.replace('\\', '/')
    log('\033[33mServer \033[1;33m%-21s \033[0mstarted at \033[33m%s\033[0m' % (ADDRESS, Local))
    if Win:
        system('title Server '+ADDRESS+' '+Local)
    # 线程1：监听连接
    thread1 = Thread(target=accept_client, daemon=True)
    thread1.start()
    # 线程2：维护回收
    thread2 = Thread(target=maintain, daemon=True)
    thread2.start()
    thread3 = Thread(target=thquit,daemon=True)
    thread3.start()
    thread4 = Thread(target=thshow,daemon=True)
    thread4.start()
    # 线程3：终端输入
    try:
        while True:
            try:
                cmd = input("")
                s = Manage(cmd)
                if s==False:
                    break
                else:print(s)
            except Exception as e:
                print(__err, str(e))
    except KeyboardInterrupt:
        pass
    close()


if __name__ == '__main__':
    init()

"""
本篇主要遇到并解决的问题：
1. HTTP
   CORS：strict-origin的网站，跨域请求R时时先发送Head请求，返回Allow-Access三大件，判断原先请求R的origin、method、header是否符合，符合才发送
   trunked：分块传输，不能设置Content-Type，encoding，否则就把主体当普通报文处理了，也不用设置Content-Length，Header\r\n\r\n16进制报文长度\r\n报文\r\n0\r\n\r\n例如 HTTP/1.1 200 OK\r\nTransfer-Encoding: trunked\r\n\r\na\r\n0123456789\r\n1c\r\n29bytes\r\n0\r\n\r\n
   Range: bytes=10-20 指 file[10:21]，bytes=[0->size|不写=0，包含]-[0->size-1|包含]  bytes=-50代表取最后50个字节，file[size-50:size] 或者 seek(size-50),read(50)
          bytes 0-99/100 100字节取全部
2. Socket
   IPv4：AF_INET，0.0.0.0,127.0.0.1
   IPv6：AF_INET6，::，
3. Websocket:
   https://developer.mozilla.org/zh-CN/docs/Web/API/WebSockets_API/Writing_WebSocket_servers
   client: [1fin|2RSV|3RSV|4RSV|5-8opcode] [1m|7len] {126:2*8len|127:8*8len} [m?4*8mask] data
   server: [1fin|000|5-8opcode]            [0m|7len] {len} |data
   opcode = 1:text   8: close
3. Pipe
   Popen(cmd,shell=True,stdin=PIPE,out,err,encoding='utf-8')
   必须设置shell为真否则cmd为完整路径才能找到
   多个管道设置为PIPE不会冲突，可使用各自的Popen.stdout.read()
   检测是否结束 Popen.poll()!=None ，未结束返回None，结束了返回程序结束码，也是returncode
   读取：执行读操作后，绝对位置变为读取完毕的那个节点，seek(2)返回该节点到流末尾的长度，也即未读取的字节数，不会改变读取指针位置，可使用read(该长度)来全部取出而不用阻塞
4. HTML:
   calc(100% - 80px) 符号左右两边必须空格！
   dragEvent 会因为子元素不断触发！
"""
