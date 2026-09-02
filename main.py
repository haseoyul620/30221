import streamlit as st

# 기타 6개 줄별 기본 튜닝 기준 옥타브별 포지션 매핑 (표준 튜닝: E A D G B E)
# [줄 번호(1~6줄), 프렛 번호]
NOTE_MAP = {
    # 3옥타브 (저음역대)
    "도3": (5, 3), "레3": (5, 5), "미3": (4, 2), "파3": (4, 3), "솔3": (4, 5), "라3": (3, 2), "시3": (3, 4),
    
    # 4옥타브 (중음역대 - 기본값)
    "도4": (3, 5), "레4": (2, 3), "미4": (2, 5), "파4": (2, 6), "솔4": (1, 3), "라4": (1, 5), "시4": (1, 7),
    
    # 5옥타브 (고음 솔로)
    "도5": (1, 8), "레5": (1, 10), "미5": (1, 12), "파5": (1, 13), "솔5": (1, 15), "라5": (1, 17), "시5": (1, 19),
    
    # 단순 계이름 입력 시 기본 4옥타브 포지션으로 매핑
    "도": (3, 5), "레": (2, 3), "미": (2, 5), "파": (2, 6), "솔": (1, 3), "라": (1, 5), "시": (1, 7),
    
    # 샵(#) 포함 계이름
    "도#": (3, 6), "레#": (2, 4), "파#": (2, 7), "솔#": (1, 4), "라#": (1, 6)
}

def generate_tab(notes_list):
    """입력받은 계이름 리스트를 TAB 악보 문자열로 변환"""
    # 기타 6개 줄 초기화 (1번 줄이 최상단, 6번 줄이 최하단)
    strings = {
        1: ["e |"],
        2: ["B |"],
        3: ["G |"],
        4: ["D |"],
        5: ["A |"],
        6: ["E |"]
    }
    
    for note in notes_list:
        note = note.strip()
        if not note:
            continue
            
        if note in NOTE_MAP:
            target_string, fret = NOTE_MAP[note]
            fret_str = str(fret)
            padding = "-" * len(fret_str)
            
            for s in range(1, 7):
                if s == target_string:
                    strings[s].append(f"{fret_str}-")
                else:
                    strings[s].append(f"{padding}-")
        else:
            # 알 수 없는 음인 경우 공백 처리
            for s in range(1, 7):
                strings[s].append("---")
                
    # 악보 마감 처리
    tab_output = []
    for s in range(1, 7):
        tab_output.append("".join(strings[s]) + "|")
        
    return "\n".join(tab_output)

# Streamlit UI 구성
st.set_page_config(page_title="일렉기타 TAB 악보 생성기", layout="centered")

st.title("🎸 계이름 -> 기타 TAB 악보 변환기")
st.write("계이름을 띄어쓰기로 구분하여 입력하면 일렉기타 TAB 악보를 생성합니다.")

# 사용자 입력
user_input = st.text_input(
    "계이름 입력", 
    value="도 레 미 파 솔 라 시 도5",
    placeholder="예: 도 레 미 파 솔 라 시 / 도4 레4 미4"
)

# 옥타브 가이드 안내
with st.expander("💡 입력 팁 & 옥타브 지정 방법"):
    st.markdown("""
    * **기본 입력**: `도`, `레`, `미`, `파`, `솔`, `라`, `시` 입력 시 기타 중간 음역대(3~1번줄)로 자동 배치됩니다.
    * **옥타브 지정**: `도3`(저음), `도4`(중음), `도5`(고음 솔로)처럼 숫자를 붙여 옥타브를 지정할 수 있습니다.
    * **반음 입력**: `도#`, `레#`, `파#`, `솔#`, `라#` 입력 가능합니다.
    """)

if user_input:
    notes = user_input.split()
    tab_result = generate_tab(notes)
    
    st.subheader("🎼 생성된 TAB 악보")
    st.code(tab_result, language="text")

    st.subheader("🎵 입력한 음 매핑 정보")
    parsed_info = []
    for n in notes:
        n_clean = n.strip()
        if n_clean in NOTE_MAP:
            s, f = NOTE_MAP[n_clean]
            parsed_info.append(f"**{n_clean}**: {s}번줄 {f}프렛")
        else:
            parsed_info.append(f"**{n_clean}**: 인식 불가")
    st.write(" | ".join(parsed_info))
