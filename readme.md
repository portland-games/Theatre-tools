A little knowledge of python and how to install pip and uv is required.

Video tools requires a 3.10 python version

uv venv --python 3.10 .venv

## Troubleshooting

### Installing pip manually in a virtual environment
If you encounter issues with `pip` in your virtual environment, you can manually install or repair it using the following steps:

1. **Activate the Virtual Environment**:
   ```pwsh
   .venv\Scripts\activate
   ```

2. **Download the `get-pip.py` Script**:
   ```pwsh
   Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
   ```

3. **Run the Script**:
   ```pwsh
   python get-pip.py
   ```

This will install or repair `pip` in your virtual environment. Once completed, you can use `pip` to install dependencies as usual:

```pwsh
pip install -r requirements.txt
```

### VLC update cache

"C:\Program Files\VideoLAN\VLC\vlc-cache-gen.exe" "C:\Program Files\VideoLAN\VLC\plugins"