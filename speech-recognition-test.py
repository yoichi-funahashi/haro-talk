import speech_recognition as sr
import os
import time

# device_indexを調べる方法
# import speech_recognition as sr

# # 使用可能なすべてのマイクデバイスのリストを表示
# for index, name in enumerate(sr.Microphone.list_microphone_names()):
#     print("Microphone with name \"{0}\" found for Microphone(device_index={1})".format(name, index))

device_index = 0

SAMPLE_RATE = 44100 # 44100  # サンプリングレート
recognizer = sr.Recognizer()
# デフォルトだと True だが、音声が長めになりがちなので False にしている
recognizer.dynamic_energy_threshold = False
# minimum audio energy to consider for recording(300)
# 録音時に考慮すべき最小のオーディオエネルギー
recognizer.energy_threshold = 100
# minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops) (0.3)
# 話し声をフレーズとみなすまでの話し声の最小秒数 - この値未満の値は無視されます（クリック音やポップ音を除外するため）
recognizer.phrase_threshold = 0.3
# seconds of non-speaking audio before a phrase is considered complete (0.8)
# フレーズが完了したとみなされるまでの、話されていない音声の秒数
recognizer.pause_threshold = 0.5
# seconds of non-speaking audio to keep on both sides of the recording (0.5)
# 録音の両側に残しておく、話されていない音声の秒数
recognizer.non_speaking_duration = 0.5

def mike_to_textise():
    print('初期化中。。。')
    with sr.Microphone(sample_rate=SAMPLE_RATE, device_index=device_index) as source:
        while True:
            recognizer.adjust_for_ambient_noise(source)
            # while True:
            try:
                print('しゃべってください')
                audio_data  = recognizer.listen(source=source, timeout=5)
                print('聞き取れました')
                sprec_text = recognizer.recognize_google(audio_data , language='ja-JP')
                # os.system('cls')
                print(sprec_text)
                # print('----------------------')
                if sprec_text == '終了':
                    return 0
            except sr.UnknownValueError:
                print('エラー：UnknownValueError')
            except sr.RequestError:
                print('エラー：RequestError')
            except sr.WaitTimeoutError:
                print('エラー：WaitTimeoutError')
            # time.sleep(1)
                



mike_to_textise()

