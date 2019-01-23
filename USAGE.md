# Prepare
Create secret token from https://github.com/settings/tokens

```
brew install python3
brew install gist
echo MY_SECRET_TOKEN > ~/.gist
```

# KMB
Download latest apk from https://apk-dl.com/app-1933-kmblwb/com.kmb.app1933 to `download\kmb\kmb-<version>.zip`

```
python3 12_download_kmb.py
python3 13_process_kmb.py
sh 14_upload_kmb.sh GIST_ID
```

# NWFB

```
python3 22_download_nwfb.py
python3 23_process_nwfb.py
sh 24_upload_mwfbb.sh GIST_ID
```
