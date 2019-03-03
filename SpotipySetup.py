import os

print("Installing packages.")

try:
    os.system("pip3 install spotipy\n"
              "pip3 install --upgrade google-api-python-client oauth2client\n"
              "pip3 install matplotlib\n")
except:
    os.system("pip install spotipy\n"
              "pip install --upgrade google-api-python-client oauth2client\n"
              "pip install matplotlib\n")

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
