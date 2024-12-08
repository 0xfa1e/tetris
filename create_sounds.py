import wave
import numpy as np
import os

def create_wav_file(filename, duration=0.1, frequencies=None, volume=0.5, fade_in=0.01, fade_out=0.01):
    """
    创建更复杂的WAV音频文件
    :param filename: 输出文件名
    :param duration: 音频持续时间（秒）
    :param frequencies: 频率列表或单个频率
    :param volume: 音量（0-1）
    :param fade_in: 淡入时间（秒）
    :param fade_out: 淡出时间（秒）
    """
    # 音频参数
    sample_rate = 44100  # 标准采样率
    samples = np.arange(int(duration * sample_rate)) / sample_rate
    
    # 处理频率
    if frequencies is None:
        frequencies = [440]  # 默认频率
    elif not isinstance(frequencies, list):
        frequencies = [frequencies]
    
    # 生成复合波形
    waveform = np.zeros_like(samples, dtype=np.float32)
    for freq in frequencies:
        # 使用正弦波和方波的混合
        sine_wave = np.sin(2 * np.pi * freq * samples)
        square_wave = np.sign(sine_wave)
        waveform += 0.7 * sine_wave + 0.3 * square_wave
    
    # 归一化
    waveform = waveform / np.max(np.abs(waveform))
    
    # 应用音量
    waveform *= volume
    
    # 淡入淡出效果
    fade_in_samples = int(fade_in * sample_rate)
    fade_out_samples = int(fade_out * sample_rate)
    
    # 淡入
    if fade_in_samples > 0:
        fade_in_curve = np.linspace(0, 1, fade_in_samples)
        waveform[:fade_in_samples] *= fade_in_curve
    
    # 淡出
    if fade_out_samples > 0:
        fade_out_curve = np.linspace(1, 0, fade_out_samples)
        waveform[-fade_out_samples:] *= fade_out_curve
    
    # 转换为16位整数
    waveform = waveform * 32767
    waveform = waveform.astype(np.int16)
    
    # 创建WAV文件
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16位
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(waveform.tobytes())

# 创建音效目录
os.makedirs('/Users/mac/CascadeProjects/tetris/assets/sounds', exist_ok=True)

# 创建清除方块音效（更丰富的音效）
create_wav_file('/Users/mac/CascadeProjects/tetris/assets/sounds/clear_sound.wav', 
                duration=0.3, 
                frequencies=[800, 1000, 1200],  # 多重频率创造丰富音色
                volume=0.4, 
                fade_in=0.05, 
                fade_out=0.1)

# 创建游戏结束音效（更悲伤、更柔和的音效）
create_wav_file('/Users/mac/CascadeProjects/tetris/assets/sounds/game_over_sound.wav', 
                duration=1.0, 
                frequencies=[200, 180, 160],  # 下降的音调
                volume=0.5, 
                fade_in=0.1, 
                fade_out=0.3)

# 创建背景音乐（更复杂的音乐结构）
def create_background_music(filename):
    sample_rate = 44100
    duration = 10  # 10秒背景音乐
    
    # 音乐和弦和音阶
    chord_progressions = [
        [261.63, 329.63, 392.00],  # C和弦
        [293.66, 369.99, 440.00],  # D和弦
        [329.63, 415.30, 493.88],  # E和弦
    ]
    
    # 生成音乐
    samples = np.arange(int(duration * sample_rate)) / sample_rate
    waveform = np.zeros_like(samples, dtype=np.float32)
    
    # 每个和弦持续2秒
    for i, chord in enumerate(chord_progressions * 5):
        start = i * 2 * sample_rate
        end = start + 2 * sample_rate
        
        if end > len(samples):
            break
        
        # 为每个和弦创建复合音
        chord_wave = np.zeros_like(samples[start:end], dtype=np.float32)
        for freq in chord:
            # 正弦波和方波混合
            sine_wave = np.sin(2 * np.pi * freq * samples[start:end])
            square_wave = np.sign(sine_wave)
            chord_wave += 0.6 * sine_wave + 0.4 * square_wave
        
        # 应用包络
        envelope = np.sin(np.linspace(0, np.pi, len(chord_wave)))
        chord_wave *= envelope
        
        waveform[start:end] += chord_wave
    
    # 归一化和音量调整
    waveform = waveform / np.max(np.abs(waveform))
    waveform = waveform * 0.3 * 32767
    waveform = waveform.astype(np.int16)
    
    # 创建WAV文件
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16位
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(waveform.tobytes())

create_background_music('/Users/mac/CascadeProjects/tetris/assets/sounds/background_music.mp3')

print("音效文件创建完成！")
