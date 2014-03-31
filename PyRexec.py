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


##  PyRexecServer
##
class PyRexecServer(object):

    class Exit(Exception): pass

    def __init__(self, conn, peer, homedir='.'):
        self.name = 'Server-%s-%s' % peer
        self.logger = logging.getLogger(self.name)
        self.logger.info('open')
        self.conn = conn
        self.homedir = homedir
        self._buf = ''
        self._task = None
        return

    def __repr__(self):
        return ('<%s: %s>' % (self.__class__.__name__, self.name))

    def close(self):
        self.conn.close()
        self.logger.info('close')
        return

    def update(self, size=4096):
        if self._task is not None:
            if not self._task.isAlive(): raise self.Exit
            return
        try:
            s = self.conn.recv(size)
        except socket.timeout:
            return
        if not s: raise self.Exit
        try:
            i = s.index('\r\n')
        except ValueError:
            self._buf += s
            return
        self._buf += s[:i]
        try:
            proc = self.run_process(self._buf)
        except OSError, e:
            self.conn.send(str(e)+'\r\n')
            raise self.Exit
        self.InputForwarder(self.conn, proc.stdin, buf=s[i+1:]).start()
        self._task = self.OutputForwarder(proc.stdout, self.conn)
        self._task.start()
        return

    def run_process(self, cmdline):
        self.logger.info('run_process: %r, cwd=%r' % (cmdline, self.homedir))
        return Popen(cmdline, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                     cwd=self.homedir, creationflags=CREATE_NO_WINDOW)

    class InputForwarder(Thread):
        def __init__(self, sock, pipe, buf='', size=4096):
            Thread.__init__(self)
            self.sock = sock
            self.pipe = pipe
            self.buf = buf
            self.size = size
            return
        def run(self):
            self.pipe.write(self.buf)
            while 1:
                try:
                    data = self.sock.recv(self.size)
                    if not data: break
                    self.pipe.write(data)
                except socket.timeout:
                    continue
                except (IOError, socket.error):
                    break
            self.pipe.close()
            return

    class OutputForwarder(Thread):
        def __init__(self, pipe, sock, size=64):
            Thread.__init__(self)
            self.pipe = pipe
            self.sock = sock
            self.size = size
            return
        def run(self):
            while 1:
                try:
                    data = self.pipe.read(self.size)
                    if not data: break
                    self.sock.send(data)
                except (IOError, socket.error):
                    break
            return

# run_server
def run_server(addr='0.0.0.0', port=8000, homedir='.', force=False):
    logging.info('Listening: %s:%s...' % (addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if force:
        try:
            reuseaddr = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuseaddr | 1)
        except socket.error:
            pass
    sock.bind((addr, port))
    sock.listen(1)
    sock.settimeout(0.01)
    app = PyRexecTrayApp()
    app.set_text(u'Listening: %s:%r...' % (addr, port))
    app.set_busy(False)
    servers = []
    while app.idle():
        for server in servers[:]:
            try:
                server.update()
            except server.Exit:
                server.close()
                servers.remove(server)
                app.show_balloon(u'Disconnected', repr(server))
                if not servers:
                    app.set_busy(False)
        try:
            (conn, peer) = sock.accept()
        except socket.timeout:
            continue
        conn.settimeout(0.01)
        logging.info('Connected: addr=%r, port=%r' % peer)
        server = PyRexecServer(conn, peer, homedir=homedir)
        servers.append(server)
        app.set_busy(True)
        app.show_balloon(u'Connected', repr(server))
    while servers:
        server = servers.pop()
        server.close()
    return
        
# run_client
def run_client(cmdline, addr='127.0.0.1', port=8000):
    logging.info('Connecting: %s:%s...' % (addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((addr, port))
    logging.info('Sending: %r' % cmdline)
    sock.send(cmdline+'\r\n')
    while 1:
        data = sock.recv(4096)
        if not data: break
        sys.stdout.write(data)
    sock.close()
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
    loglevel = logging.INFO
    logfile = None
    port = 8000
    addr = '0.0.0.0'
    force = False
    homedir = os.environ.get('HOME', '.')
    remotedir = os.environ.get('USERPROFILE', '.')
    for (k, v) in opts:
        if k == '-d': loglevel = logging.DEBUG
        elif k == '-f': force = True
        elif k == '-l': logfile = v
        elif k == '-p': port = int(v)
        elif k == '-h': homedir = v
        elif k == '-r': remotedir = v
    if args:
        addr = args.pop(0)
    logging.basicConfig(level=loglevel, filename=logfile, filemode='a')
    if args:
        # Run at Unix.
        path = os.getcwd()
        path = os.path.relpath(path, homedir)
        path = path.replace(os.path.sep, '\\')
        cmdline = 'cmd /c "cd %s & %s"' % (path, ' '.join(args))
        run_client(cmdline, addr=addr, port=port)
    else:
        # Run at Windows.
        PyRexecTrayApp.initialize()
        run_server(addr=addr, port=port, homedir=remotedir, force=force)
    return
if __name__ == '__main__': sys.exit(main(sys.argv))
