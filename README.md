# Synthetic-Exfiltration-Simulator (SEF)

## syntheticExfil.py
This script performs a file transfer from a %USERPROFILE%\Documents\upload or %USERPROFILE%\OneDrive\Documents\upload to a specifief host target. Protocols supported are FTP, FTPS, SFTP, WebDav and MEGA. The --include option can be used to specify the name of a file containing file extensions (one per line). If specified only files of these types will be copied. 

Usage:

syntheticExfill.py -h



syntheticExfil.py --host <hostname> --target <targetname> -l <username> -p <password> --protocol <protocolname> --include includeFileName (optional) -v

if specified the include file will be read and only files with the specified file extensions will be copied. Example file include.txt provided.

For example:

syntheteExfil.py --target targetName -l username -p assword --protocol ftp

will copy all files in %USERPROFILE%/Documents to the host with name targetname using protocol FTP. Authentication using the supplied username and password.


## SEFHarness.py
This script takes as input testCaseFile.csv. For each entry in the file a data exfiltration simulation will be peformed. Output will be displayed at the terminal and also writted to SEFHarnessOutput.csv

For example, if testCaseFile.CSV is:

  tool,	protocol,	target,	user,	password,	source,	include
  sef,	sftp,	ubuntuTarget,	bob,	bobpassword, include.txt
  scp, sftp, ubuntuTarget,bob, bobpassword, include.txt


then running SEFHarness.py will execute sytheticExfil.py using protocol SFTP, filtering applied using include.txt followed by WinSCP also (in this example) using SFTP to copy the same files to the same destination. Various performance metrics are displayed on screen and captured to file SEFOutput.csv.

supported values for tool are: 
1. sef (synthetic exfiltration simulator, sytheticexfil.py) as provided here, scp (winscp),
2. winscp
3. freefilesync
4. restic
5. rclone

If run with the parameter -r, SEFHarness will attempt to run script reset.sh on the target host. This script could be used to reset (delete) files between test cases. This script is not provided.

For FreeFileSync batch files will need to be created using FreeFileSync and saved as <protocol>batchRun.ffs_batch.ffs_batch. Where <protocol> is one of ftp, ftps or sftp.
