# Code by Sergio1260

banner = [
"                          █████     ███████████ █████ █████       ██████████   ",
"                         ░░███     ░░███░░░░░░█░░███ ░░███       ░░███░░░░░█   ",
" █████ ███ █████  ██████  ░███████  ░███   █ ░  ░███  ░███        ░███  █ ░    ",
"░░███ ░███░░███  ███░░███ ░███░░███ ░███████    ░███  ░███        ░██████      ",
" ░███ ░███ ░███ ░███████  ░███ ░███ ░███░░░█    ░███  ░███        ░███░░█      ",
" ░░███████████  ░███░░░   ░███ ░███ ░███  ░     ░███  ░███      █ ░███ ░   █   ",
"  ░░████░████   ░░██████  ████████  █████       █████ ███████████ ██████████   ",
"   ░░░░ ░░░░     ░░░░░░  ░░░░░░░░  ░░░░░       ░░░░░ ░░░░░░░░░░░ ░░░░░░░░░░    ",
" lightweight web server to share files and play multimedia over the network    "]
banner = ("\n".join(banner))+"\n\n"


from subprocess import Popen, DEVNULL
from sys import path, argv
from os.path import exists, isdir
from os import sep
from time import sleep as delay
from re import compile as recompile

ipv4_pattern = recompile(r'^(\d{1,3}\.){3}\d{1,3}$')
ipv6_pattern = recompile(r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$')

def is_valid_ip(ip):
    if ipv4_pattern.match(ip):
        parts = ip.split('.')
        for part in parts:
            if int(part) < 0 or int(part) > 255:
                return False
        return True
    elif ipv6_pattern.match(ip): return True
    else: return False

def init():
    error_exit=False
    if len(argv)==1:
        file=path[0]+sep+"bin"+sep+"config.cfg"
    else: file=argv[1]
    try: file = open(file,"r")
    except: print("[ERROR]: CANT OPEN CONFIG FILE"); exit(1)
    dic={}
    for x in file:
        x=x.rstrip().lstrip()
        if not len(x)==0 and not x.startswith("#"):
            key=x[:x.find(":")]; value=x[x.find(":")+1:]
            value=value.strip(); dic[key.strip()]=value
    if not "port" in dic: dic["port"]="80"
    if not "listen" in dic: dic["listen"]="172.0.0.1"
    if not "show.folder.size" in dic: folder_size="false"
    if not "no.subtitle.cache" in dic: subtitle_cache="false"

    if not "folder" in dic:
        print("[CFG_FILE]: A FOLDER PATH IS NEEDED")
        error_exit = True
    root=dic["folder"]
    if not (exists(root) and isdir(root)):
        print("[CFG_FILE]: THE FOLDER PATH IS NOT VALID")
        error_exit = True
    port=dic["port"]; listen=dic["listen"]

    if "-" in port:
        st,end = port.split("-")
        try: st=int(st); end=int(end)
        except:
            print("[CFG_FILE]: PORTS MUST BE A NUMBER")
            error_exit = True
        if st>end: st,end = end,st
        ports=[str(x) for x in range(st,end+1)]
    else:
        ports=[]
        for x in port.split(","):
            try: ports.append(str(int(x.strip())))
            except:
                print("[CFG_FILE]: PORTS MUST BE A NUMBER")
                error_exit = True
    buffer=[]
    for x in listen.split(","):
        x=x.strip()
        if is_valid_ip(x):
            buffer.append(x)
        else:
            print("[CFG_FILE]: THE IP IS NOT VALID")
            error_exit = True
    listen=buffer; del buffer

    no_sub_cache=dic["no.subtitle.cache"].upper()
    if no_sub_cache=="TRUE": no_sub_cache=True
    elif no_sub_cache=="FALSE": no_sub_cache=False
    else:
        print("[CFG_FILE]: BAD VALUE IN no.subtitle.cache")
        error_exit = True

    folder_size=dic["show.folder.size"].upper()
    if folder_size=="TRUE": folder_size=True
    elif folder_size=="FALSE": folder_size=False
    else:
        print("[CFG_FILE]: BAD VALUE IN show.folder.size")
        error_exit = True

    if error_exit: exit(1)
    
    return ports, listen, root, folder_size, no_sub_cache


def main():
    print("")
    # Parse and get values
    ports,listen,root,folder_size,no_sub_cache = init()
    data = ["\033[32mListening on: \033[34m"+ip+\
            "\033[32m:\033[31m"+port+"\033[0m"\
            for ip in listen for port in ports]
    # Print info
    print(banner, end="")
    print("\n".join(data))
    print("\033[32mServing path: \033[34m"+root+"\033[0m\n")
    # Execute each process
    PyExec=path[0]+sep+"bin"+sep+"main.py"
    if sep==chr(92): python="python"
    else: python="python3"
    for ip in listen:
        for port in ports:
            args=[python,PyExec,"-b",ip,"-p",port,"-d",root]
            if folder_size: args.append("--dirsize")
            if no_sub_cache: args.append("--no-sub-cache")
            Popen(args,stdout=DEVNULL); delay(0.1)
    try: # wait forever
        while True: delay(1)
    except: exit()


if __name__=="__main__": main()
