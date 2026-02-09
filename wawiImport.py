from time import sleep
import subprocess


def GPTBestellImport():
    print("Auftragsimport Starting")
    sleep(5)
    result = subprocess.run(
        "\\\\192.168.31.10\\Orlando\\WWPROG\\Wawi.exe ARTIKELIMPOR 1 -IMPORT=995 -log=Auftragiimport_Log.txt")
    print("Auftragsimport Done")
    return result



def GPTAngebotImport():
    print("Auftragsimport Starting")
    sleep(5)
    result = subprocess.run(
        "\\\\192.168.31.10\\Orlando\\WWPROG\\Wawi.exe ARTIKELIMPOR 1 -IMPORT=994 -log=Auftragiimport_Log.txt")
    print("Auftragsimport Done")
    return result
