import os

print("Installing packages.")

os.system("sudo pip3 install spotipy\n"
          "sudo pip3 install --upgrade google-api-python-client oauth2client\n"
          "sudo pip3 install matplotlib\n")
os.system("sudo pip install spotipy\n"
          "sudo pip install --upgrade google-api-python-client oauth2client\n"
          "sudo pip install matplotlib\n")

try:
    import spotipy
    import googleapiclient
    import matplotlib
    print("\n\n\nFinished.")
except:
    print("\n\n\nFailed to download the packages... ")
    print("Please run the following commands in the terminal: ")
    print("pip install spotipy")
    print("pip install --upgrade google-api-python-client oauth2client")
