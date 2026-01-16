import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. 디자인 보정 (글자색 명시적 지정) ---
st.set_page_config(page_title="욕망의 탑", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 0rem; padding-bottom: 0rem; max-width: 100%;}
    
    /* 전체 배경 및 기본 글자색 강제 지정 */
    html, body, [class*="css"] {
        background-color: #050505 !important;
        color: #FFFFFF !important; /* 글자색을 순백색으로 고정 */
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* 상단 고정 상태창 디자인 보정 */
    .status-bar {
        position: fixed; top: 0; left: 0; width: 100%;
        background: #111111; padding: 12px 0; border-bottom: 2px solid #ff4b4b;
        z-index: 9999; display: flex; justify-content: space-around;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.6);
    }
    .stat-item { text-align: center; flex: 1; border-right: 1px solid #333; }
    .stat-item:last-child { border-right: none; }
    .stat-label { font-size: 11px; color: #AAAAAA; margin-bottom: 2px; font-weight: bold; }
    .stat-value { font-size: 13px; font-weight: bold; color: #ff4b4b; }

    /* HP 게이지 */
    .hp-bg { width: 80px; background: #333; height: 8px; border-radius: 4px; margin: 4px auto; overflow: hidden; }
    .hp-fill { background: linear-gradient(90deg, #ff4b4b, #ff8080); height: 100%; transition: width 0.5s; }

    /* 스토리 카드 가독성 강화 */
    .content-wrapper { margin-top: 100px; padding: 20px; padding-bottom: 150px; }
    .story-bubble {
        background: #1A1A1A; border-left: 5px solid #ff4b4b;
        padding: 25px; border-radius: 12px; margin-bottom: 25px;
        line-height: 1.8; font-size: 17px; white-space: pre-wrap;
        color: #FFFFFF !important; /* 카드 내 글자색 흰색 고정 */
        box-shadow: 8px 8px 20px rgba(0,0,0,0.7);
    }

    /* 하단 버튼 */
    .stButton>button { 
        background: #111 !important; color: #FFF !important; 
        border: 1px solid #ff4b4b !important; font-size: 16px !important;
    }
    .stButton>button:hover { background: #ff4b4b !important; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API 연결 ---
genai.configure(api_key="AIzaSyCdfCaW_5i1SJ3voHnVM3IWxSnkOSQtZ7M") 
model = genai.GenerativeModel('gemini-2.0-flash')

if "messages" not in st.session_state: st.session_state.messages = []
if "player" not in st.session_state:
    st.session_state.player = {
        "name": "도전자", "ability": "각성 대기 중", "grade": "-", "floor": 0,
        "hp": 100, "atk": 10, "def": 10, "inventory": []
    }
if "is_dead" not in st.session_state: st.session_state.is_dead = False

# --- 3. 로직 함수 (데이터 정제 강화) ---

def get_ai_response(user_input):
    system_prompt = f"""당신은 '욕망의 탑' 마스터입니다. 
    - 응답 마지막에 반드시 [HP:-10] 같은 스탯 변화를 포함하세요.
    - 선택지는 4개를 명확히 제시하세요.
    현재 플레이어: {st.session_state.player}"""
    chat = model.start_chat(history=[])
    response = chat.send_message(f"{system_prompt}\n\n입력: {user_input}")
    return response.text

def clean_ability_name(text):
    """능력 이름에서 특수문자와 주사위 숫자를 제거하는 함수"""
    cleaned = re.sub(r"##|주사위|결과|:|등급|[0-9]|\"|\'", "", text)
    return cleaned.strip()[:10] # 최대 10자까지만

def parse_changes(text):
    for stat in ["HP", "ATK", "DEF"]:
        match = re.search(fr"\[{stat}:([+-]?\d+)\]", text)
        if match: st.session_state.player[stat.lower()] += int(match.group(1))
    if st.session_state.player["hp"] <= 0:
        st.session_state.player["hp"] = 0
        st.session_state.is_dead = True

# --- 4. 화면 출력 ---

# [상단 바]
hp_p = max(0, min(100, st.session_state.player['hp']))
st.markdown(f"""
    <div class="status-bar">
        <div class="stat-item"><div class="stat-label">도전자</div><div class="stat-value">{st.session_state.player['name']}</div></div>
        <div class="stat-item"><div class="stat-label">위치</div><div class="stat-value">{st.session_state.player['floor']}F</div></div>
        <div class="stat-item">
            <div class="stat-label">체력 {hp_p}%</div>
            <div class="hp-bg"><div class="hp-fill" style="width:{hp_p}%"></div></div>
        </div>
        <div class="stat-item"><div class="stat-label">능력({st.session_state.player['grade']})</div><div class="stat-value">{st.session_state.player['ability']}</div></div>
        <div class="stat-item"><div class="stat-label">전투/방어</div><div class="stat-value">⚔️{st.session_state.player['atk']} / 🛡️{st.session_state.player['def']}</div></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

if st.session_state.is_dead:
    st.markdown('<div class="story-bubble" style="border-color:red; text-align:center;"><h1>YOU DIED</h1><p>탑의 거름이 되었습니다.</p></div>', unsafe_allow_html=True)
    if st.button("새로운 운명으로 시작하기"):
        st.session_state.clear()
        st.rerun()

elif st.session_state.player['floor'] == 0:
    st.title("🏙️ 욕망의 탑: SEOUL")
    name_in = st.text_input("이름을 입력하세요")
    if name_in and st.button("탑 입장"):
        st.session_state.player['name'] = name_in
        dice = random.randint(1, 100)
        # 등급 부여
        g = "EX" if dice >= 99 else "S" if dice >= 90 else "A" if dice >= 70 else "B" if dice >= 40 else "F"
        st.session_state.player['grade'] = g
        
        # AI에게 딱 능력 이름만 먼저 물어봄
        res_ab = model.generate_content(f"주사위 {dice}, 등급 {g}입니다. 이 캐릭터의 '능력 이름' 딱 하나만 짧게 알려주세요. (수식어 없이)")
        st.session_state.player['ability'] = clean_ability_name(res_ab.text)
        
        # 이후 첫 스토리 생성
        res_story = model.generate_content(f"내 능력은 {st.session_state.player['ability']}입니다. 1층 입구 스토리를 시작하세요.")
        st.session_state.player['floor'] = 1
        st.session_state.messages.append({"role": "assistant", "content": res_story.text})
        st.rerun()

else:
    for msg in st.session_state.messages:
        label = "👤 PLAYER" if msg["role"] == "user" else "💀 MASTER"
        st.markdown(f'<div class="story-bubble"><b>{label}</b><br><br>{msg["content"]}</div>', unsafe_allow_html=True)

    st.divider()
    cols = st.columns(4)
    for i in range(1, 5):
        if cols[i-1].button(f"선택지 {i}"):
            dice = random.randint(1, 100)
            st.toast(f"🎲 주사위 결과: {dice}")
            with st.spinner("운명 계산 중..."):
                res_text = get_ai_response(f"{i}번 선택, 주사위 {dice}.")
                parse_changes(res_text)
                st.session_state.messages.append({"role": "user", "content": f"{i}번 선택 (주사위 {dice})"})
                st.session_state.messages.append({"role": "assistant", "content": res_text})
                if "대기실" in res_text: st.session_state.player['floor'] += 1
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
