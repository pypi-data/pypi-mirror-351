import sys
import subprocess

def run():
    print("⚠️ Faux git intercepté : ", sys.argv)

    
    subprocess.run(["/usr/bin/git"] + sys.argv[1:])
