# PyRexecd

PyRexecd is a standalone SSH server for Windows.

![PyRexecd Screenshot](docs/pyrexecd.gif)

## Features:

  * Standalone Win32 app (not a service) that resides in the SysTray.
  * Single user / pubkey auth only.
  * Notifies incoming connections via popup.
  * Sends/Receives the clipboard text via stdin/stdout.

## Prerequisites:

  * Python 3 (or 2)
  * Paramiko (install via pip)
  * PyWin32 - http://sourceforge.net/projects/pywin32/
  * cx_Freeze (optional - if you want to build .exe)

## How to Setup:

  1. Run PyRexec.py. It creates an empty config directory
     (AppData\Roaming\PyRexecd) and opens it.
  1. Create a new ssh host key via OpenSSH and place it in the config dir.<br>
    `$ ssh-keygen -N '' -f ssh_host_rsa_key`
  1. Copy your public key into the config dir.<br>
    `> copy your\id_rsa.pub authorized_keys`

## Command Line Sytax:

    > pyrexecd.exe [-d] [-l logfile] [-s sshdir] [-L addr] [-p port]
                   [-u username] [-a authkeys] [-h homedir] [-c cmdexe]
		   hostkeys ...
		   
  * `-d` : Turns on Debug mode (verbose logging).
  * `-l logfile` : Log file path (default: `pyrexecd.log`).
  * `-s sshdir` : Config directory path. (default: `AppData\Roaming\PyRexecd`)
  * `-p port` : Specifies the listen port (default: `2200`). 
  * `-L a.b.c.d` : Specifies the listen address (default: `127.0.0.1`).
  * `-c cmdexe` : cmd.exe path. (default: `cmd.exe`)
  * `-u username` : Username.
  * `-a authkeys` : authorized_keys path. (default: `authorized_keys`)
  * `-h homedir` : Home directory path. (default: `%UserProfile%`)

## Special commands:

  Certain SSH command is recognized as special commands:

  * `@clipget` : Receives the clipboard text from Windows.<br>
    `$ ssh windows @clipget > clipboard.txt`
  * `@clipset` : Sends the clipboard text to Windows.<br>
    `$ echo foo | ssh windows @clipset`
  * `@open`, `@edit`, and `@print` : Windows shell operation.
    The target pathname should be given from stdin.<br>
    `$ echo C:\User\euske\foo.txt | ssh windows @edit`

## How to Build .exe (requires cx_Freeze):

    > python setup.py build
