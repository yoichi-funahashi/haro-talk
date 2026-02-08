import asyncio
import io
import pygame
from edge_tts import Communicate

# --- 内部的な非同期処理（ここはライブラリの仕様上必要） ---
async def _generate_audio(text, voice):
    communicate = Communicate(text, voice)
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])
    audio_buffer.seek(0)
    return audio_buffer

# --- 同期的に呼び出せるラッパー関数 ---
def speak(text, voice="ja-JP-NanamiNeural"):
    """非同期処理を隠蔽して、普通の関数として呼び出せるようにする"""
    # asyncio.run() で非同期の世界を一時的に起動して結果を待つ
    buffer = asyncio.run(_generate_audio(text, voice))
    
    # pygameの再生（ここは元々同期処理）
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(buffer)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10) # CPU負荷を抑えつつ待機
    finally:
        pygame.mixer.quit()
        buffer.close()

# --- メイン処理（asyncなし！） ---
def main():
    print("音声生成を開始します...")
    
    # 普通の関数として呼び出し
    speak("こんにちは。これは、非同期処理を隠して同期的に実行するテストです。")
    
    print("再生が終了しました。")

if __name__ == "__main__":
    main()