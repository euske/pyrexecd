#!/usr/bin/env python
import sys
import os
import os.path
import socket
import logging
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
CREATE_NO_WINDOW = 0x08000000


##  SysTrayApp
##
class SysTrayApp(object):

    WM_NOTIFY = None
    WNDCLASS = None
    CLASS_ATOM = None
    _instance = None

    @classmethod
    def initialize(klass):
        import win32con
        import win32gui
        WM_RESTART = win32gui.RegisterWindowMessage('TaskbarCreated')
        klass.WM_NOTIFY = win32con.WM_USER+1
        klass.WNDCLASS = win32gui.WNDCLASS()
        klass.WNDCLASS.hInstance = win32gui.GetModuleHandle(None)
        klass.WNDCLASS.lpszClassName = 'Py_'+klass.__name__
        klass.WNDCLASS.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        klass.WNDCLASS.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        klass.WNDCLASS.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        klass.WNDCLASS.hbrBackground = win32con.COLOR_WINDOW
        klass.WNDCLASS.lpfnWndProc = {
            WM_RESTART: klass._restart,
            klass.WM_NOTIFY: klass._notify,
            win32con.WM_DESTROY: klass._destroy,
            win32con.WM_COMMAND: klass._command,
            win32con.WM_TIMER: klass._timer,
            }
        klass.CLASS_ATOM = win32gui.RegisterClass(klass.WNDCLASS)
        klass._instance = {}
        return

    @classmethod
    def _create(klass, hwnd, instance):
        import win32gui
        klass._instance[hwnd] = instance
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_ADD,
            (hwnd, 0,
             (win32gui.NIF_ICON | win32gui.NIF_MESSAGE),
             klass.WM_NOTIFY, klass.WNDCLASS.hIcon))
        instance.open()
        return

    @classmethod
    def _restart(klass, hwnd, msg, wparam, lparam):
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_ADD,
            (hwnd, 0,
             (win32gui.NIF_ICON | win32gui.NIF_MESSAGE),
             klass.WM_NOTIFY, klass.WNDCLASS.hIcon))
        self = klass._instance[hwnd]
        self.open()
        return
        
    @classmethod
    def _notify(klass, hwnd, msg, wparam, lparam):
        import win32con
        import win32gui
        self = klass._instance[hwnd]
        if lparam == win32con.WM_LBUTTONDBLCLK:
            menu = self.get_popup()
            wid = win32gui.GetMenuDefaultItem(menu, 0, 0)
            win32gui.PostMessage(hwnd, win32con.WM_COMMAND, wid, 0)
        elif lparam == win32con.WM_RBUTTONUP:
            menu = self.get_popup()
            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(hwnd)
            win32gui.TrackPopupMenu(
                menu, win32con.TPM_LEFTALIGN,
                pos[0], pos[1], 0, hwnd, None)
            win32gui.PostMessage(hwnd, win32con.WM_NULL, 0, 0)
        elif lparam == win32con.WM_LBUTTONUP:
            pass
        return True

    @classmethod
    def _destroy(klass, hwnd, msg, wparam, lparam):
        import win32gui
        del klass._instance[hwnd]
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (hwnd, 0))
        win32gui.PostQuitMessage(0)
        return

    @classmethod
    def _command(klass, hwnd, msg, wparam, lparam):
        import win32gui
        wid = win32gui.LOWORD(wparam)
        self = klass._instance[hwnd]
        self.choose(wid)
        return

    @classmethod
    def _timer(klass, hwnd, msg, wparam, lparam):
        self = klass._instance[hwnd]
        self.update()
        return

    def __init__(self, name):
        import win32con
        import win32gui
        self.logger = logging.getLogger(name)
        self._hwnd = win32gui.CreateWindow(
            self.CLASS_ATOM, name,
            (win32con.WS_OVERLAPPED | win32con.WS_SYSMENU),
            0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0,
            self.WNDCLASS.hInstance, None)
        self._create(self._hwnd, self)
        self.logger.info('create: name=%r' % name)
        return

    def open(self):
        self.logger.info('open')
        return

    def run(self, timer=0):
        import ctypes
        import win32gui
        self.logger.info('run: timer=%r' % timer)
        if timer:
            ctypes.windll.User32.SetTimer(self._hwnd, 1, timer, None)
        win32gui.UpdateWindow(self._hwnd)
        win32gui.PumpMessages()
        return

    def close(self):
        import win32gui
        self.logger.info('close')
        win32gui.DestroyWindow(self._hwnd)
        return

    def set_icon(self, icon):
        import win32gui
        self.logger.info('set_icon: %r' % icon)
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_MODIFY,
            (self._hwnd, 0, win32gui.NIF_ICON,
             0, icon))
        return

    def set_text(self, text):
        import win32gui
        self.logger.info('set_text: %r' % text)
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_MODIFY,
            (self._hwnd, 0, win32gui.NIF_TIP,
             0, 0, text))
        return
        
    def show_balloon(self, title, text, timeout=1):
        import win32gui
        self.logger.info('show_balloon: %r, %r' % (title, text))
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_MODIFY,
            (self._hwnd, 0, win32gui.NIF_INFO,
             0, 0, '', text, timeout, title, win32gui.NIIF_INFO))
        return

    IDI_QUIT = 100
    
    def get_popup(self):
        import win32gui
        import win32gui_struct
        menu = win32gui.CreatePopupMenu()
        (item, _) = win32gui_struct.PackMENUITEMINFO(text=u'Quit', wID=self.IDI_QUIT)
        win32gui.InsertMenuItem(menu, 0, 1, item)
        win32gui.SetMenuDefaultItem(menu, 0, self.IDI_QUIT)
        (item, _) = win32gui_struct.PackMENUITEMINFO(text=u'Test', wID=123)
        win32gui.InsertMenuItem(menu, 0, 1, item)
        return menu

    def update(self):
        print 'update'
        return

    def choose(self, wid):
        self.logger.info('choose: wid=%r' % wid)
        if wid == self.IDI_QUIT:
            self.close()
        return


def netstring(x):
    return '%d:%s,' % (len(x), x)

class NetstringParser(object):
    
    def __init__(self):
        self.data = ''
        self.length = 0
        self._parse = self._parse_len
        return
        
    def feed(self, s):
        i = 0
        while i < len(s):
            i = self._parse(s, i)
        return
        
    def _parse_len(self, s, i):
        while i < len(s):
            c = s[i]
            if c < '0' or '9' < c:
                self._parse = self._parse_sep
                break
            self.length *= 10
            self.length += ord(c)-48
            i += 1
        return i
        
    def _parse_sep(self, s, i):
        if s[i] != ':': raise SyntaxError(i)
        self._parse = self._parse_data
        return i+1
        
    def _parse_data(self, s, i):
        n = max(self.length, len(s)-i)
        self.data += s[i:i+n]
        self.length -= n
        if self.length == 0:
            self._parse = self._parse_end
        return i+n
        
    def _parse_end(self, s, i):
        if s[i] != ',': raise SyntaxError(i)
        self._parse = None
        return i+1


##  PyRexec
##
class PyRexec(SysTrayApp):

    @classmethod
    def initialize(klass):
        import win32con
        import win32gui
        SysTrayApp.initialize()
        klass.ICON_IDLE = win32gui.LoadImage(
            0, 'PyRexec.ico',
            win32con.IMAGE_ICON,
            win32con.LR_DEFAULTSIZE, win32con.LR_DEFAULTSIZE,
            win32con.LR_LOADFROMFILE)
        klass.ICON_BUSY = win32gui.LoadImage(
            0, 'PyRexecConnected.ico',
            win32con.IMAGE_ICON,
            win32con.LR_DEFAULTSIZE, win32con.LR_DEFAULTSIZE,
            win32con.LR_LOADFROMFILE)
        return

    def __init__(self, sock, name='PyRexec', **kwargs):
        SysTrayApp.__init__(self, name)
        self.kwargs = kwargs
        (addr, port) = sock.getsockname()
        self.set_text(u'Listening: %s:%r...' % (addr, port))
        self._sock = sock
        self._servers = []
        return

    def update(self):
        for server in self._servers[:]:
            try:
                server.update()
            except server.Exit:
                server.close()
                self._servers.remove(server)
                self.show_balloon(u'Disconnected', repr(server))
                if not self._servers:
                    self.set_icon(self.ICON_IDLE)
        try:
            (conn, peer) = self._sock.accept()
        except socket.timeout:
            return
        conn.settimeout(0.01)
        self.logger.info('connected: addr=%r, port=%r' % peer)
        server = self.Server(conn, peer, **self.kwargs)
        self._servers.append(server)
        self.set_icon(self.ICON_BUSY)
        self.show_balloon(u'Connected', repr(server))
        return

    def open(self):
        SysTrayApp.open(self)
        self.set_icon(self.ICON_IDLE)
        return

    def close(self):
        while self._servers:
            server = self._servers.pop()
            server.close()
        SysTrayApp.close(self)
        return

    def get_popup(self):
        import win32gui
        import win32gui_struct
        menu = win32gui.CreatePopupMenu()
        (item, _) = win32gui_struct.PackMENUITEMINFO(text=u'Quit', wID=self.IDI_QUIT)
        win32gui.InsertMenuItem(menu, 0, 1, item)
        win32gui.SetMenuDefaultItem(menu, 0, self.IDI_QUIT)
        return menu

    def choose(self, wid):
        if wid == self.IDI_QUIT:
            self.close()
        return

    class Server(object):
        
        def __init__(self, conn, peer, homedir='.'):
            self.name = 'server-%s-%s' % peer
            self.logger = logging.getLogger(self.name)
            self.logger.info('open')
            self.conn = conn
            self.homedir = homedir
            self._buf = None
            self._proc = None
            return

        def __repr__(self):
            return ('<%s: %s>' % (self.__class__.__name__, self.name))

        def close(self):
            self.conn.send('bye.\r\n')
            self.conn.close()
            self.logger.info('close')
            return

        def prompt(self):
            self.conn.send('%s> ' % os.getcwd())
            return

        def update(self, size=4096):
            if self._proc is not None:
                if self._proc.is_alive(): return
                self._proc = None
            if self._buf is None:
                self.prompt()
                self._buf = ''
            try:
                s = self.conn.recv(size)
            except socket.timeout:
                return
            if not s: raise self.Exit
            for c in s:
                if c == '\n' and self._buf:
                    self.execute(self._buf)
                    self._buf = None
                else:
                    if self._buf is None:
                        self._buf = ''
                    self._buf += c
            return

        def execute(self, line):
            line = line.strip()
            if not line: return
            self.logger.info('execute: %r' % line)
            (cmd, _, args) = line.partition(' ')
            if cmd in ('exit', '\x04'): raise self.Exit
            if cmd == 'cd':
                if args:
                    d = args
                else:
                    d = self.homedir
                try:
                    os.chdir(d)
                except OSError:
                    self.conn.send('cannot chdir: %s\r\n' % d)
                return
            cmdline = 'cmd.exe /c '+line
            proc = Popen(cmdline, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                         creationflags=CREATE_NO_WINDOW)
            proc.stdin.close()
            self._proc = self.Forwarder(proc, proc.stdout, self.conn).start()
            return
    
        class Exit(Exception): pass

        class Forwarder(Thread):
            def __init__(self, proc, fp0, fp1, size=64):
                Thread.__init__(self)
                self.proc = proc
                self.size = size
                if hasattr(fp0, 'recv'):
                    self._read = fp0.recv
                else:
                    self._read = fp0.read
                if hasattr(fp1, 'send'):
                    self._write = fp1.send
                else:
                    self._write = fp1.write
                return
            def __repr__(self):
                return ('<%s: proc=%r>' % (self.__class__.__name__, self.proc))
            def run(self):
                while 1:
                    data = self._read(self.size)
                    if not data: break
                    self._write(data)
                #print 'terminate', self
                return

# main
def main(argv):
    import getopt
    def usage():
        print ('usage: %s [-d] [-f] [-l logfile] [-h homedir] [-r remotedir]'
               ' [-p port] [addr [cmd ...]]' % argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dfl:h:r:p:')
    except getopt.GetoptError:
        return usage()
    name = 'PyRexec'
    loglevel = logging.INFO
    logfile = None
    port = 8000
    addr = '0.0.0.0'
    force = False
    homedir = os.environ.get('HOME', '.')
    remotedir = os.environ.get('USERPROFILE', '.')
    altsep = '\\'
    for (k, v) in opts:
        if k == '-f': force = True
        elif k == '-d': loglevel = logging.DEBUG
        elif k == '-l': logfile = v
        elif k == '-p': port = int(v)
        elif k == '-h': homedir = v
        elif k == '-r': remotedir = v
    if args:
        addr = args.pop(0)
    logging.basicConfig(level=loglevel, filename=logfile)
    if args:
        logging.info('Connecting: %s:%s...' % (addr, port))
        path = os.getcwd()        
        path = os.path.relpath(path, homedir)
        path = remotedir+altsep+path.replace(os.path.sep, altsep)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr, port))
        sock.send('cd %s\r\n' % path)
        sock.send(' '.join(args)+'\r\n')
        sock.send('exit\r\n')
        while 1:
            data = sock.recv(4096)
            if not data: break
            sys.stdout.write(data)
        sock.close()
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if force:
            try:
                reuseaddr = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuseaddr | 1)
            except socket.error:
                pass
        sock.bind((addr, port))
        sock.settimeout(0.01)
        PyRexec.initialize()
        app = PyRexec(sock, name=name, homedir=remotedir)
        app.run(timer=50)
    return
if __name__ == '__main__': sys.exit(main(sys.argv))
