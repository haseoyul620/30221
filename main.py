import re
import streamlit as st

# Streamlit UI 기본 설정
st.set_page_config(page_title="GUITAR SHOP - TAB & Power Chord", layout="centered")

# 🎨 기타 샵(Guitar Shop) 분위기 CSS 스타일링
st.markdown("""
    <style>
    /* 전체 배경: 세련된 다크 메탈/앰프 스타일 */
    .stApp {
        background-color: #0e0e12;
        color: #e0e0e0;
    }
    
    /* 메인 타이틀 네온 글로우 효과 */
    h1 {
        color: #ffb400 !important;
        text-shadow: 0 0 10px rgba(255, 180, 0, 0.5), 0 0 20px rgba(255, 180, 0, 0.3);
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    
    /* 서브 헤더 스타일 */
    h2, h3 {
        color: #f39c12 !important;
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
    }

    /* 입력창 및 패널 컨테이너 (앰프/페달 느낌) */
    .stTextInput > div > div > input {
        background-color: #1a1a24 !important;
        color: #00ffcc !important;
        border: 1px solid #ffb400 !important;
        border-radius: 6px;
        font-family: 'Courier New', monospace;
    }

    /* Expander 스타일 */
    .streamlit-expanderHeader {
        background-color: #16161d !important;
        color: #ffb400 !important;
        border: 1px solid #333;
        border-radius: 4px;
    }

    /* TAB 악보 출력 코드 블록 (골드/그린 네온 텍스트) */
    .stCodeBlock {
        border: 2px solid #ffb400 !important;
        box-shadow: 0 0 15px rgba(255, 180, 0, 0.2);
    }
    
    /* 배지/정보 박스 */
    .info-box {
        background-color: #1a1a24;
        border-left: 4px solid #ffb400;
        padding: 10px 15px;
        margin-top: 10px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_dict=True)


# ------------------------------------------------------------------
# 1. 기존 멜로디 / 옥타브 / 특수주법 TAB 데이터 & 로직
# ------------------------------------------------------------------
NOTE_MAP = {
    "미2": (6, 0), "파2": (6, 1), "솔2": (6, 3), "라2": (5, 0), "시2": (5, 2),
    "도3": (5, 3), "레3": (5, 5), "미3": (4, 2), "파3": (4, 3), "솔3": (4, 5), "라3": (3, 2), "시3": (3, 4),
    "도4": (3, 5), "레4": (2, 3), "미4": (2, 5), "파4": (2, 6), "솔4": (1, 3), "라4": (1, 5), "시4": (1, 7),
    "도5": (1, 8), "레5": (1, 10), "미5": (1, 12), "파5": (1, 13), "솔5": (1, 15), "라5": (1, 17), "시5": (1, 19),
    "도": (3, 5), "레": (2, 3), "미": (2, 5), "파": (2, 6), "솔": (1, 3), "라": (1, 5), "시": (1, 7),
    "도#": (3, 6), "레#": (2, 4), "파#": (2, 7), "솔#": (1, 4), "라#": (1, 6),
    "도#3": (5, 4), "레#3": (4, 1), "파#3": (4, 4), "솔#3": (3, 1), "라#3": (3, 3),
    "도#4": (3, 6), "레#4": (2, 4), "파#4": (2, 7), "솔#4": (1, 4), "라#4": (1, 6),
    "도#5": (1, 9), "레#5": (1, 11), "파#5": (1, 14), "솔#5": (1, 16), "라#5": (1, 18)
}

def parse_note_token(token):
    token = token.strip()
    if not token:
        return None

    # 연결 주법 (s, /, h, p)
    connect_match = re.match(r'^([가-힣0-9#]+)([shp/])([가-힣0-9#]+)$', token)
    if connect_match:
        note1, op, note2 = connect_match.groups()
        if note1 in NOTE_MAP and note2 in NOTE_MAP:
            s1, f1 = NOTE_MAP[note1]
            s2, f2 = NOTE_MAP[note2]
            op_char = '/' if op in ['s', '/'] else op
            fret_symbol = f"{f1}{op_char}{f2}"
            label_map = {'s': '슬라이드', '/': '슬라이드', 'h': '해머링 온', 'p': '풀링 오프'}
            desc = f"{note1}→{note2} ({s1}번줄 {f1}→{f2}프렛 {label_map[op]})"
            return s1, fret_symbol, desc

    # 단일 음 주법 (b, ~)
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
    strings = {s: [f"{name} |"] for s, name in zip(range(1, 7), ["e", "B", "G", "D", "A", "E"])}
    parsed_info = []

    for token in notes_list:
        if not token.strip():
            continue

        target_string, fret_symbol, desc = parse_note_token(token)
        parsed_info.append(desc)

        if target_string is None:
            for s in range(1, 7):
                strings[s].append("---")
            continue

        symbol_len = len(fret_symbol)
        padding = "-" * symbol_len

        for s in range(1, 7):
            if s == target_string:
                strings[s].append(f"{fret_symbol}-")
            else:
                strings[s].append(f"{padding}-")

    tab_output = ["".join(strings[s]) + "|" for s in range(1, 7)]
    return "\n".join(tab_output), parsed_info


# ------------------------------------------------------------------
# 2. 파워코드(Power Chord) 매핑 로직 추가
# ------------------------------------------------------------------
POWER_CHORD_MAP = {
    # 6번 줄 근음 기준 파워코드 (6번줄 프렛, 5번줄 프렛, 4번줄 프렛)
    "F": (6, 1, 3, 3), "F#": (6, 2, 4, 4), "Gb": (6, 2, 4, 4),
    "G": (6, 3, 5, 5), "G#": (6, 4, 6, 6), "Ab": (6, 4, 6, 6),
    "A": (6, 5, 7, 7), "A#": (6, 6, 8, 8), "Bb": (6, 6, 8, 8),
    "B": (6, 7, 9, 9),
    
    # 5번 줄 근음 기준 파워코드 (5번줄 프렛, 4번줄 프렛, 3번줄 프렛)
    "C": (5, 3, 5, 5), "C#": (5, 4, 6, 6), "Db": (5, 4, 6, 6),
    "D": (5, 5, 7, 7), "D#": (5, 6, 8, 8), "Eb": (5, 6, 8, 8),
    "E": (5, 7, 9, 9)
}

def generate_power_chord_tab(chords_list):
    """입력된 코드명을 파워코드 TAB 악보로 변환"""
    strings = {s: [f"{name} |"] for s, name in zip(range(1, 7), ["e", "B", "G", "D", "A", "E"])}
    info_list = []

    for chord in chords_list:
        # 코드에서 파워코드 근음 추출 (예: Cmaj7 -> C, F#m -> F#)
        clean_chord = re.sub(r'(m|maj|min|7|dim|aug|add9|sus4).*', '', chord, flags=re.IGNORECASE).capitalize()
        
        if clean_chord in POWER_CHORD_MAP:
            root_string, f_root, f_fifth, f_octave = POWER_CHORD_MAP[clean_chord]
            
            # 6번줄 근음 파워코드인 경우 (6, 5, 4번줄 사용)
            if root_string == 6:
                active_frets = {6: str(f_root), 5: str(f_fifth), 4: str(f_octave)}
            # 5번줄 근음 파워코드인 경우 (5, 4, 3번줄 사용)
            else:
                active_frets = {5: str(f_root), 4: str(f_fifth), 3: str(f_octave)}

            max_len = max(len(v) for v in active_frets.values())
            
            for s in range(1, 7):
                if s in active_frets:
                    val = active_frets[s].ljust(max_len, '-')
                    strings[s].append(f"{val}-")
                else:
                    strings[s].append("-" * max_len + "-")
            
            info_list.append(f"{chord} $\\rightarrow$ {clean_chord}5 ({root_string}번줄 근음)")
        else:
            for s in range(1, 7):
                strings[s].append("---")
            info_list.append(f"{chord}: 변환 불가")

    tab_output = ["".join(strings[s]) + "|" for s in range(1, 7)]
    return "\n".join(tab_output), info_list


# ------------------------------------------------------------------
# 3. Streamlit UI 메인 화면 구성
# ------------------------------------------------------------------
st.title("🎸 ROCK GUITAR SHOP & TAB GENERATOR")
st.caption("일렉기타 리프 멜로디 및 파워코드(Power Chord) 자동 TAB 생성 시스템")

# 탭 나누기 (멜로디 TAB 변환 / 파워코드 변환)
tab1, tab2 = st.tabs(["🎼 멜로디 & 특수주법 TAB", "⚡ 파워코드(Power Chord) 변환"])

# --- TAB 1: 멜로디 & 특수주법 ---
with tab1:
    st.subheader("계이름 $\\rightarrow$ TAB 악보")
    user_input = st.text_input(
        "계이름 입력", 
        value="도 레b 미~ 파s솔 라h시 도5p시4",
        placeholder="예: 도 레b 미~ 파s솔 라h시"
    )

    with st.expander("💡 멜로디 & 주법 입력 가이드"):
        st.markdown("""
        * **기본/옥타브**: `도3`(저음), `도4`(중음), `도5`(고음), `도#`
        * **밴딩**: 음 뒤 `b` (예: `도b`, `솔4b`)
        * **비브라토**: 음 뒤 `~` (예: `미~`)
        * **슬라이드/해머링/풀링**: `도s레`, `도h레`, `레p도`
        """)

    if user_input:
        notes = user_input.split()
        tab_result, parsed_info = generate_tab(notes)
        
        st.code(tab_result, language="text")
        st.markdown("<div class='info-box'>" + " | ".join([f"**{info}**" for info in parsed_info]) + "</div>", unsafe_allow_dict=True)

# --- TAB 2: 파워코드 변환기 ---
with tab2:
    st.subheader("일반 기타 코드 $\\rightarrow$ 5도 파워코드(Power Chord)")
    chord_input = st.text_input(
        "코드 진행 입력 (공백으로 구분)",
        value="C G Am F",
        placeholder="예: C G Am F 또는 E F#m G A"
    )

    with st.expander("💡 파워코드(5도 코드) 특징"):
        st.markdown("""
        * **파워코드(Root + 5th)**: 3도 음을 생략하여 드라이브/디스토션 앰프 사용 시 깔끔하고 묵직한 톤을 연출합니다.
        * 일반 코드(C, Am, Fmaj7 등)를 입력하면 자동으로 근음(Root)을 추출해 **Power Chord(5)**로 일괄 전환합니다.
        """)

    if chord_input:
        chords = chord_input.split()
        p_tab_result, p_info = generate_power_chord_tab(chords)
        
        st.code(p_tab_result, language="text")
        st.markdown("<div class='info-box'>" + " | ".join([f"**{info}**" for info in p_info]) + "</div>", unsafe_allow_dict=True)
