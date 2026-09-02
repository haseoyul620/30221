import numpy as np
import librosa

# 기타 6개 줄의 표준 조율(E Standard) MIDI 번호 (6번줄 -> 1번줄)
# E2(40), A2(45), D3(50), G3(55), B3(59), E4(64)
GUITAR_STRINGS = [40, 45, 50, 55, 59, 64]
MAX_FRETS = 21

def midi_to_tab_position(midi_note):
    """
    MIDI 노트 번호를 바탕으로 가장 연주하기 좋은 기타 줄(String)과 프렛(Fret)을 추천하는 함수
    """
    candidates = []
    
    for string_idx, open_note in enumerate(GUITAR_STRINGS):
        fret = midi_note - open_note
        if 0 <= fret <= MAX_FRETS:
            candidates.append((string_idx + 1, fret))  # 줄 번호 (1~6번줄), 프렛 번호
            
    if not candidates:
        return None  # 기타 음역대를 벗어난 경우

    # 가중치 알고리즘: 가급적 낮은 프렛(1~12프렛) 및 가운데 줄을 선호하도록 정렬
    candidates.sort(key=lambda pos: (pos[1], abs(pos[0] - 3)))
    return candidates[0]  # 가장 적합한 (string, fret) 반환

def transcribe_audio_to_tab(audio_path):
    """
    음원 파일을 읽어 오디오 분석 후 TAB 데이터 리스트로 변환
    """
    # 1. 오디오 로드 및 모노 변환
    y, sr = librosa.load(audio_path, sr=22050)
    
    # 2. 피치 추정 (YIN 또는 PYIN 알고리즘 사용)
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, 
        fmin=librosa.note_to_hz('E2'),  # 기타 최저음
        fmax=librosa.note_to_hz('E6'),  # 기타 최고음 부근
        sr=sr
    )
    
    times = librosa.times_like(f0, sr=sr)
    
    tab_sequence = []
    last_midi = None
    
    # 3. 프레임별 피치 추출 및 MIDI/TAB 변환
    for t, freq in zip(times, f0):
        if np.isnan(freq) or freq <= 0:
            last_midi = None
            continue
            
        # Hz -> MIDI 번호 변환
        midi_note = int(round(librosa.hz_to_midi(freq)))
        
        # 노트가 변경되었을 때만 이벤트 등록 (간단한 Onset filtering)
        if midi_note != last_midi:
            tab_pos = midi_to_tab_position(midi_note)
            if tab_pos:
                string_num, fret_num = tab_pos
                tab_sequence.append({
                    "time": round(float(t), 2),
                    "midi": midi_note,
                    "note_name": librosa.midi_to_note(midi_note),
                    "string": string_num,  # 1번줄 ~ 6번줄
                    "fret": fret_num       # 0프렛 ~ 21프렛
                })
            last_midi = midi_note
            
    return tab_sequence

# 사용 예시
# tab_data = transcribe_audio_to_tab("sample_guitar.wav")
# print(tab_data)
