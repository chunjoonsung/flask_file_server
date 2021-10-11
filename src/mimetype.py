MIME_TYPE = { 
    'css'  : 'text/css',
    'gif'  : 'image/gif',
    'htm'  : 'text/html',
    'html' : 'text/html',
    'ico'  : 'image/x-icon',
    'jpeg' : 'image/jpg', 
    'jpg'  : 'image/jpg', 
    'pdf'  : 'application/pdf', 
    'png'  : 'image/png', 
    'txt'  : 'text/plane', 
    #'7z'   : 'application/x-7z-compressed',
    #'zip'  : 'application/zip', 
    
}

def get_mime_type(filename):
    if '.' in filename:
        return MIME_TYPE.get(filename.rsplit('.', 1)[1])
    return None
