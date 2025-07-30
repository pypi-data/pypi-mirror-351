#!/usr/bin/env python3
import requests as req
import argparse as arg
from urllib.parse import urlparse
import os
import sys

bold='\033[1m'
yellow='\033[93m'
blue='\033[96m'
red="\033[31m"
orange="\033[38;5;208m"
green = "\033[32m"
rescolor='\033[0m'

logo = f'''{green}
 ███████╗██╗  ██╗       █████╗ ██╗   ██╗██████╗ ██╗████████╗
 ██╔════╝██║  ██║      ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝
 ███████╗███████║█████╗███████║██║   ██║██║  ██║██║   ██║   
 ╚════██║██╔══██║╚════╝██╔══██║██║   ██║██║  ██║██║   ██║   
 ███████║██║  ██║      ██║  ██║╚██████╔╝██████╔╝██║   ██║   
 ╚══════╝╚═╝  ╚═╝      ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   {rescolor}
 Invisiber                       Security Headers Audit Tool
'''

missing = 0
urltarget=""
outputf=""

def colors():
    global bold,yellow,blue,red,orange,green,rescolor
    bold=''
    yellow=''
    blue=''
    red=''
    orange=''
    green = ''
    rescolor=''

def flag():
    info=arg.ArgumentParser("",description="Security Headers Audit Tool")
    info.add_argument('-u','--url',type=str,help='Input URL to Scan')
    info.add_argument('-s','--silent',action='store_true',help='Silent Output')
    info.add_argument('-nc','--nocolor',action='store_true',help='No Color')
    info.add_argument('-o','--output',nargs="?",const="",default=None,help="Output file (default: sh-example.com)")
    info.add_argument('-i','--info',action='store_true',help='Information')
    return info.parse_args()

def process(listHeader, response):
    global outputf
    global missing
    global urltarget
    implemented = []
    missing_list = []

    if outputf != None:
        if os.path.exists(outputf):
            os.remove(outputf)

    for header, info in listHeader.items():
        if header in response.headers:
            implemented.append((header, info))
        elif info['required']:
            missing += 1
            missing_list.append((header, info))

    print(f"\n{bold}[INFO] Implemented Headers:{rescolor}")
    for header, info in implemented:
        print(f"{bold}{blue}[+]{rescolor}{bold} {header}{rescolor} - {info['description']}")
        if outputf != None:
            with open(outputf , 'a') as o:
                o.write(f"{bold}{blue}[+]{rescolor}{bold} {header}{rescolor} - {info['description']}\n")
        
    if missing > 0:
        print(f"\n{bold}[INFO] Missing Headers:{rescolor}")
    for header, info in missing_list:
        print(f"{red}{bold}[-]{rescolor}{bold} {info['level']} - {header} is missing {rescolor}- {info['tnr']}")
        print(f"    Recommendation : {info['recommendation']}")
        if outputf != None:
            with open(outputf, 'a') as o:
                o.write(f"{red}{bold}[MISSING]{rescolor}{bold} {info['level']} - {header}{rescolor}- {info['tnr']}\n")


def showInfo(listHeader):
    print(f""" {bold}[INFO] ——— {rescolor}Right now, the headers included in this tool are 
 limited to the ones listed below. This tool is currently in beta, 
 which means new features will be added and bugs will be fixed in 
 future updates. Feel free to share any feedback, suggestions, or 
 comments directly on my YouTube channel: {bold}@invisiber{rescolor}!
 """)

    for header, info in listHeader.items():
        print(f"{bold}[~] {header} - {info['level']} {red}{bold}{'- REQUIRED' if info['required'] == True else ''}{rescolor}")
        print(f"{bold}[?]{rescolor} {info['description']}")
        if info['required'] == True:
            print(f"{bold}[!]{rescolor} {info['tnr']}")
        print(f"{bold}[=]{rescolor} {info['recommendation']} \n")
    exit()


def main():
    try:
        global outputf
        global urltarget    

        args=flag()
        urltarget=args.url
        outputf=args.output
        
        if outputf == "":
            outputf = f"sh-{urlparse(urltarget).netloc}"
        if args.nocolor:
            colors()
        if not args.silent:
            print(logo)    
    

        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        }    

        listHeader = {
            "Content-Security-Policy": {
                "level": f"{orange}HIGH{rescolor}",
                "description": "CSP helps prevent XSS by specifying which dynamic resources are allowed to load.",
                "recommendation": "Set CSP with strict rules like 'default-src 'self'; script-src 'self''",
                "required": True,
                "tnr": "Without CSP, the application is more vulnerable to XSS attacks."
            },
            "Strict-Transport-Security": {
                "level": f"{orange}HIGH{rescolor}",
                "description": "HSTS enforces secure (HTTPS) connections to the server.",
                "recommendation": "Use 'Strict-Transport-Security: max-age=63072000; includeSubDomains; preload'",
                "required": True,
                "tnr": "Without HSTS, attackers can downgrade connections to HTTP (MITM)."
            },
            "X-Frame-Options": {
                "level": f"{yellow}MEDIUM{rescolor}",
                "description": "Protects against clickjacking by controlling whether the site can be framed.",
                "recommendation": "Use 'DENY' or 'SAMEORIGIN' to block framing.",
                "required": True,
                "tnr": "Missing this may lead to clickjacking attacks."
            },
            "Referrer-Policy": {
                "level": f"{yellow}MEDIUM{rescolor}",
                "description": "Controls how much referrer information is sent with requests.",
                "recommendation": "Use 'strict-origin-when-cross-origin' for better privacy.",
                "required": True,
                "tnr": "Sensitive URLs may be leaked in Referer headers."
            },
            "Permissions-Policy": {
                "level": f"{green}LOW{rescolor}",
                "description": "Controls which features can be used in the browser (e.g., geolocation, camera).",
                "recommendation": "Define only required features like 'geolocation=()'",
                "required": True,
                "tnr": "Missing this allows use of unnecessary browser features."
            },
            "X-Content-Type-Options": {
                "level": f"{orange}HIGH{rescolor}",
                "description": "Prevents MIME-type sniffing.",
                "recommendation": "Always use 'nosniff'.",
                "required": True,
                "tnr": "Without this, browsers may interpret files as a different MIME type."
            },
            "Cross-Origin-Resource-Policy": {
                "level": f"{green}LOW{rescolor}",
                "description": "Isolates resources to same-site or same-origin for cross-origin protection.",
                "recommendation": "Use 'same-origin' where possible.",
                "required": False
            },
            "Cross-Origin-Opener-Policy": {
                "level": f"{green}LOW{rescolor}",
                "description": "Isolates browsing context group to prevent side-channel attacks.",
                "recommendation": "Use 'same-origin'.",
                "required": False
            },
            "Cross-Origin-Embedder-Policy": {
                "level": f"{green}LOW{rescolor}",
                "description": "Ensures resources are loaded securely from trusted origins.",
                "recommendation": "Use 'require-corp'.",
                "required": False
            },
            "Access-Control-Allow-Origin": {
                "level": f"{blue}INFORMATION{rescolor}",
                "description": "CORS header that indicates allowed origins.",
                "recommendation": "Restrict to trusted domains, avoid wildcard '*'.",
                "required": False
            },
            "Expect-CT": {
                "level": f"{red}DEPRECATED{rescolor}",
                "description": "Was used to enforce Certificate Transparency.",
                "recommendation": "Consider removing, as it's deprecated.",
                "required": False
            },
            "X-Permitted-Cross-Domain-Policies": {
                "level": f"{blue}INFORMATION{rescolor}",
                "description": "Limits Adobe Flash or PDF from accessing data across domains.",
                "recommendation": "Set to 'none' unless specifically needed.",
                "required": False
            },
            "X-XSS-Protection": {
                "level": f"{red}DEPRECATED{rescolor}",
                "description": "Old anti-XSS header, deprecated in modern browsers.",
                "recommendation": "Consider removing, Rely on CSP instead.",
                "required": False
            },
            "Access-Control-Allow-Credentials": {
                "level": f"{yellow}MEDIUM{rescolor}",
                "description": "browser can send credentials (like cookies) in cross-origin requests.",
                "recommendation": "Use only when necessary and with a specific Access-Control-Allow-Origin.",
                "required": False
            }
        }    

        if args.info:
            showInfo(listHeader)
        print(f"[INFO] Target scan: {urltarget}")
        try:
            response = req.get(args.url, headers=headers, timeout=5)
        except req.exceptions.RequestException as e:
            print(f"[-] {args.url} is not reachable ({e})")
            exit()    

        process(listHeader,response)
        
        if missing == 1:
            print(f"{bold}[INFO] Rating: {6-missing}/6 {green}[A]{rescolor}")
        elif missing == 2:
            print(f"{bold}[INFO] Rating: {6-missing}/6 {green}[B]{rescolor}")
        elif missing == 3:
            print(f"{bold}[INFO] Rating: {6-missing}/6 {yellow}[C]{rescolor}")
        elif missing == 4:
            print(f"{bold}[INFO] Rating: {6-missing}/6 {yellow}[D]{rescolor}")
        elif missing == 5:
            print(f"{bold}[INFO] Rating: {6-missing}/6 {red}[E]{rescolor}")
        elif missing == 6:
            print(f"{bold}[INFO] Rating: {6-missing}/6 {red}[F]{rescolor}")
        else:
            print(f"{bold}[INFO] Rating: {6-missing}/6 {green}[Excellent!]{rescolor}")
        
    except KeyboardInterrupt:
        print(f"\n{red}{bold}[!] {rescolor}{bold}Process stopped by user{rescolor}")
        sys.exit(0)

if __name__ == "__main__":
    main()
