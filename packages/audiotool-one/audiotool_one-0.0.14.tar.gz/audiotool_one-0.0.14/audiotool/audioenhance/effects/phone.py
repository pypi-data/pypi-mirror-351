from typing import Optional, Union
import librosa
import numpy as np
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
from pydub.effects import normalize
import soundfile as sf
from scipy import signal


def add_phone_effect(audio: Union[AudioSegment, str], output_file: str):
    """
    给 AudioSegment 添加电话效果并保存

    :param audio: 输入的 AudioSegment 对象
    :param output_file: 输出文件路径
    """
    if isinstance(audio, str):
        audio = AudioSegment.from_wav(audio)
    # 1. 转换为单声道（如果不是的话）
    if audio.channels > 1:
        audio = audio.set_channels(1)

    # 2. 带通滤波器（模拟电话频率范围）
    audio = high_pass_filter(audio, 300)
    audio = low_pass_filter(audio, 3400)

    # 3. 降低音质（模拟电话压缩）
    audio = audio.compress_dynamic_range()

    # 4. 添加轻微失真
    audio = audio.overlay(
        audio.compress_dynamic_range(threshold=-20, ratio=5, attack=5, release=50)
    )

    # 5. 降低音量（模拟远距离通话）
    audio = audio - 6  # 降低 6dB

    # 6. 添加轻微噪音（模拟线路噪音）
    # 注意：这需要一个噪音样本文件，如果没有，可以跳过这一步
    try:
        noise = AudioSegment.from_wav("path_to_noise_sample.wav")
        noise = noise * (len(audio) // len(noise) + 1)  # 重复噪音样本以匹配音频长度
        noise = noise[: len(audio)]  # 裁剪到与音频相同长度
        noise = noise - 20  # 降低噪音音量
        audio = audio.overlay(noise)
    except FileNotFoundError:
        print("噪音样本文件未找到，跳过添加噪音步骤。")

    # 7. 重采样到典型的电话采样率（可选）
    audio = audio.set_frame_rate(8000)

    # 保存处理后的音频
    audio.export(output_file, format="wav")
    print(f"带电话效果的音频已保存到: {output_file}")


def dephone_effect(input_file, output_file, sample_rate=48000):
    """
    remove phone effect in audio.
    """

    audio = AudioSegment.from_file(input_file)

    if audio.frame_rate != sample_rate:
        audio = audio.set_frame_rate(sample_rate)

    # # 1. 轻微扩展频率范围
    # audio = high_pass_filter(audio, 100)  # 稍微降低高通滤波器的频率
    # audio = low_pass_filter(audio, 7000)  # 稍微提高低通滤波器的频率
    # 1. 扩展频率范围，但限制高频
    audio = high_pass_filter(audio, 80)  # 稍微降低高通滤波器的频率，恢复更多低频
    # audio = low_pass_filter(audio, 6000)  # 降低低通滤波器的频率，减少高频
    # audio = low_pass_filter(audio, 5000)  # 降低低通滤波器的频率，减少高频
    audio = low_pass_filter(audio, 4500)  # 降低低通滤波器的频率，减少高频
    # We need lower high pass filter, not need too much high freqs

    # 2. 增强中频（提高清晰度，但避免过多高频）
    enhanced_mid = high_pass_filter(low_pass_filter(audio, 3000), 800) - 6
    audio = audio.overlay(enhanced_mid)  # 将

    enhanced_low = (
        audio.low_pass_filter(300) + 3
    )  # 创建一个低频增强的版本，并稍微提高其音量
    audio = audio.overlay(enhanced_low)

    # 2. 轻微增强高频（提高清晰度） looks like we need avoid high freqs
    # enhanced = audio.high_pass_filter(1000) - 12  # 创建一个高频增强的版本，但降低其音量
    # audio = audio.overlay(enhanced)  # 将增强的高频与原始音频混合

    # 3. 轻微的动态范围调整
    audio = normalize(audio)  # 标准化音量
    # audio = audio.compress_dynamic_range(threshold=-15, ratio=1.5)  # 非常温和的压缩
    audio = audio.compress_dynamic_range(threshold=-20, ratio=1.8)  # 非常温和的压缩

    # 5. 再次应用低通滤波器以确保高频被抑制
    # audio = low_pass_filter(audio, 5500)
    # audio = low_pass_filter(audio, 4500)
    audio = low_pass_filter(audio, 4200)

    # 4. 最终音量标准化
    audio = normalize(audio)

    # 保存处理后的音频
    audio.export(output_file, format="wav")
    return output_file


def advanced_dephone_effect(input_file, output_file):
    """
    使用高级技术去除音频中的电话效果，尽量恢复原始声音的纯净度

    :param input_file: 输入音频文件路径
    :param output_file: 输出音频文件路径
    """
    # 使用 librosa 加载音频，这样我们可以进行更高级的处理
    y, sr = librosa.load(input_file, sr=None)

    # 1. 重采样到 48kHz（如果原始采样率不是48kHz）
    if sr != 48000:
        y = librosa.resample(y, orig_sr=sr, target_sr=48000)
        sr = 48000

    # 2. 轻微扩展频率范围
    y_highpassed = librosa.effects.preemphasis(y, coef=0.90)
    y_bandpassed = librosa.effects.preemphasis(y_highpassed, coef=-0.90)

    # 3. 应用预加重滤波器来增强高频
    y_preemphasized = librosa.effects.preemphasis(y_bandpassed, coef=0.90)

    # 4. 频谱减法降噪
    S = librosa.stft(y_preemphasized)
    S_mag, S_phase = librosa.magphase(S)
    noise_estimate = np.mean(S_mag[:, :10], axis=1, keepdims=True)
    S_mag_denoised = np.maximum(S_mag - noise_estimate, 1e-6)
    y_denoised = librosa.istft(S_mag_denoised * S_phase)

    # 5. 自适应均衡化
    S_eq = librosa.stft(y_denoised)
    S_eq_db = librosa.amplitude_to_db(np.abs(S_eq), ref=np.max)
    S_eq_smooth = librosa.decompose.nn_filter(
        S_eq_db, aggregate=np.median, metric="cosine", width=5
    )
    S_eq_residual = S_eq_db - S_eq_smooth
    S_eq_enhanced = S_eq_smooth + S_eq_residual * 1.2
    y_eq = librosa.istft(
        librosa.db_to_amplitude(S_eq_enhanced) * np.exp(1.0j * np.angle(S_eq))
    )

    # 6. 动态范围扩展
    percentile_low = np.percentile(y_eq, 5)
    percentile_high = np.percentile(y_eq, 95)
    y_expanded = np.interp(y_eq, (percentile_low, percentile_high), (-0.9, 0.9))

    # 7. 高频增强
    y_highfreq = librosa.effects.preemphasis(y_expanded, coef=0.2)

    # 8. 轻微的动态范围压缩（模拟 pydub 的压缩）
    def compress(x, threshold=0.3, ratio=0.6):
        mask = np.abs(x) > threshold
        x[mask] = np.sign(x[mask]) * (threshold + (np.abs(x[mask]) - threshold) * ratio)
        return x

    y_compressed = compress(y_highfreq)

    # 9. 音高校正（如果需要）
    # n_steps = -0.1 # 降低一个半音，可以根据需要调整
    # y_compressed = librosa.effects.pitch_shift(y_compressed, sr=sr, n_steps=n_steps)

    # 9. 最终音量标准化
    y_normalized = librosa.util.normalize(y_compressed)

    # 保存处理后的音频
    sf.write(output_file, y_normalized, sr)
    print(f"处理后的音频已保存到: {output_file}")

    return output_file
