# Define the file path (DBFS)
file_path = %LOCAL_PATH%."/%NAME%.csv"

# Write DataFrame to CSV file in DBFS
%SRC_NODE_NAME%.coalesce(1).write.csv(file_path, header=True)

# List the files to confirm creation
display(dbutils.fs.ls(%LOCAL_PATH%))

# FTP server credentials and connection details
ftp_host = '%HOST%'
ftp_user = '%USERNAME%'
ftp_pass = '%PASSWORD%'
ftp_dir = '%REMOTE_PATH%'

# Local path to the file (adjust based on your file's location)
local_file_path = '%LOCAL_PATH%/%NAME%.csv'

# Establish FTP connection
ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)
ftp.cwd(ftp_dir)

# Open the local file and upload it
with open(local_file_path, 'rb') as file:
    ftp.storbinary(f'STOR {os.path.basename(local_file_path)}', file)

# Close the FTP connection
ftp.quit()