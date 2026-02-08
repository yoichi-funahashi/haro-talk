# ハロとおしゃべり

プラモデルを改造したハロとおしゃべりします。  
音声認識した文字列をGeminiAPIに送り、応答を読み上げます。  
読み上げている間ハロの口をサーボモータでパクパクします。

## setup

### linux library
pythonライブラリに必要なライブラリをインストールします。
```bash
sudo apt install -y portaudio19-dev
sudo apt install -y flac
sudo apt install -y python3-rpi.gpio
```

### python venv
venvを作成します。GPIOを利用したいので、"--system-site-packages"オプションをつけてください。
```bash
python -m venv .venv  --system-site-packages
```

### python library
"requirements.txt"を使ってインストールしてください。
```bash
pip install -r requirements.txt
```

### .env
以下の内容で.envファイルを作成し、APIキーを設定してください。
```
GOOGLE_API_KEY=<Google AI Studio apikey>
```

## execute
"haro-talk.py"を実行してください。
```bash
source .venv/bin/activate
python haro-talk.py
```
