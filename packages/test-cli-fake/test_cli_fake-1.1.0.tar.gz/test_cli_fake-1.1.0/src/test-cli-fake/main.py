import sys
import subprocess

def run():
    print("⚠️ Faux git intercepté : ", sys.argv)

    # Simuler relai vers le vrai git
    subprocess.run(["/usr/bin/git"] + sys.argv[1:])
