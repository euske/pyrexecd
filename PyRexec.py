#!/usr/bin/env python

# Prerequisites:
#   Python 2.7 (https://www.python.org/downloads/)
#   Python for Windows (http://sourceforge.net/projects/pywin32/)
#   PyCrypto (http://www.voidspace.org.uk/python/modules.shtml#pycrypto)
#   Python-ecdsa (https://pypi.python.org/pypi/ecdsa)
#   Paramiko (https://github.com/paramiko/paramiko)

# Usage:
#   python pyrexec.py ssh_host_rsa_key

import sys
import os
import os.path
import socket
import logging
import paramiko
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from paramiko.py3compat import decodebytes
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
            win32con.WM_CLOSE: klass._close,
            win32con.WM_DESTROY: klass._destroy,
            win32con.WM_COMMAND: klass._command,
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
    def _close(klass, hwnd, msg, wparam, lparam):
        import win32gui
        win32gui.DestroyWindow(hwnd)
        return

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
        import win32gui
        self.logger.info('open')
        win32gui.UpdateWindow(self._hwnd)
        return

    def run(self):
        import win32gui
        self.logger.info('run')
        win32gui.PumpMessages()
        return

    def idle(self):
        import win32gui
        return not win32gui.PumpWaitingMessages()

    def close(self):
        import win32con
        import win32gui
        self.logger.info('close')
        win32gui.PostMessage(self._hwnd, win32con.WM_CLOSE, 0, 0)
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

    def choose(self, wid):
        self.logger.info('choose: wid=%r' % wid)
        if wid == self.IDI_QUIT:
            self.close()
        return


##  PyRexecTrayApp
##
class PyRexecTrayApp(SysTrayApp):

    @classmethod
    def initialize(klass, basedir='.'):
        import win32con
        import win32gui
        SysTrayApp.initialize()
        klass.ICON_IDLE = win32gui.LoadImage(
            0, os.path.join(basedir, 'PyRexec.ico'),
            win32con.IMAGE_ICON,
            win32con.LR_DEFAULTSIZE, win32con.LR_DEFAULTSIZE,
            win32con.LR_LOADFROMFILE)
        klass.ICON_BUSY = win32gui.LoadImage(
            0, os.path.join(basedir, 'PyRexecConnected.ico'),
            win32con.IMAGE_ICON,
            win32con.LR_DEFAULTSIZE, win32con.LR_DEFAULTSIZE,
            win32con.LR_LOADFROMFILE)
        return

    def __init__(self, name='PyRexec'):
        SysTrayApp.__init__(self, name)
        return

    def set_busy(self, busy):
        if busy:
            self.set_icon(self.ICON_BUSY)
        else:
            self.set_icon(self.ICON_IDLE)
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


##  PyRexecSession
##
class PyRexecSession(paramiko.ServerInterface):

    class Exit(Exception): pass

    def __init__(self, peer, name, username, pubkeys, homedir, cmdline):
        self.peer = peer
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.username = username
        self.pubkeys = pubkeys
        self.homedir = homedir
        self.cmdline = cmdline
        self._chan = None
        self._proc = None
        self._tasks = None
        return

    def __repr__(self):
        return ('<%s: %s>' % (self.__class__.__name__, self.name))

    def get_peer(self):
        return '%s:%s' % self.peer

    def get_allowed_auths(self, username):
        if username == self.username:
            return 'publickey'
        return ''
    
    def check_auth_publickey(self, username, key):
        self.logger.debug('check_auth_publickey: %r' % username)
        if username == self.username:
            for k in self.pubkeys:
                if k == key: return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
    def check_channel_request(self, kind, chanid):
        self.logger.debug('check_channel_request: %r' % kind)
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_channel_shell_request(self, channel):
        self.logger.debug('check_channel_shell_request')
        self.open(channel)
        return True

    def open(self, chan):
        self.logger.info('open: %r' % chan)
        self._chan = chan
        self._chan.settimeout(0.05)
        self._proc = Popen(
            self.cmdline, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
            cwd=self.homedir, creationflags=CREATE_NO_WINDOW)
        self._tasks = (
            self.ChanForwarder(self, self._chan, self._proc.stdin),
            self.PipeForwarder(self, self._proc.stdout, self._chan),
        )
        for task in self._tasks:
            task.start()
        return
    
    def close(self):
        self.logger.info('close: %r' % self._chan)
        self._proc.terminate()
        status = self._proc.wait()
        self.logger.info('exit status: %r' % status)
        self._chan.send_exit_status(status)
        self._chan.close()
        return

    def is_closed(self):
        if self._tasks is None: return False
        for task in self._tasks:
            if not task.isAlive(): return True
        return False
    
    class ChanForwarder(Thread):
        def __init__(self, session, chan, pipe, size=64):
            Thread.__init__(self)
            self.session = session
            self.chan = chan
            self.pipe = pipe
            self.size = size
            return
        def run(self):
            while 1:
                try:
                    data = self.chan.recv(self.size)
                    if not data: break
                    self.pipe.write(data)
                except socket.timeout:
                    continue
                except (IOError, socket.error):
                    break
            self.session.logger.info('chan end')
            self.pipe.close()
            return
        
    class PipeForwarder(Thread):
        def __init__(self, session, pipe, chan, size=1):
            Thread.__init__(self)
            self.session = session
            self.pipe = pipe
            self.chan = chan
            self.size = size
            return
        def run(self):
            while 1:
                try:
                    data = self.pipe.read(self.size)
                    if not data: break
                    self.chan.send(data)
                except socket.timeout:
                    continue
                except (IOError, socket.error):
                    break
            self.session.logger.info('pipe end')
            self.pipe.close()
            return

# get_host_key
def get_host_key(path):
    if path.endswith('rsa_key'):
        f = paramiko.RSAKey
    elif path.endswith('dsa_key'):
        f = paramiko.DSSKey
    elif path.endswith('ecdsa_key'):
        f = paramiko.ECDSAKay
    else:
        raise ValueError(path)
    return f(filename=path)

# get_authorized_keys
def get_authorized_keys(path):
    keys = []
    fp = file(path)
    for line in fp:
        (t,_,data) = line.partition(' ')
        if t == 'ssh-rsa':
            f = paramiko.RSAKey
        elif t == 'ssh-dss':
            f = paramiko.DSSKey
        elif t.startswith('ecdsa-'):
            f = paramiko.ECDSAKey
        else:
            continue
        data = decodebytes(data)
        keys.append(f(data=data))
    fp.close()
    return keys

# run_server
def run_server(hostkeys, username, pubkeys, homedir, cmdline,
               addr='127.0.0.1', port=2222):
    logging.info('Hostkeys: %d' % len(hostkeys))
    logging.info('Username: %r (pubkeys:%d)' % (username, len(pubkeys)))
    logging.info('Listening: %s:%s...' % (addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        reuseaddr = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuseaddr | 1)
    except socket.error:
        pass
    sock.bind((addr, port))
    sock.listen(5)
    sock.settimeout(0.05)
    app = PyRexecTrayApp()
    app.set_text(u'Listening: %s:%r...' % (addr, port))
    app.set_busy(False)
    sessions = []
    while app.idle():
        for session in sessions[:]:
            if session.is_closed():
                session.close()
                sessions.remove(session)
                app.show_balloon(u'Disconnected', session.get_peer())
                if not sessions:
                    app.set_busy(False)
        try:
            (conn, peer) = sock.accept()
        except socket.timeout:
            continue
        conn.settimeout(0.05)
        logging.info('Connected: addr=%r, port=%r' % peer)
        t = paramiko.Transport(conn)
        t.load_server_moduli()
        for k in hostkeys:
            t.add_server_key(k)
        name = 'Session-%s-%s' % peer
        session = PyRexecSession(peer, name, username, pubkeys, homedir, cmdline)
        try:
            t.start_server(server=session)
            if t.accept(10):
                logging.info('Accepted')
                sessions.append(session)
                app.show_balloon(u'Connected', session.get_peer())
                app.set_busy(True)
            else:
                t.close()
        except EOFError:
            t.close()
    while sessions:
        session = sessions.pop()
        session.close()
    return

# main
def main(argv):
    import getopt
    def usage():
        print ('usage: %s [-d] [-l logfile] [-L addr] [-p port]'
               ' [-u username] [-a authkeys] [-h homedir] [-c cmdline]' % argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dl:L:p:u:a:h:c:')
    except getopt.GetoptError:
        return usage()
    loglevel = logging.INFO
    logfile = None
    port = 2222
    addr = '0.0.0.0'
    username = os.environ.get('USERNAME', 'unknown')
    homedir = os.environ.get('USERPROFILE', '.')
    pubkeys = get_authorized_keys('authorized_keys')
    cmdline = 'cmd /Q'
    for (k, v) in opts:
        if k == '-d': loglevel = logging.DEBUG
        elif k == '-l': logfile = v
        elif k == '-L': addr = v
        elif k == '-p': port = int(v)
        elif k == '-u': username = v
        elif k == '-a': pubkeys.extend(get_authorized_keys(v))
        elif k == '-h': homedir = v
        elif k == '-c': cmdline = v
    hostkeys = []
    for path in args:
        hostkeys.append(get_host_key(path))
    if not hostkeys:
        print 'no hostkey is found!'
        return 111
    logging.basicConfig(level=loglevel, filename=logfile, filemode='a')
    PyRexecTrayApp.initialize(basedir=os.path.dirname(argv[0]))
    run_server(hostkeys, username, pubkeys, homedir, cmdline,
               addr=addr, port=port)
    return
if __name__ == '__main__': sys.exit(main(sys.argv))
