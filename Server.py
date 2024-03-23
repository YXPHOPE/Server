VER = '1.1.9' # 必须是3个整数由2个点隔开
PWD = '123456'
from requests import get, post  # 其实可以用socket，但我不想弄SSL
from os import getcwd, system, rename, remove, path, chdir, makedirs, scandir, _exit, execlp
import wave
from traceback import format_exc as fexc
from ssl import wrap_socket
import struct
from io import BytesIO
from signal import signal,SIGTERM,SIGINT
from PIL import ImageGrab
from base64 import b64encode
from hashlib import sha1  # 建立websocket时握手需要
from re import sub
from subprocess import Popen, PIPE, DEVNULL
from urllib.parse import unquote
from shutil import rmtree
from mimetypes import guess_type
from socket import socket, AF_INET, AF_INET6, SOCK_STREAM, gethostname, gethostbyname
from json import loads, dumps  # json解析和封装
from threading import Thread  # 多线程
from sys import argv  # 命令行参数
from typing import Dict
from time import strftime, time, localtime, sleep  # 格式化的时间
from platform import system as getOS
Win = getOS() == 'Windows'

# 以下为windows用，linux不行
if Win:
    system("color")  # Windows CMD 颜色刷新
    from win32api import GetConsoleTitle,SetConsoleCtrlHandler
    from win32gui import FindWindow, ShowWindow, GetCursorInfo
    from win32com.client import Dispatch # windows组件
    TM = FindWindow(0, GetConsoleTitle())
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(2)
    windll.kernel32.SetThreadExecutionState(0x80000001)
    from pynput import mouse, keyboard
    from pyaudio import PyAudio
    Mouse = mouse.Controller()
    Key = keyboard.Controller()
# 任务：历史记录（js）
# 播放器播放列表，连续播放（js）
ST = 0
Lim = 300*1024*1024

def showTM() -> None:
    if Win:
        global ST
        ST = 0 if ST == 9 else 9
        ShowWindow(TM, ST)


Hosts = {}
Magic = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11" # for socket
# GetCursorInfo()[1]: CSS.cursor
CS = {65539:'default', 0:'none', 65563:'help', 65567:'pointer', 65561:'progress', 65543:'wait', 49743883:'cell', 65545:'crosshair', 65541:'text', 303762077:'vertical-text', 29429383:'alias', 31919477:'copy', 65557:'move', 65559:'no-drop', 14093987:'grab', 41092819:'grabbing', 65553:'e-resize', 65555:'n-resize', 65551:'ne-resize', 65549:'nw-resize', 9241657:'col-resize', 41684679:'row-resize', 52956727:'zoom-in', 90771627:'zoom-out'}
Diskdir = {'folder': [], 'file': [], 'dir': ''}
Buffer = 1024
Sub = 0
Local = __file__.replace('\\','/')  # 相对路径地址
Local = Local[:Local.rfind('/')]
if Win:Local = Local.lower()
Share = None  # 共享地址(不用密码)
rmtIMG = BytesIO()
SL = 0
B = [1, 256, 256**2, 256**3, 256**4, 256**5, 256**6, 256**7]
Server = None
Servers = None
conn_pool = []  # 连接池
ip_pool = {}  # ip 池 限制同一ip连接数不超过16个，以及记录密码错误
Pipes = []  # 子程序池
M3U8 = []
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
ERR = '\033[1;31mError\033[0m  '
CTjson = {"Content-Type": "application/json; charset=utf-8"}


class Cfg:
    def __init__(self) -> None:
        self.nopwd = False
        self.log = True
        self.auto_sleep = False
        self.auto_update = True
        self.port = int(80)
        self.ip = '0.0.0.0'
        self.address = (self.ip, self.port)
        self.addr = '%s:%s'%(self.ip,self.port)
        # :: 只有在socket(AF_INET6, SOCK_STREAM)绑定IPv6地址时有效，表示IPv6回环地址，且支持IPv4访问
        # 127.0.0.1 环回地址，域名localhost默认指向它，只能在本机访问
        # 0.0.0.0   监听所有本地IP地址的该端口，访问本机IP即可访问
        self.pwd = PWD
        self.PWD = ''
        self.share = ''
        self.tokens = {}  # str:float
        self.ver = VER
        self.version = 0
        self.p()
        self.up_url = 'https://gitee.com/yxphope/server/raw/main/'
        self.host = 'http://172.25.75.95/:host'
        self.last = 0
        self.updated = False

    def load(self) -> None:
        try:
            with open('config', 'rb') as f:
                bs = bytearray(f.read())
                if len(bs) == 0:
                    self.save()
                else:
                    for i in range(len(bs)):
                        bs[i] = bs[i] ^ 0x66
                    if bs[:6] == b'config' and bs[-3:] == b'end':
                        self.nopwd = bs[6] != 0
                        self.log = bs[7] != 0
                        self.auto_sleep = bs[8] != 0
                        self.auto_update = bs[9] != 0
                        self.port = struct.unpack('<h', bs[10:12])[0]
                        lt = struct.unpack('<i', bs[12:16])[0]
                        l = [i.decode('utf-8')
                             for i in bs[16:16+lt].split(b'\0')]
                        self.ip = l[0]
                        self.pwd = l[1]
                        self.p()
                        self.share = l[2]
                        l = 20+lt
                        li = struct.unpack('<i', bs[16+lt:l])[0]
                        for i in range(li):
                            j = struct.unpack('<h', bs[l:l+2])[0]
                            l += 2+j
                            self.tokens[bs[l-j:l].decode('utf-8')] = struct.unpack('<f', bs[l:l+4])[0]
                            l += 4
        except Exception as e:
            print(ERR, str(e))
            if path.isfile('config'):
                if input('config file not exists, or is not consistent with the expected format, rewrite it?(y) ') == 'y':
                    self.save()
            else:
                self.save()

    def save(self) -> None:
        n = b'\0'
        y = b'\1'
        try:
            f = open('config', 'wb')
            bs = bytearray(struct.pack('6s????h', b'config', self.nopwd, self.log, self.auto_sleep, self.auto_update,self.port))
            bstr = self.pack(self.ip)+n + self.pack(self.pwd) + n + self.pack(self.share)+n
            bs += struct.pack('i', len(bstr))
            bs += bstr+struct.pack('i', len(self.tokens))
            for i in self.tokens:
                bs += struct.pack('h', len(i))+i.encode('utf-8') + struct.pack('f', self.tokens[i])
            bs += b'end'
            for i in range(len(bs)):
                bs[i] = bs[i] ^ 0x66
            f.write(bs)
            f.close()
        except Exception as e:
            print(ERR, str(e))

    def p(self) -> None:
        self.PWD = ''.join([chr(i ^ 0x66) for i in bytearray(self.pwd.encode('utf-8'))])
        l = [int(i) for i in VER.split('.')]
        self.version = l[0]*10000+l[1]*100+l[2]


    def pack(self, s='') -> bytes:
        return struct.pack(str(len(s))+'s', s.encode('utf-8'))

    def setpwd(self, b=True, p=''):
        self.nopwd = not b
        self.pwd = p
        self.p()
        self.save()

    def setport(self, p=80):
        if p > 0 and p < 65536:
            self.port = p
            self.save()

    def setshare(self, s):
        self.share = s
        self.save()

    def update(self, force=False):
        # 获取版本文件 如果有版本则下载所有文件并覆盖，然后socket解绑端口，运行新实例，退出本程序
        C.last = time()
        try:
            v = loads(get(self.up_url+'version.json').text)
            C.host = 'http://'+v['host']+'/:host'
            if force or v['version'] > self.version:
                i = self.auto_update
                if not i:
                    i = input('New version '+v['ver']+', Update?(y)').lower()=='y'
                if i:
                    log('NEW    %-21s %s --> %s' % ('Updating...', self.ver, v['ver']))
                    self.sync('', v['files'])
                    self.version = v['version']
                    log('Update Success')
                    self.updated = True
                    if len(conn_pool) <= 3:
                        log('Restarting...')
                        self.restart()
                        self.updated = False
            elif self.updated:
                if len(conn_pool) <= 3:
                    log('Restarting...')
                    self.restart()
                    self.updated = False
        except Exception as e:
            e = str(e)
            if "HTTPSConnection" in e: e = "Connection Failed"
            log('Update Failed: '+e)

    def sync(self, cur='', tar={}):
        for i in tar:
            if i == './':
                for j in tar[i]:
                    with open(j, 'wb') as f:
                        f.write(get(self.up_url+cur+j).content)
                        print(cur+j)
            else:
                nc = cur+i
                if not path.isdir(nc):
                    makedirs(nc)
                chdir(nc)
                self.sync(nc, tar[i])
                chdir('../')

    def restart(self):
        if Server: Server.close()
        if Servers: Servers.close()
        self.save()
        # execlp 使用当前path环境变量，将当前进程替换为另一个进程，pid不变
        # execlp 可行，system 不行，加start也不行，Popen也不行
        execlp('python','-u','"'+__file__+'"')
        _exit(0)

    def Task(self):
        if not Win: return
        # 连接计划任务服务
        try:
            scheduler = Dispatch('Schedule.Service')
            scheduler.Connect()
            Root = scheduler.GetFolder('\\')
            Task = scheduler.NewTask(0)
            # tk = Root.GetTask('Server') # 找不到会直接报错
            # tg = tk.Definition.Triggers[0]
            # general 信息
            Info = Task.RegistrationInfo
            Info.Description = 'Auto start python server at startup.'
            Info.Author = "python"
            Info.Date = '2021-10-31T10:00:00'
            Info.Version = VER
            Prcp = Task.Principal
            Prcp.GroupId = 'Administrators'
            Prcp.LogonType = 4 # 需要管理员权限
            Prcp.RunLevel = 1
            Prcp.Id = scheduler.ConnectedUser
            # Triggers 触发器 1:Once 2:Daily 6:on idle 8:at startup 9:At log on(8、9需要管理员权限) 更多可先在任务设置好，这里获取scheduler.GetFolder('\\').GetTask('Server').Definition.Triggers[0]
            Trigger = Task.Triggers.Create(9)
            Trigger.Delay = 'PT30S'
            Trigger.Enabled = True
            # Trigger.StartBoundary = '2024-02-23T20:37:00'
            # Trigger.Id = "DailyTriggerId"
            # Acition 执行的动作
            Action = Task.Actions.Create(0)
            Action.ID = 'TEST'
            Action.Path = 'python'
            # Action.Path = "netstat"
            Action.Arguments = '"'+__file__+'"'
            # Settings 设置
            Set = Task.Settings
            Set.Enabled = True
            Set.Hidden = True
            Set.RunOnlyIfIdle = False
            Set.DisallowStartIfOnBatteries = False
            Set.StopIfGoingOnBatteries = False
            Set.StartWhenAvailable = True
            Set.RestartCount = 3
            Set.RestartInterval = "PT5M"
            # 注册任务
            Root.RegisterTaskDefinition(
                "Server",
                Task, 
                6,   # update
                '',  # 用于注册任务的用户凭据
                '',  # 用于注册任务的userId的密码
                0  # 未指定登录方法。
            )
        except:
            log('Task   Failed to create or update, check administrator privilege')

def Help() -> str:
    s = ''
    if Server:
        hostname = gethostname()
        ip_address = gethostbyname(hostname)
        s += 'Listening ' + C.addr + '    IP: ' + ip_address+'\n'
        s += 'Runtime:\n'
        for i in HP_RUN:
            s += '  %8s  %s\n' % (i, HP_RUN[i])
    else:
        s += 'Argument:\n'
        for i in HP_ARG:
            s += '  %12s  %s\n' % (i, HP_ARG[i])
    return s


Head = {"Host": "opqnext.com", "Pragma": "no-cache", "Referer": "http://opqnext.com/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62}"}


class WAV:
    def __init__(self) -> None:
        self.file = BytesIO()
        self.audio = PyAudio()
        self.rec = self.audio.open(format=16, channels=1, rate=20000, input=True, frames_per_buffer=1024)

    def play(self, dat=b'') -> None:
        pf = BytesIO()
        pf.write(dat)
        pf.seek(0)  # 位置回到开头
        w = wave.open(pf, 'rb')
        p = self.audio.open(format=self.audio.get_format_from_width(w.getsampwidth()), channels=w.getnchannels(), rate=w.getframerate(), output=True)
        while len(data := w.readframes(1024)):
            p.write(data)
        p.close()
        pf.close()

    def record(self, cli):
        if not self.rec.is_active():
            self.rec.start_stream()
        pass


class IP:
    def __init__(self, addr) -> None:
        self.ip = addr
        self.qpwd = 0
        self.lastqpwd = 0
        self.conn = 0


def getLrcList(q, singer='') -> list:
    r = get('http://opqnext.com/search.html?q=' + q + ' '+singer, headers=Head).text
    s = r.find('<div class="media position-relative">')
    e = r.rfind('"content_right"')-74
    r = r[s:e].split('<hr>')
    res = []
    bol = 0
    # print(q,singer)
    o = {}
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


def getLrc(u) -> str:
    r = get(u, headers=Head).text
    s = r.find('lyric-textarea" rows="12">')+26
    e = r.find('</textarea>', s)
    return r[s:e]


def Lrc(p) -> list:
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

    def con(self, ip, client) -> None:
        log('Chat   %-21s connected' % (ip))
        self.clients[ip] = client

    def push(self, dat={'name': '', 'chat': ''}, ip='') -> None:
        dat['ip'] = ip
        dat['time'] = time()
        self.chat.append(dat)
        dat = packMes(dumps(dat))
        try:
            for k in self.clients:
                self.clients[k].socket.send(dat)
        except:
            pass

    def get(self, client, t=0) -> None:
        for i in self.chat:
            if i['time'] > t:
                client.socket.send(packMes(dumps(i)))

    def close(self, ip) -> None:
        log('Chat   %-21s disconnected' % (ip))
        self.clients.pop(ip)


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
        ip_pool[self.host].conn += 1

    def close(self, client=0) -> None:
        self.open = False
        self.socket.close()
        ip_pool[self.host].conn -= 1
        if self.file:
            if self.ws == ':tlcm':
                self.file.delete()
            else:
                self.file.close()
        if self.ws == ':chat':
            CHAT.close(self.address)
        if client:
            client.req_pool.remove(self)
        else:
            conn_pool.remove(self)
        log('Client %-21s disconnected' % (self.address))


def _exc(s,e:Exception):
    return
def _handle(client:Client):
    return
class MyServer:
    def __init__(self,ip='0.0.0.0', port=80, exc=_exc,handle=_handle, ssl=False) -> None:
        self.set(ip,port)
        self.running = False
        self.handle = handle
        self.ssl = ssl
        self.socket = socket(AF_INET, SOCK_STREAM)
        try:self.bind()
        except Exception as e:
            self.running = False
            exc(self,e)
    def bind(self)->None:
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(self.address)
        self.socket.listen(16)
        if self.ssl:
            self.wrap()
        th = Thread(target=self.run,daemon=True)
        th.start()
        self.running = True
    def set(self,ip,port):
        self.ip = ip
        self.port = port
        self.address = (ip,port)
        self.addr = '%s:%s'%(ip,port)

    def wrap(self,cert='mycert.pem')->None:
        self.socket = wrap_socket(self.socket,certfile=cert,keyfile='mycert.key',server_side=True)

    def run(self)->None:
        while True:
            try:
                # 阻塞，等待客户端连接，当 Server 关闭时，会抛出异常
                skt, address = self.socket.accept()
            except Exception as e:
                return
            # 加入连接池5
            if not ip_pool.get(address[0]):
                ip_pool[address[0]] = IP(address[0])
            client = Client(skt, address)
            conn_pool.append(client)
            # 同一IP连接数大于16则拒绝连接
            if ip_pool[address[0]].conn > 32:
                client.close()
                continue
            # 子线程：对每个连接的数据进行处理, args=tuple(arg1, arg2, ... , )
            thread = Thread(target=self.handle, args=(client,))
            # 设置成守护线程
            thread.setDaemon(True)
            thread.start()

    def close(self)->None:
        if self.running:
            self.socket.close()
            self.running = False


def Kill(proc, timeout, client) -> None:
    sleep(timeout)
    proc.kill()
    if proc.poll() == None:
        proc.kill()
    if client.open:
        client.socket.send(b'0\r\n\r\n')
        client.close()


def newkill(proc, client, timeout=5) -> None:
    thr = Thread(target=Kill, args=(proc, timeout, client,))
    thr.start()


def T() -> str:
    sec = str(time())
    sec = sec[sec.find('.'):][:4]
    return strftime('[%H:%M:%S'+sec+'] ')


def log(s) -> None:
    if C.log:
        print(T()+s+'\n', end='')


def parse_url(url='') -> object:
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


def parse_head(head) -> Dict[str,str]:
    header = {}
    if isinstance(head, bytes):
        head = head.decode()
    head = head.split('\r\n')
    head[0] = head[0].split()
    header['Method'] = head[0][0]
    header['path'] = unquote(head[0][1][1:])
    header['params'] = {}
    header['token'] = None
    if header['path'].rfind('?') > 0:
        header['path'], param = header['path'].split('?')
        param = param.split('&')
        ps = {}
        for i in param:
            k, v = i.split('=')
            ps[k] = v
        if ps.get('token'):
            header['token'] = ps['token']
        header['params'] = ps
    head.pop(0)
    head = [i.split(': ', 1) for i in head]
    i = 0
    while i < len(head):
        if head[i][0] != '':
            header[head[i][0]] = head[i][1]
        i += 1
    if not header['token']:
        header['token'] = header.get('Token')
    if header.get('Cookie'):
        h = header['Cookie'].split('; ')
        ps = {}
        for i in h:
            k, v = i.split('=',)
            ps[k] = v
        header['Cookie'] = ps
        if ps.get('token') and not header['token']:
            header['token'] = ps['token']
    return header


def pack(method='', url='', header={}, data='', res='') -> bytes:
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


def packMes(d:'str|bytes', text=True) -> bytes:
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


def getLen(m=b'') -> tuple:
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
        msglen = m[9]+m[8]*B[1]+m[7]*B[2]+m[6]*B[3] + m[5]*B[4]+m[4]*B[5]+m[3]*B[6]+m[2]*B[7]
        offset = 10
    return (msglen, offset)


def parseMes(m=b'', msglen=0, offset=0) -> bytes:
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


def checkPWD(p) -> bool:
    p = str(p)
    return C.nopwd or p == C.PWD or C.tokens.get(p, 0) > 0


def getFile(loc, head=False, rang='', pETag='', token='') -> bytes:
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
        loc = path.abspath(loc).replace('\\', '/')
        # 烦死了 获取到的abspath大小写变来变去，在调试模式和正常运行模式下不一样
        if Win: loc = loc.lower()
    else:
        if pETag == etgFavi:
            return faviSame
        else:
            return favi
    if path.isdir(loc):
        # 列出具体目录
        if not checkPWD(token):
            if Share and loc[:SL] == Share:
                pass
            else:
                return pwdErr
        log('%-7s%-21s %s' % ('GET', 'listDir', loc))
        # 返回目录信息
        try:
            filelist = scandir(loc)
            dir = {'folder': [], 'file': [], 'dir': loc.replace('\\', '/')}
            for i in filelist:
                try:
                    s = i.stat()
                except:
                    continue
                f = {'name': i.name, 'mtime': s.st_mtime, 'mts': strftime('%Y/%m/%d %H:%M', localtime(s.st_mtime))[2:]}
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
            resp = pack(res="HTTP/1.1 400 Bad Request", header=CTjson, data=dumps({"code": 400, "message": str(e), "trace": fexc()}))
    elif path.isfile(loc):
        # print(Local,loc,token)
        if loc.find(Local) != 0 and not checkPWD(token) and loc[:SL] != Share:
            return pwdErr
        size = path.getsize(loc)
        if size < 20971520:
            cache = False
        curMod = path.getmtime(loc)
        ETag = f'W/"{size}-{curMod}"'
        header = {'Content-Length': size, 'Content-Type': guess_type(loc)[0], 'Accept-Ranges': 'bytes', 'Last-Modified': strftime('%a, %d %b %Y %H:%M:%S GMT', localtime(curMod)), "Cache-Control": "public, max-age=31536000", 'ETag': ETag}
        if pETag == ETag:
            resp = pack(res='HTTP/1.1 304 Not Modified', header=header)
        elif head:
            resp = pack(res='HTTP/1.1 200 OK', header=header)
        else:
            if rang:  # 只接受一组值，多组的特喵的自己再请求一次
                rang = rang.split(', ')[0].split('-')
                se = [0,0,0]
                if rang[0] == '':
                    se[1] = int(rang[1])
                    se[0] = size-se[1]
                    se[1] = size
                elif rang[1] == '':
                    se[0] = int(rang[0])
                    maxs = se[0]+2097151  # 2Mb
                    se[1] = size-1 if (not cache) or size - se[0] < maxs else maxs
                else:
                    se[0] = int(rang[0])
                    se[1] = int(rang[1])
                se[2] = se[1]-se[0]+1
                if se[0] < 0 or se[1] < se[0] or se[1] > size:
                    resp = pack(res='HTTP/1.1 416 Range Not Satisfiable', data='')
            else:
                se = [0, size-1, size]
            if se[2] > Lim:
                se[1] = se[0]+Lim-1
                se[2] = Lim
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
                file.seek(se[0])
                c = file.read(se[2])
                header['Content-Length'] = se[2]
                header['Content-Range'] = f'bytes {se[0]}-{se[1]}/{size}'
                a = '206 Partial Content' if se[2] < size else '200 OK'
                resp = pack(res='HTTP/1.1 '+a, header=header, data=c)
                if not cache:
                    file.close()
            except Exception as e:
                resp = pack(res="HTTP/1.1 400 Bad Request", header=CTjson, data=dumps({"code": 400, "message": str(e), "trace": fexc()}))
                log('\033[1;33m%-7s\033[0m%-21s %s' % ('GET', (rg if rg else 'whole') +
                    ('  HEAD' if head else ''), loc+" Fail: "+str(e)))
    else:
        resp = pack(res='HTTP/1.1 404 Not Found', data='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>404</title></head><body style="padding: 5%;width: 500px;margin: 0 auto;"><div style="font: 700 32px/60px Sans-serif">404 Not Fount</div><div>Message: The page you are looking for is not found, click <a href="/">here</a> to go back to the homepage.</div><div style="padding: 10px 0;">Server: Python</div></body></html>')
        log('\033[1;33m%-7s\033[0m%-21s %s' % ('GET', (rg if rg else 'whole')+('  HEAD' if head else ''), loc+" Not Found"))
    return resp


def accept_client() -> None:
    # 线程1：监听连接
    while True:
        try:
            # 阻塞，等待客户端连接，当 Server 关闭时，会抛出异常
            skt, address = Server.accept()
        except:
            return
        # 加入连接池
        if not ip_pool.get(address[0]):
            ip_pool[address[0]] = IP(address[0])
        client = Client(skt, address)
        conn_pool.append(client)
        # 同一IP连接数大于16则拒绝连接
        if ip_pool[address[0]].conn > 16:
            client.close()
            continue
        # 子线程：对每个连接的数据进行处理, args=tuple(arg1, arg2, ... , )
        thread = Thread(target=message_handle, args=(client,))
        # 设置成守护线程
        thread.setDaemon(True)
        thread.start()


def message_handle(client:'Client') -> None:
    log('Client %-21s connected' % (client.address))
    # 循环等待请求
    msg = 'Unknown Error'
    trc = ''
    while client.open:
        resp = b''
        # 接收数据头head与数据主体data
        data = b''
        head = ''
        l = 0  # recv的总长度
        m = 0 if client.ws else -1   # 请求头与内容的分隔位置
        # 根据请求头的长度及时跳出循环，防阻塞
        buf = Buffer
        lenth = 0x7FFFFFFF
        wsl = (0, 0)
        try:
            while l <= lenth:
                rec = client.socket.recv(buf)
                if client.ws and wsl[1]==0:
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
                    if client.ws == ':remote' and Win:
                        # 收发数据还是以json格式 {name:,chat,time}
                        dat = dat.decode()
                        dat = loads(dat)
                        snd = 1
                        if dat.get('frame') != None:
                            img = ImageGrab.grab()
                            rmtIMG.seek(0)
                            img.save(rmtIMG, "JPEG")
                            rmtIMG.seek(0)
                            client.socket.send(packMes(rmtIMG.read(), 0))
                            snd = 0
                        elif dat.get('control'):
                            typ = dat.get('type')
                            xy = dat.get('xy')
                            key = dat.get('key')
                            if xy:
                                if xy[0]==None:xy=(0,0)
                                else:xy = (xy[0], xy[1])
                            if typ == 'move':
                                Mouse.position = xy
                            elif typ == 'click':
                                Mouse.position = xy
                                Mouse.click(mouse.Button.left)
                            elif typ == 'wheel':
                                Mouse.position = xy
                                dxy = dat.get('dxy', [0, 0])
                                Mouse.scroll(dxy[0], dxy[1])
                            elif typ == 'mousedown':
                                Mouse.position = xy
                                Mouse.press(mouse.Button.left)
                            elif typ == 'mouseup':
                                Mouse.position = xy
                                Mouse.release(mouse.Button.left)
                            elif typ == 'context':
                                Mouse.position = xy
                                Mouse.press(mouse.Button.right)
                                Mouse.release(mouse.Button.right)
                            elif typ == 'keydown':
                                if len(key) > 1:
                                    Key.press(keyboard.Key.__getitem__(key))
                                else:
                                    Key.press(key)
                            elif typ == 'keyup':
                                if len(key) > 1:
                                    Key.release(keyboard.Key.__getitem__(key))
                                else:
                                    Key.release(key)
                            elif typ == 'tap':
                                if len(key) > 1:
                                    Key.tap(keyboard.Key.__getitem__(key))
                                else:
                                    Key.tap(key)
                            if snd:
                                p = GetCursorInfo()[1]
                                client.socket.send(packMes(str(p)))
                    elif client.ws == ':chat':
                        dat = dat.decode()
                        dat = loads(dat)
                        if dat.get('time', -1) != -1:
                            CHAT.get(client, dat['time'])
                        elif dat.get('chat'):
                            CHAT.push(dat, client.address)
                    elif client.ws == ':tlcm':
                        print('rec')
                        f = client.file.read()
                        client.socket.send(packMes(struct.pack("h" * len(f), *f)))
                        # 传递录制帧
                        pass
                except Exception as e:
                    client.socket.send(packMes(dumps({'message': 'Error: '+fexc()})))
            else:
                client.socket.send(b'\x880')
                client.close()
                break
            continue
        head = parse_head(head)
        data = data[m+4:]
        if head['Method'].upper() == "GET":
            if head.get('Upgrade') == 'websocket':
                tp = head['path']
                if tp == ':chat' or ((tp == ':remote' or tp == ':tlcm') and checkPWD(head.get('token'))):
                    client.ws = tp
                    if tp == ':tlcm':
                        print(tp)
                        client.file = PvRecorder(frame_length=512)
                        client.file.start()
                        wave.open(WAV, 'wb')
                    elif tp == ':chat':
                        CHAT.con(client.address, client)
                    k = head.get('Sec-WebSocket-Key')
                    if not k: k = head.get('Sec-Websocket-Key')
                    key = k.encode()+Magic
                    key = b64encode(sha1(key).digest())
                    resp = b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nServer: WebSocket++/0.7.0\r\nSec-WebSocket-Accept: '+key+b'\r\n\r\n'
                else:
                    resp = UnknownErr
            elif head['path'] == ':getWH':
                wh = ImageGrab.grab().size
                resp = pack(res='HTTP/1.1 200 OK', data=f'{wh[0]},{wh[1]}')
            else:
                resp = getFile(head['path'], rang=head.get('Range',''), pETag=head.get('If-None-Match',''), token=head.get('token',''))
        elif head['Method'].upper() == "POST":
            pt = head['path']
            if pt == ':host':
                d = loads(data.decode())
                if not Hosts.get(d.get('ip')):
                    Hosts[d.get('ip')] = d.get('host')
                    log('Host   '+d.get('host'))
                resp = b"1"
            elif data[:15] != b'{"oprt":"token"' and pt[:SL] != Share and not checkPWD(head['token']):
                resp = pwdErr
            elif head.get('Content-Type') == 'plain/text':
                with open(pt, 'wb') as f:
                    f.write(data)
                resp = successResp
            elif pt and head.get('Content-Type') == 'application/octet-stream':
                # 加上Range: start-end,total
                lt = int(head.get('Content-Length',0))
                if lt>0: log("Post   File %-16s %s" % (lt, pt))
                start = int(head.get('Start', 0))
                f = None
                try:
                    if pt in Files:
                        f = Files[pt]['file']
                        Files[pt]['last'] = time()
                    else:
                        f = open(pt, 'wb')
                        Files[head['path']] = {'last': time(), 'file': f}
                        # 写入相应大小的空文件  全部被填充为\0 Nul  可以保留一个日志，记录已经上传的字节范围
                        f.seek(int(head.get('Size', 1))-1)
                        f.write(b'\0')
                    if start == -1:
                        sleep(2)
                        Files.pop(pt)
                        f.close()
                    else:
                        f.seek(start)
                        f.write(data)
                    resp = successResp
                except Exception as e:
                    msg = str(e)
                    trc = fexc()
            elif head.get('Content-Type') == "application/json" and len(data) > 0:
                try:
                    data = loads(data.decode())
                except:
                    msg = 'Invalid Data'
                    trc = fexc()
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
                                resp = b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n' + ('%x\r\n' % (len(output))
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
                                trc = fexc()
                        else:
                            log('\033[35mcmd\033[0m    no return             '+cmds)
                            try:
                                proc = Popen(cmd, shell=True, bufsize=0, stdout=PIPE, stderr=PIPE, encoding='utf-8')
                                Pipes.append(proc)
                                if 'N_m3u8DL-CLI' in cmd:
                                    M3U8.append(proc)
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
                                trc = fexc()
                    else:
                        msg = "Parameter Error (expect key of 'cmd')"
                        trc = fexc()
                elif oprt == 'token':
                    ip = ip_pool[client.host]
                    ip.lastqpwd = time()
                    ip.qpwd += 1
                    if ip.qpwd > 5:
                        msg = "Please wait for a moment and try again later."
                    elif data.get('pwd') and str(data['pwd']) == C.PWD:
                        tok = str(int(ip.lastqpwd * time() * (ip.lastqpwd % 9)/9))
                        C.tokens[tok] = ip.lastqpwd
                        resp = pack(res='HTTP/1.1 200 OK', header=CTjson, data=dumps({'code': 200, 'token': tok}))
                    else:
                        msg = "No pwd or the password is incorrect!"
                elif oprt == 'setpwd':
                    p = data.get('pre','')
                    n = data.get('ndpwd',False)
                    pwd = data.get('pwd','')
                    msg = ''
                    if len(pwd)<6 :
                        msg = 'The length of password must longer than 6!'
                    if p!=C.pwd:
                        msg = 'Wrong previous password.'
                    if msg=='':
                        C.setpwd(n,pwd)
                        resp = pack(res='HTTP/1.1 200 OK', header=CTjson, data=dumps({'code': 200, 'msg': 'Success'}))
                    
                elif oprt == 'update':
                    pass
                elif oprt == 'restart':
                    C.restart()
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
                        trc = fexc()
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
                            resp = getFile(p, token=head['token'])
                        else:
                            try:
                                res = Lrc(data['path'])
                                resp = pack(res='HTTP/1.1 200 OK', header=CTjson, data=dumps(res))
                            except Exception as e:
                                msg = str(e)
                                trc = fexc()
                    elif data.get('url'):
                        try:
                            l = getLrc(data['url'])
                            resp = pack(res='HTTP/1.1 200 OK', header={"Content-Type": "text/plain; charset=utf-8"}, data=l)
                        except Exception as e:
                            msg = str(e)
                            trc = fexc()
                    else:
                        msg = "Parameter Error (expect key of 'path')"
                else:
                    msg = 'Unsupport Operation'
            else:
                msg = 'Unsupport Content'
        elif head['Method'].upper() == "HEAD":
            resp = getFile(head['path'], head=True)
        elif head['Method'].upper() == 'OPTIONS':
            # 恶心巴拉的跨域CORS，恶心的预检请求preflight
            resp = b'HTTP/1.1 204 No Content\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: POST, GET, HEAD, OPTIONS\r\nAccess-Control-Allow-Headers: *\r\nAccess-Control-Expose-Headers: *\r\nAccess-Control-Max-Age: 31536000\r\nAllow: OPTIONS, GET, HEAD, POST\r\nServer: python\r\n\r\n'
        else:
            msg = 'Unsupport Method'
        try:
            if resp:
                client.socket.send(resp)
                if client.ws == ':chat':
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
                resp = pack(res="HTTP/1.1 400 Bad Request", header=CTjson, data=dumps({"code": 400, "message": msg, "trace": trc}))
                client.socket.send(resp)
        except:
            pass
        client.close()
    del client


def maintain() -> None:
    global Sub
    while True:
        if not Sub:
            host = gethostname()
            ip = gethostbyname(host)
            try:
                if ip not in C.host:
                    if post(C.host, data=dumps({"host": host, "ip": ip}), timeout=5).text == '1':
                        Sub = 1
            except:
                pass
        sleep(60)
        now = time()
        if now - C.last > 290:
            C.update()
        w = []
        for i in Files:
            if now-Files[i]['last'] > 60:
                Files[i]['file'].close()
                w.append(i)
        for i in w:
            # log('\033[33mFile   \033[0m%-21s \033[0m%s' % ('closed', i))
            Files.pop(i)
        w = []
        for i in ip_pool:
            p = ip_pool[i]
            if p.conn == 0 and now-p.lastqpwd > 120:
                w.append(i)
            elif p.qpwd and now-p.lastqpwd > 60:
                p.qpwd = 0
        for i in w:
            ip_pool.pop(i)
        w = []
        for i in C.tokens:
            if now-C.tokens[i] > 43200:
                w.append(i)
        for i in w:
            C.tokens.pop(i)


def Nm3u8():
    while True:
        sleep(10)
        i = len(M3U8)
        while i>0:
            i-=1
            try:
                r = M3U8[i].stdout.read()
            except:pass
            if M3U8[i].poll()!=None:
                s = M3U8[i].args
                s = s[s.find('--saveName "')+12:]
                s = s[:s.find('" -')]
                log('%-7s%-22s%s'%('m3u8', 'Task Done',s))
                M3U8.pop(i)

def Manage(cmd):
    f = ''
    p = 0
    global Files, Pipes, AutoCloseSub
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
        C.log = not C.log
        if C.log:
            return "log enabled."
        else:
            return "log disabled."
    elif cmd == '-f':
        s = ''
        for i in Files:
            s += str(i)+'\n'
        return s
    elif cmd == '-i':
        s = ''
        for i in ip_pool:
            s += ip_pool[i].ip+' '+str(ip_pool[i].conn)+'\n'
        return s
    elif cmd == '-a':
        s = ''
        for i in Pipes:
            if i.poll() != None:
                s += 'closed\n'
            try:
                out = i.stdout.read(i.stdout.seek(0, 2))
                if out[151] < ' ' or out[151] > 'z':
                    out[151] = ' '
                if out[152] < ' ' or out[152] > 'z':
                    out[152] = ' '
                l = len(out)
                if l < 150:
                    s += out
                else:
                    s += out[l-100:]
            except:
                pass
        return s
    elif cmd == '':
        if input("\033[1A\033[1;31mSure to exit? yes or no\033[0m ") == 'yes':
            return False
    elif cmd == '-p':
        l = len(Pipes)
        if l == 0:
            return 'No pipes'
        else:
            s = ''
            for i in range(l):
                s += str(i+1) + ' running' if Pipes[i].poll() != None else ' closed' + Pipes[i].args+'\n'
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
    elif cmd == '-sub':
        print(Hosts)
    elif len(cmd) > 2 and (cmd[0] == "/" or cmd[1] == ":"):
        global SL, Share
        if Win:
            cmd = cmd.replace('/', '\\')
        if not Share:
            Diskdir['folder'].append({})
        if path.isdir(cmd):
            cmd = cmd.replace('\\', '/')
            if cmd[-1] == '/':
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
    elif cmd == '-b':
        ShowWindow(TM, 0)
        return 'Background running...'
    elif cmd == '-s':
        C.auto_sleep = not C.auto_sleep
        if Win:
            if C.auto_sleep:
                windll.kernel32.SetThreadExecutionState(0x80000000)
                return 'Auto sleep when leave for certain period'
            else:
                windll.kernel32.SetThreadExecutionState(0x80000001)
                return 'Wake locked, computer will not sleep.'
        else:
            return 'This is not a windows system, sleep has not supported yet.'
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


def close(a=0,b=None) -> None:
    Server.close()
    C.save()
    log(f'Server {C.addr} closed.')
    if Win:
        windll.kernel32.SetThreadExecutionState(0x80000000)
    if Sub:
        # post('http://')
        pass
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
    with keyboard.GlobalHotKeys({'<ctrl>+<shift>+\\': showTM}) as h:
        h.join()


def thquit():
    with keyboard.GlobalHotKeys({'<ctrl>+<shift>+q': close}) as h:
        h.join()
def soc_exc(s,e:Exception):
    log(ERR + str(e))
    try:
        s.socket = socket(AF_INET, SOCK_STREAM)  # 创建 socket 对象
        p = input('Try another port number: ')
        if p.isdigit():
            p = int(p)
            C.address = (C.address[0], p)
            s.set(C.address[0],p)
            s.bind()
        else:
            raise ValueError('Port is not an invalid number([0-65535])!')
    except Exception as e1:
        log(ERR+str(e1))
        _exit(0)

def init():
    global Server, Servers, AutoCloseSub, Pipes, CHAT, SL
    print('\033[1;33mPython Server\033[0m         Version: '+VER)
    for i in range(len(argv)):
        if i == 0:
            continue
        if argv[i].isdigit():
            C.port = int(argv[i])
            C.address = (C.address[0], C.port)
        elif argv[i] == '-h' or argv[i] == '/?':
            print(Help())
            return
    C.load()
    C.update()
    C.Task()
    Server = MyServer('0.0.0.0',80,soc_exc,message_handle)
    if not Server.running:
        return
    C.addr = f'{C.address[0]}:{C.address[1]}'
    if Win:
        ShowWindow(TM, 0)
        # system('start http://localhost:'+str(C.address[1]))
    hostname = gethostname()
    ip_address = gethostbyname(hostname)
    print(strftime('Date: %Y/%m/%d %a'), ' IP:', ip_address)
    log('\033[33mServer \033[1;33m%-21s \033[0mstarted at \033[33m%s\033[0m' %
        (C.addr, Local))
    if Win: system('title Server '+C.addr+' '+Local)
    Thread(target=maintain, daemon=True).start()
    Thread(target=Nm3u8).start()
    sleep(1)
    if Win:
        Thread(target=thquit, daemon=True).start()
        Thread(target=thshow, daemon=True).start()
    # 线程3：终端输入
    try:
        while True:
            try:
                cmd = input("")
                s = Manage(cmd)
                if s == False:
                    break
                else:
                    print(s)
            except Exception as e:
                print(ERR, str(e))
    except KeyboardInterrupt:
        pass
    close()


i = __file__.rfind('\\')
if i < 0: i = __file__.rfind('/')
if i > 0: chdir(__file__[:i])
for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    disk = c+':'
    if path.isdir(disk):
        Diskdir['folder'].append({"name": disk, "mtime": "", "mts": ""})
C = Cfg()
if len(argv)>1 and argv[1]=='-r':C.restart()
CHAT = Chat()
if Win: SetConsoleCtrlHandler(close,True)
else: signal(SIGINT,close) # ctrl + C

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
