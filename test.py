import gdown

file_id = '1krFy7cKUTzUhBP-pWrnbIEDhZTNVscB0'
destination = 'cv1.pdf'
gdown.download(f'https://drive.google.com/uc?id={file_id}', destination, quiet=False)
