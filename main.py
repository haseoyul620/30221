import re
import streamlit as st

# 기타 6개 줄별 기본 튜닝 기준 옥타브별 포지션 매핑 (표준 튜닝: E A D G B E)
# [줄 번호(1~6줄), 프렛 번호]
NOTE_MAP = {
    # 2옥타브 (극저음역대 - 6번줄/5번줄)
    "미2": (6, 0), "파2": (6, 1), "솔2": (6, 3), "라2": (5, 0), "시2": (5, 2),
    
    # 3옥타브 (저음역대)
    "도3": (5, 3), "레3": (5, 5), "미3": (4, 2), "파3": (4, 3), "솔3": (4, 5), "라3": (3, 2), "시3": (3, 4),
    
    # 4옥타브 (중음역대 - 기본값)
    "도4": (3, 5), "레4": (2, 3), "미4": (2, 5), "파4": (2, 6), "솔4": (1, 3), "라4": (1, 5), "시4": (1, 7),
    
    # 5옥타브 (고음 솔로)
    "도5": (1, 8), "레5": (1, 10), "미5": (1, 12), "파5": (1, 13), "솔5": (1, 15), "라5": (1, 17), "시5": (1, 19),
    
    # 단순 계이름 입력 시 기본 4옥타브 포지션으로 매핑
    "도": (3, 5), "레": (2, 3), "미": (2, 5), "파": (2, 6), "솔": (1, 3), "라": (1, 5), "시": (1, 7),
    
    # 샵(#) 포함 계이름
    "도#": (3, 6), "레#": (2, 4), "파#": (2, 7), "솔#": (1, 4), "라#": (1, 6),
    "도#3": (5, 4), "레#3": (4, 1), "파#3": (4, 4), "솔#3": (3, 1), "라#3": (3, 3),
    "도#4": (3, 6), "레#4": (2, 4), "파#4": (2, 7), "솔#4": (1, 4), "라#4": (1, 6),
    "도#5": (1, 9), "레#5": (1, 11), "파#5": (1, 14), "솔#5": (1, 16), "라#5": (1, 18)
}

def parse_note_token(token):
    """
    단일 단어(토큰)를 분석하여 주법 기호 및 프렛 텍스트 생성
    반환값: (target_string, fret_symbol, description)
    """
    token = token.strip()
    if not token:
        return None

    # 1. 연결 주법 (Slide 's' 또는 '/', Hammer-on 'h', Pull-off 'p')
    # 예: 도s레, 도/레, 도h레, 레p도
    connect_match = re.match(r'^([가-힣0-9#]+)([shp/])([가-힣0-9#]+)$', token)
    if connect_match:
        note1, op, note2 = connect_match.groups()
        if note1 in NOTE_MAP and note2 in NOTE_MAP:
            s1, f1 = NOTE_MAP[note1]
            s2, f2 = NOTE_MAP[note2]
            
            # 연결 주법은 기본적으로 동일한 줄에서 연주됨
            op_char = '/' if op in ['s', '/'] else op
            fret_symbol = f"{f1}{op_char}{f2}"
            
            label_map = {'s': '슬라이드', '/': '슬라이드', 'h': '해머링 온', 'p': '풀링 오프'}
            desc = f"{note1}→{note2} ({s1}번줄 {f1}→{f2}프렛 {label_map[op]})"
            return s1, fret_symbol, desc

    # 2. 단일 음 주법 (Bending 'b', Vibrato '~')
    # 예: 도b, 도~, 도4b~
    has_bend = 'b' in token
    has_vib = '~' in token
    clean_note = token.replace('b', '').replace('~', '')

    if clean_note in NOTE_MAP:
        string, fret = NOTE_MAP[clean_note]
        fret_symbol = str(fret)
        
        effects = []
        if has_bend:
            fret_symbol += "b"
            effects.append("밴딩")
        if has_vib:
            fret_symbol += "~"
            effects.append("비브라토")

        effect_str = f" ({', '.join(effects)})" if effects else ""
        desc = f"{clean_note}: {string}번줄 {fret}프렛{effect_str}"
        return string, fret_symbol, desc

    return None, "---", f"{token}: 인식 불가"

def generate_tab(notes_list):
    """입력받은 계이름 리스트를 TAB 악보 문자열로 변환"""
    strings = {s: [f"{name} |"] for s, name in zip(range(1, 7), ["e", "B", "G", "D", "A", "E"])}
    parsed_info = []

    for token in notes_list:
        if not token.strip():
            continue

        target_string, fret_symbol, desc = parse_note_token(token)
        parsed_info.append(desc)

        if target_string is None:
            # 인식 불가 토큰 처리
            for s in range(1, 7):
                strings[s].append("---")
            continue

        # 프렛 표기 길이에 맞게 다른 줄 간격(padding) 맞춰주기
        symbol_len = len(fret_symbol)
        padding = "-" * symbol_len

        for s in range(1, 7):
            if s == target_string:
                strings[s].append(f"{fret_symbol}-")
            else:
                strings[s].append(f"{padding}-")

    # 악보 마감 처리
    tab_output = [ "".join(strings[s]) + "|" for s in range(1, 7) ]
    return "\n".join(tab_output), parsed_info

# Streamlit UI 구성
st.set_page_config(page_title="일렉기타 TAB 악보 생성기", layout="centered")

st.title("🎸 계이름 -> 기타 TAB 악보 변환기 (특수 주법 지원)")
st.write("계이름과 주법 기호를 함께 입력하여 TAB 악보를 생성할 수 있습니다.")

# 사용자 입력
user_input = st.text_input(
    "계이름 입력", 
    value="도 레b 미~ 파s솔 라h시 도5p시4",
    placeholder="예: 도 레b 미~ 파s솔 라h시"
)

# 옥타브 및 특수주법 가이드 안내
with st.expander("💡 입력 팁 & 특수 주법 입력 방법"):
    st.markdown("""
    * **기본 입력**: `도`, `레`, `미`, `파`, `솔`, `라`, `시`
    * **옥타브 지정**: `도3`(저음), `도4`(중음), `도5`(고음)
    * **반음 입력**: `도#`, `레#`, `파#`, `솔#`, `라#`
    
    ---
    
    #### 🎸 특수 주법 입력법
    * **밴딩 (Bending)**: 음 뒤에 `b` 붙이기 $\rightarrow$ 예: `도b`, `솔4b`
    * **비브라토 (Vibrato)**: 음 뒤에 `~` 붙이기 $\rightarrow$ 예: `미~`, `라4~`
    * **슬라이드 (Slide)**: 두 음 사이에 `s` 또는 `/` 넣기 $\rightarrow$ 예: `도s레`, `파/솔`
    * **해머링 온 (Hammer-on)**: 두 음 사이에 `h` 넣기 $\rightarrow$ 예: `도h레`
    * **풀링 오프 (Pull-off)**: 두 음 사이에 `p` 넣기 $\rightarrow$ 예: `레p도`
    * **복합 적용**: `도b~` (밴딩 + 비브라토)
    """)

if user_input:
    notes = user_input.split()
    tab_result, parsed_info = generate_tab(notes)
    
    st.subheader("🎼 생성된 TAB 악보")
    st.code(tab_result, language="text")

    st.subheader("🎵 입력한 음 & 주법 매핑 정보")
    st.write(" | ".join([f"**{info}**" for info in parsed_info]))
