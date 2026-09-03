import re
import streamlit as st

# ==========================================
# 1. 기타 샵 느낌의 빈티지 우드 테마 CSS 설정
# ==========================================
def set_guitar_shop_theme():
    st.markdown(
        """
        <style>
        /* 전체 배경: 빈티지 우드/앰프 느낌의 다크 브라운 그라데이션 */
        .stApp {
            background-color: #2b1d14;
            background-image: radial-gradient(circle at 50% 50%, #4a3320 0%, #1a110c 100%);
            color: #f4e3c5;
        }
        
        /* 텍스트 입력창 및 박스 스타일링 */
        .stTextInput > div > div > input {
            background-color: #1a110c !important;
            color: #f4e3c5 !important;
            border: 2px solid #8b5a2b !important;
            border-radius: 8px;
        }
        
        /* Expander (안내창) 스타일 */
        .streamlit-expanderHeader {
            background-color: #3e271a !important;
            color: #fce8cd !important;
            border-radius: 5px;
        }
        
        /* 탭(Tab) 디자인 변경 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #3e271a;
            border-radius: 4px 4px 0px 0px;
            color: #f4e3c5;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #8b5a2b !important;
            color: white !important;
            border-bottom-color: #f4e3c5 !important;
        }
        
        /* 코드 블록(악보 출력부) 색상 */
        code {
            color: #ffcc00 !important;
            background-color: #110b08 !important;
            font-weight: bold;
            font-size: 1.1em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# 2. 기존 계이름 매핑 및 파싱 함수
# ==========================================
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
    token = token.strip()
    if not token: return None

    # 연결 주법 확인
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

    # 단일 음 주법 확인
    has_bend = 'b' in token
    has_vib = '~' in token
    clean_note = token.replace('b', '').replace('~', '')

    if clean_note in NOTE_MAP:
        string, fret = NOTE_MAP[clean_note]
        fret_symbol = str(fret)
        effects = []
        if has_bend: fret_symbol += "b"; effects.append("밴딩")
        if has_vib: fret_symbol += "~"; effects.append("비브라토")
        effect_str = f" ({', '.join(effects)})" if effects else ""
        desc = f"{clean_note}: {string}번줄 {fret}프렛{effect_str}"
        return string, fret_symbol, desc

    return None, "---", f"{token}: 인식 불가"

def generate_tab(notes_list):
    strings = {s: [f"{name} |"] for s, name in zip(range(1, 7), ["e", "B", "G", "D", "A", "E"])}
    parsed_info = []

    for token in notes_list:
        if not token.strip(): continue
        target_string, fret_symbol, desc = parse_note_token(token)
        parsed_info.append(desc)

        if target_string is None:
            for s in range(1, 7): strings[s].append("---")
            continue

        symbol_len = len(fret_symbol)
        padding = "-" * symbol_len

        for s in range(1, 7):
            if s == target_string:
                strings[s].append(f"{fret_symbol}-")
            else:
                strings[s].append(f"{padding}-")

    tab_output = [ "".join(strings[s]) + "|" for s in range(1, 7) ]
    return "\n".join(tab_output), parsed_info

# ==========================================
# 3. 파워코드 매핑 및 생성 함수 (새로운 기능)
# ==========================================
POWER_CHORD_MAP = {
    "C": (5, 3), "C#": (5, 4), "Db": (5, 4), "D": (5, 5), "D#": (5, 6), "Eb": (5, 6),
    "E": (6, 0), "F": (6, 1), "F#": (6, 2), "Gb": (6, 2), "G": (6, 3), "G#": (6, 4), "Ab": (6, 4),
    "A": (6, 5), "A#": (5, 1), "Bb": (5, 1), "B": (5, 2)
}

def generate_power_chord_tab(chords_list):
    """입력받은 코드 리스트를 3-노트 파워코드 TAB 악보로 변환"""
    strings = {s: [f"{name} |"] for s, name in zip(range(1, 7), ["e", "B", "G", "D", "A", "E"])}
    parsed_info = []

    for token in chords_list:
        if not token.strip(): continue
        
        # 정규식을 이용해 코드의 근음(Root)만 추출 (예: Cmaj7 -> C, F#m -> F#)
        root_match = re.match(r'^([A-G][#b]?)', token, re.IGNORECASE)
        
        if root_match:
            root_note = root_match.group(1).capitalize()
            if root_note in POWER_CHORD_MAP:
                root_string, root_fret = POWER_CHORD_MAP[root_note]
                
                # 3노트 파워코드 (근음, 5도, 옥타브) 프렛 계산
                fret_5th = root_fret + 2 if root_fret != 0 else 2
                fret_octave = root_fret + 2 if root_fret != 0 else 2
                
                # 자리 배치
                for s in range(1, 7):
                    if s == root_string:
                        strings[s].append(f"-{root_fret:2}-")
                    elif s == root_string - 1:
                        strings[s].append(f"-{fret_5th:2}-")
                    elif s == root_string - 2:
                        strings[s].append(f"-{fret_octave:2}-")
                    else:
                        strings[s].append("----")
                
                parsed_info.append(f"{token} -> {root_note}5 파워코드 ({root_string}번줄 {root_fret}프렛 근음)")
                continue
                
        # 인식 불가 처리
        for s in range(1, 7): strings[s].append("----")
        parsed_info.append(f"{token}: 인식 불가")

    tab_output = [ "".join(strings[s]) + "|" for s in range(1, 7) ]
    return "\n".join(tab_output), parsed_info


# ==========================================
# 4. Streamlit UI 구성
# ==========================================
st.set_page_config(page_title="기타 샵 악보 생성기", layout="centered", page_icon="🎸")
set_guitar_shop_theme()

st.title("🎸 톤우드 기타 샵 (Tab Generator)")
st.write("솔로 라인(계이름)과 백킹 트랙(파워코드)을 탭 악보로 손쉽게 변환하세요.")

# 탭 나누기
tab1, tab2 = st.tabs(["🎼 멜로디 (계이름 -> TAB)", "🤘 백킹 (일반코드 -> 파워코드)"])

with tab1:
    user_input_melody = st.text_input(
        "계이름 및 주법 입력", 
        value="도 레b 미~ 파s솔 라h시 도5p시4",
        placeholder="예: 도 레b 미~ 파s솔 라h시",
        key="melody_input"
    )

    with st.expander("💡 입력 팁 & 특수 주법 입력 방법"):
        st.markdown("""
        * **기본 입력**: `도`, `레`, `미`, `파`, `솔`, `라`, `시`
        * **옥타브 지정**: `도3`(저음), `도4`(중음), `도5`(고음)
        * **반음 입력**: `도#`, `레#`
        
        #### 🎸 특수 주법
        * **밴딩**: `b` (예: `도b`)
        * **비브라토**: `~` (예: `미~`)
        * **슬라이드**: `s` 또는 `/` (예: `도s레`)
        * **해머링 온**: `h` (예: `도h레`)
        * **풀링 오프**: `p` (예: `레p도`)
        """)

    if user_input_melody:
        notes = user_input_melody.split()
        tab_result, parsed_info = generate_tab(notes)
        
        st.code(tab_result, language="text")
        st.write(" | ".join([f"**{info}**" for info in parsed_info]))

with tab2:
    user_input_chord = st.text_input(
        "코드 진행 입력 (마이너, 세븐스 등은 자동 생략됨)", 
        value="C G Am F Dm E7",
        placeholder="예: C G Am F",
        key="chord_input"
    )

    with st.expander("💡 파워코드 변환기 안내"):
        st.markdown("""
        * 일렉기타 백킹에서 주로 쓰이는 **파워코드(Power Chord, 1도-5도-8도)**로 강제 변환합니다.
        * `Cmaj7`, `Am`, `D9` 등 복잡한 코드를 입력해도 자동으로 **근음(Root)**을 찾아 파워코드 형태(`C5`, `A5`, `D5`)로 출력합니다.
        * **근음 위치 기준**: 6번줄(E~A#)과 5번줄(A#~D#)을 기준으로 가장 잡기 편한 포지션을 자동 배정합니다.
        """)

    if user_input_chord:
        chords = user_input_chord.split()
        power_tab_result, power_parsed_info = generate_power_chord_tab(chords)
        
        st.code(power_tab_result, language="text")
        for info in power_parsed_info:
            st.write(f"- {info}")
