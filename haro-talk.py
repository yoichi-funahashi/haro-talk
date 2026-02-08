import io
import pygame
import os
import time
import threading
import asyncio

from dotenv import load_dotenv
from gpiozero import AngularServo
from google import genai
from google.genai.types import GenerateContentConfig
import speech_recognition as sr
from edge_tts import Communicate

# サーボモータ関連設定
SERVO_PIN = 18
MIN_DEGREE = -90
MAX_DEGREE = 90

# 音声認識設定
SAMPLE_RATE = 48000 # 44100/48000
mic_device_index = 0
mic_listen_timeout = None # long/None

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 100
recognizer.phrase_threshold = 0.3
recognizer.pause_threshold = 0.5
recognizer.non_speaking_duration = 0.5

# システムプロンプト（System Instruction）の定義
system_prompt = """
あなたの返答は音声としてスピーカーから出力されるので、読み上げられる文字で出力してください。
ハッシュタグなどは出力しないでください。
英文字はアルファベットで読み上げられてしまうのでカタカナで出力してください。
かっこが気の読み仮名についても出力しないでください。
クオータを節約するため、100字以内を目標にできるだけ簡潔に答えてください。
"""
# Geminiの設定
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MODEL_CODE='gemini-2.5-flash' # gemini-3-flash-preview/gemini-2.5-flash

client = genai.Client(api_key=GOOGLE_API_KEY)
chat = client.chats.create(
    model=MODEL_CODE,
    config=GenerateContentConfig(
        system_instruction=system_prompt
    )
)

def kuchipaku(stop_event):
    """
    口パク
    サーボモータを制御して口パクします
    
    :param stop_event: スレッド停止イベント
    """
    servo = AngularServo(SERVO_PIN, min_angle=MIN_DEGREE, max_angle=MAX_DEGREE, min_pulse_width=0.5/1000, max_pulse_width=2.4/1000, frame_width=1/50)
    servo.angle = 0
    time.sleep(0.1)
    # SG90を 0度 <-> +15度で角度を変える
    try:
        while not stop_event.is_set():
            servo.angle = 15
            time.sleep(0.1)
            servo.angle = 0
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("kuchipaku error")

def create_kuchipaku_thread():
    """
    口パクスレッド生成
    """
    stop_event = threading.Event()
    thead_hundle = threading.Thread(target=kuchipaku, args=(stop_event,))
    return thead_hundle, stop_event

async def _generate_audio(text, voice):
    """
    音声バイナリ生成
    
    :param text: 出力するテキスト
    :param voice: 音声
    """
    communicate = Communicate(text, voice)
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])
    audio_buffer.seek(0)
    return audio_buffer

def speak(text, voice="ja-JP-NanamiNeural"):
    """
    読み上げ処理
    
    :param text: 出力するテキスト
    :param voice: 音声
    """
    buffer = asyncio.run(_generate_audio(text, voice))
    
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(buffer)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        pygame.mixer.quit()
        buffer.close()

def do_chat():
    """
    メイン処理
    """
    print('=== 初期化中。。。 ===')
    with sr.Microphone(sample_rate=SAMPLE_RATE, device_index=mic_device_index) as source:
        while True:
            recognizer.adjust_for_ambient_noise(source)
            try:
                print('=== しゃべってください ===')
                audio_data  = recognizer.listen(source=source, timeout=mic_listen_timeout)
                print('=== 聞き取れました ===')
                sprec_text = recognizer.recognize_google(audio_data , language='ja-JP')
                print(sprec_text)
                if sprec_text == '終了':
                    return 0

                # Gemini呼び出し
                response = chat.send_message_stream(sprec_text)
                response_text = ''
                for chunk in response:
                    response_text += chunk.text
                print('=== Geminiからの回答 ===')
                print(response_text)

                # Gemini返答を読み上げ
                thead_hundle, stop_event = create_kuchipaku_thread()
                thead_hundle.start()
                speak(response_text)
                stop_event.set() # ループを停止させる
                thead_hundle.join() # スレッドが完全に終わるのを待つ

            except sr.UnknownValueError:
                print('=== エラー：UnknownValueError ===')
            except sr.RequestError:
                print('=== エラー：RequestError ===')
            except sr.WaitTimeoutError:
                print('=== エラー：WaitTimeoutError ===')

do_chat()
