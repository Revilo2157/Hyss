import os

print("Installing packages.")
os.system("pip install spotipy\n"
          "pip install --upgrade google-api-python-client oauth2client\n")

try:
    import spotipy
    import googleapiclient
    print("\n\n\nFinished.")
except:
    print("\n\n\nFailed to download the packages... ")
    print("Please run the following commands in the terminal: ")
    print("pip install spotipy")
    print("pip install --upgrade google-api-python-client oauth2client")
