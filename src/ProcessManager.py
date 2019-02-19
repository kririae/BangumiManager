import psutil
import ctypes, sys

def is_admin():
  try:
    return ctypes.windll.shell32.IsUserAnAdmin()
  except:
    return False

class ProcessManager:
  def __init__(self):
    if not is_admin():
      ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:
      for i in psutil.pids():
        print(psutil.Process(i).cwd())
def main():
  p = ProcessManager()

if __name__ == '__main__':
  main()