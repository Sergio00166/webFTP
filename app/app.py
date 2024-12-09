#Code by Sergio00166

# BASIC WEB-file-sharing-server with a basic interface
# Allows you to share a folder across the LAN (READ-ONLY mode)

from functions import get_file_type,getclient
from flask import send_file,redirect,request
from actions import *
from secrets import token_hex
from threading import Thread

app,folder_size,root = init()
sroot = app.static_folder
app.secret_key = token_hex(16)
USERS,ACL = {},{}
thr = Thread(target=update_rules, args=(USERS,ACL,))
thr.daemon = True;  thr.start()


@app.route('/<path:path>', methods=['GET','POST'])
# For showing a directory, launching the custom media players
# or send in raw mode (or stream) files or send the dir as .tar
def explorer(path):
    client = getclient(request)
    try:
        # User login/logout stuff
        if "logout" in request.args: return logout(request)
        if "login" in request.args:  return login(request,USERS)
        # Paths must not end on slash
        if path.endswith("/"): path = path[:-1]
        # Check if we can access it
        req_path = path
        path = isornot(path,root)
        validate_acl(req_path,ACL,write=False)
        # Get the file type of the file
        file_type = get_file_type(path)
        # Check if the path is not a dir
        if not file_type=="directory":
            if request.path.endswith('/') and client!="json":
                return redirect(request.path[:-1])
            # If the text is plain text send it as plain text
            if file_type in ["text","source"]:
                return send_file(path,mimetype='text/plain')
            # If it have the raw arg or is requested
            # from a cli browser return the file
            elif "raw" in request.args or client!="normal":
                return send_file(path)
            # Custom player for each multimedia format
            elif file_type=="video":
                info = (request.method.lower()=="head")
                subs = request.args["subs"] if "subs" in request.args else ""
                return video(path,root,subs,file_type,info,ACL)  
            elif file_type=="audio": return audio(path,root,file_type,ACL)
            # Else send it and let flask autodetect the mime
            else: return send_file(path)
        # Return the directory explorer
        else:
            if not request.path.endswith('/') and client!="json":
                return redirect(request.path+'/')
            proto = request.headers.get('X-Forwarded-Proto', request.scheme)
            hostname = proto+"://"+request.host+"/"
            sort = request.args["sort"] if "sort" in request.args else ""
            if "tar" in request.args: return send_dir(path)
            return directory(path,root,folder_size,sort,client,hostname,ACL)
  
    except Exception as e: return error(e,client)


@app.route('/', methods=['GET','POST'])
# Here we show the root dir, serve the static files
# or send the root dir as .tar
def index():
    client = getclient(request)
    try:
        # User login/logout stuff
        if "logout" in request.args: return logout(request)
        if "login" in request.args:  return login(request,USERS)
        # Check if static page is requested
        if "static" in request.args:
            path = request.args["static"]
            return send_file( isornot(path,sroot) )
        # Else show the root directory
        proto = request.headers.get('X-Forwarded-Proto',request.scheme)
        hostname = proto+"://"+request.host+"/"
        path = isornot("/",root) # Check if we can access it
        sort = request.args["sort"] if "sort" in request.args else ""
        if "tar" in request.args: return send_dir(path)
        return directory(path,root,folder_size,sort,client,hostname,ACL)

    except Exception as e: return error(e,client)

