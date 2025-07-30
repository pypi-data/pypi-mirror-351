import subprocess

def main():
    try:
        user_input = input()
        cmd = f'ssh -p 80 ubuntu@4.156.195.94 "python3 ~/p.py \\"{user_input}\\""'
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print("Error:", e)
