# Synthetic-Exfiltration-Simulator (SEF)

## syntheticExfil.py
This script performs a file transfer from a specified source to a given tagret using the requetsed protocol. Protocols supported FTP, FTPS, SFTP, WebDav and MEGA,

Usage:

syntheteExfil.py --host <hostname> --target <targetname> -l <username> -p <password> --protocol <protocolname> --include includeFileName (optional)

if specified the include file will be read and only files with the specified file extensions will be copied. Example include.txt provided.

For example:

syntheteExfil.py --target targetName -l username -p assword --protocol ftp

will copy all files in %USERPROFILE%/Documents to the host with name targetname using protocol FTP. Authentication using the supplied username and password.


SEFHarness.Py
This script takes as input testCaseFile.csv. For each entry in the file 
