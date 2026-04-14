"""
🍔 먹픽(muk pick!) — 리뷰 AI 분석기
=====================================
실행 방법:
    pip install streamlit transformers pandas torch matplotlib selenium webdriver-manager
    python -m streamlit run realmukpick.py

입력 방식:
    1. 직접 입력 (텍스트 영역)
    2. 샘플 데이터
    3. CSV 파일 업로드 (컬럼 자동 감지)
    4. 네이버 플레이스 크롤링
"""

# ──────────────────────────────────────────────────────────
# 표준 라이브러리
# ──────────────────────────────────────────────────────────
import re
import time
import random
from collections import Counter

# ──────────────────────────────────────────────────────────
# 서드파티 라이브러리
# ──────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline


# ══════════════════════════════════════════════════════════
# 0. 페이지 설정  ← 반드시 첫 번째 Streamlit 호출
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="먹픽(muk pick!)",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ══════════════════════════════════════════════════════════
# 1. 커스텀 CSS
# ══════════════════════════════════════════════════════════
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}
.main-title {
    font-size: 2.8rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #f7971e, #ffd200);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 1.5rem 0 0.4rem;
    letter-spacing: -1px;
}
.sub-title {
    text-align: center;
    color: #a0a0c0;
    font-size: 1rem;
    margin-bottom: 0.4rem;
}
.version-badge {
    text-align: center;
    margin-bottom: 1.4rem;
}
.version-badge span {
    background: rgba(255,210,0,0.12);
    border: 1px solid rgba(255,210,0,0.32);
    border-radius: 50px;
    padding: 0.22rem 1rem;
    color: #ffd200;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 1.5px;
}
.card {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px;
    padding: 1.5rem 2rem;
    margin: 0.75rem 0;
    backdrop-filter: blur(14px);
}
.card-title {
    font-size: 0.74rem;
    font-weight: 800;
    color: #ffd200;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-bottom: 1rem;
}
.composite-box {
    background: linear-gradient(135deg,
        rgba(247,151,30,0.16) 0%,
        rgba(255,210,0,0.09) 100%);
    border: 1px solid rgba(255,210,0,0.35);
    border-radius: 14px;
    padding: 1.4rem 1.8rem;
    font-size: 1.2rem;
    font-weight: 600;
    color: #fff8e1;
    line-height: 1.75;
    margin: 0.5rem 0 1rem;
    position: relative;
}
.composite-box::before {
    content: "💬";
    font-size: 1.5rem;
    margin-right: 0.6rem;
}
.summary-point {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    font-size: 0.94rem;
    color: #ddd;
    line-height: 1.65;
}
.summary-point:last-child { border-bottom: none; }
.summary-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-top: 7px;
    flex-shrink: 0;
}
.stat-number {
    font-size: 2.4rem;
    font-weight: 900;
    line-height: 1;
}
.stat-label {
    font-size: 0.82rem;
    color: #777;
    margin-top: 0.3rem;
}
.kw-wrap  { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.5rem; }
.kw-tag   { border-radius: 50px; padding: 0.3rem 0.85rem; font-size: 0.85rem; font-weight: 600; }
.kw-pos   { background: rgba(56,239,125,0.12); border: 1px solid rgba(56,239,125,0.32); color: #38ef7d; }
.kw-neg   { background: rgba(244,67,54,0.12);  border: 1px solid rgba(244,67,54,0.32);  color: #f44336; }
.kw-neu   { background: rgba(255,210,0,0.12);  border: 1px solid rgba(255,210,0,0.32);  color: #ffd200; }
.review-sample {
    background: rgba(255,255,255,0.035);
    border-left: 3px solid;
    border-radius: 6px;
    padding: 0.6rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.9rem;
    color: #ccc;
    line-height: 1.65;
}
.review-pos { border-color: #38ef7d; }
.review-neu { border-color: #ffd200; }
.review-neg { border-color: #f44336; }
.stButton > button {
    background: linear-gradient(90deg, #f7971e, #ffd200) !important;
    color: #1a1a2e !important;
    font-weight: 800 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.6rem 2.5rem !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 20px rgba(255,210,0,0.28) !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(255,210,0,0.46) !important;
}
hr { border-color: rgba(255,255,255,0.08) !important; }
.upload-hint { text-align: center; color: #555; font-size: 0.82rem; margin-top: 0.5rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════
# 2. 감정 분석 — 가중치 스코어링 + 3단계 완화 분류
# ══════════════════════════════════════════════════════════

POS_DICT: dict[str, float] = {
    "맛있": 1.0, "최고": 1.0, "대박": 1.0, "강추": 1.0, "완벽": 1.0,
    "감동": 1.0, "훌륭": 1.0, "맛집": 1.0,
    "재주문": 0.7, "또시킬": 0.7, "만족": 0.7, "좋아요": 0.7, "좋았": 0.7,
    "추천": 0.7, "친절": 0.7, "신선": 0.7, "가성비": 0.7, "빠르": 0.7,
    "푸짐": 0.7, "깔끔": 0.7, "굿": 0.7,
    "맛나": 0.4, "괜찮": 0.4, "나쁘지않": 0.4, "무난": 0.4, "보통": 0.3,
}

NEG_DICT: dict[str, float] = {
    "최악": 1.0, "별로": 1.0, "실망": 1.0, "환불": 1.0, "후회": 1.0,
    "토할": 1.0, "이물": 1.0, "상한": 1.0,
    "못먹": 0.7, "못 먹": 0.7, "불친절": 0.7, "오배달": 0.7, "불만": 0.7,
    "짜다": 0.7, "짜고": 0.7, "늦": 0.7, "느리": 0.7, "식어": 0.7,
    "식었": 0.7, "아쉽": 0.7, "딱딱": 0.7, "퍽퍽": 0.7,
    "비싸": 0.4, "작아": 0.4, "적어": 0.4, "없어요": 0.35, "다시는": 0.6,
    "이상한": 0.5, "구려": 0.8, "잘못": 0.5,
    # ✅ MUKPICK 추가 부정 키워드
    "노맛": 1.0, "노베": 0.8, "별로임": 1.0, "맛없": 1.0, "안맛": 0.9,
    "느림": 0.7, "다신안": 0.8, "토나": 1.0, "역겨": 1.0, "짜증": 0.7,
    "별로예요": 1.0, "별로에요": 1.0, "노맛임": 1.0, "맛이없": 1.0,
    "맛도없": 1.0, "최악이": 1.0,
}


def _weighted_bias(text: str) -> float:
    t = text.lower()
    pos_score = sum(w for kw, w in POS_DICT.items() if kw in t)
    neg_score = sum(w for kw, w in NEG_DICT.items() if kw in t)
    total = pos_score + neg_score
    if total == 0.0:
        return 0.0
    return (pos_score - neg_score) / total


def _raw_to_score(label: str, score: float, model_type: str) -> float:
    label = label.upper()
    if model_type == "kr":
        if "POS" in label:   return score
        elif "NEG" in label: return 1.0 - score
        else:                return 0.5
    elif model_type == "multi":
        stars = int(label.split()[0]) if label and label[0].isdigit() else 3
        return (stars - 1) / 4.0
    else:
        return score if "POS" in label else 1.0 - score


def _score_to_label(s: float) -> str:
    if s >= 0.55:
        return "긍정"
    if s <= 0.40:
        return "부정"
    return "중립"


@st.cache_resource
def load_sentiment_model():
    candidates = [
        ("snunlp/KR-FinBert-SC",                             "kr"),
        ("monologg/koelectra-base-finetuned-sentiment",       "kr"),
        ("nlptown/bert-base-multilingual-uncased-sentiment",  "multi"),
        ("distilbert-base-uncased-finetuned-sst-2-english",   "en"),
    ]
    for model_id, mtype in candidates:
        try:
            mdl = pipeline("text-classification", model=model_id, device=-1)
            return mdl, mtype
        except Exception:
            continue
    raise RuntimeError("사용 가능한 감정 분석 모델이 없습니다.")


def analyze_sentiment(texts: list, model, model_type: str) -> list:
    truncated   = [t[:512] if isinstance(t, str) else "" for t in texts]
    raw_results = []

    for i in range(0, len(truncated), 32):
        batch = truncated[i:i + 32]
        try:
            raw_results.extend(model(batch))
        except Exception:
            raw_results.extend([{"label": "NEUTRAL", "score": 0.5}] * len(batch))

    results = []
    for text, r in zip(texts, raw_results):
        model_score = _raw_to_score(
            r.get("label", ""), r.get("score", 0.5), model_type
        )
        bias        = _weighted_bias(str(text))
        final_score = max(0.0, min(1.0, model_score + bias * 0.22))
        results.append({
            "label": _score_to_label(final_score),
            "score": round(final_score, 4),
        })
    return results


# ══════════════════════════════════════════════════════════
# 3. 키워드 추출
# ══════════════════════════════════════════════════════════

STOPWORDS: set[str] = {
    "이","그","저","것","수","등","및","를","을","가","은","는","에","의","로",
    "으로","도","만","와","과","나","다","하다","있다","없다","되다","했","해서",
    "해요","했어요","했습니다","합니다","같아요","같습니다","거","좀","더",
    "너무","정말","진짜","그냥","한","또","이번","번","번째","주문","시켰",
    "먹었","왔","왔어요","왔습니다","받았","받았어요","배달","음식","리뷰",
    "후기","가게","여기","거기","이거","저거","뭐","어","아","네","예",
    "ㅋㅋ","ㅎㅎ","ㄷㄷ","ㅠㅠ","ㅜㅜ","그리고","그런데","하지만",
    "근데","이렇게","저렇게","어떻게","때문","진짜로","정말로",
}

FOOD_KW_POS: list[str] = [
    "맛있","맛집","최고","대박","강추","추천","재주문","가성비",
    "푸짐","양많","신선","친절","빠른","깔끔","완벽","만족","훌륭",
    "고소","담백","얼큰","매콤","달콤","국물","면발","바삭","촉촉",
]
FOOD_KW_NEG: list[str] = [
    "별로","실망","최악","느린","늦게","식어","딱딱","퍽퍽","짜다",
    "싱겁","비싸","양적","환불","불만","아쉽","불친절","오배달","이물",
    "상한","후회","다시는","못먹","구려","냄새","노맛",
]

_BAD_ENDINGS: tuple = (
    "하고","해서","하면","하게","했는","같은","이런","그런",
    "에서","에게","까지","부터","이라","이고","이며","이나",
    "처럼","만큼","위해","통해","따라","대한","관한",
)


def _extract_counter(text_list: list) -> Counter:
    all_text = " ".join(str(t) for t in text_list)
    c: Counter = Counter()
    for kw in FOOD_KW_POS + FOOD_KW_NEG:
        cnt = all_text.count(kw)
        if cnt > 0:
            c[kw.replace(" ", "")] += cnt
    for tok in re.findall(r"[가-힣]{2,5}", all_text):
        if tok in STOPWORDS:
            continue
        if any(tok.endswith(e) for e in _BAD_ENDINGS):
            continue
        c[tok] += 1
    return Counter({k: v for k, v in c.items() if v >= 2})


def extract_keywords(reviews: list, sentiment_results: list, top_n: int = 10) -> dict:
    pos_texts = [
        reviews[i]
        for i, r in enumerate(sentiment_results)
        if r["label"] == "긍정" and i < len(reviews)
    ]
    neg_texts = [
        reviews[i]
        for i, r in enumerate(sentiment_results)
        if r["label"] == "부정" and i < len(reviews)
    ]

    def _top(counter: Counter) -> list:
        return counter.most_common(top_n) or [("데이터 부족", 0)]

    return {
        "positive": _top(_extract_counter(pos_texts)),
        "negative": _top(_extract_counter(neg_texts)),
        "all":      _top(_extract_counter(reviews)),
    }


# ══════════════════════════════════════════════════════════
# 4. 복합 총평 생성
# ══════════════════════════════════════════════════════════

def generate_summary(reviews: list, sentiment_results: list, keyword_data: dict) -> dict:
    total = len(sentiment_results)
    if total == 0:
        return {
            "composite": "분석 데이터가 없습니다.",
            "headline":  "데이터 없음",
            "points":    [],
            "avg_score": 0.5,
            "pos_ratio": 0.0,
            "neu_ratio": 0.0,
            "neg_ratio": 0.0,
        }

    pos_cnt   = sum(1 for r in sentiment_results if r["label"] == "긍정")
    neu_cnt   = sum(1 for r in sentiment_results if r["label"] == "중립")
    neg_cnt   = total - pos_cnt - neu_cnt
    avg_score = sum(r["score"] for r in sentiment_results) / total
    pos_r, neu_r, neg_r = pos_cnt / total, neu_cnt / total, neg_cnt / total

    all_kws = [k for k, _ in keyword_data.get("all",      [])]
    pos_kws = [k for k, _ in keyword_data.get("positive", [])]
    neg_kws = [k for k, _ in keyword_data.get("negative", [])]

    def has(*patterns: str, src: str = "all") -> bool:
        kw_src = {"all": all_kws, "pos": pos_kws, "neg": neg_kws}[src]
        return any(
            any(p in kw for kw in kw_src)
            or any(p in rv for rv in reviews[:60])
            for p in patterns
        )

    pos_phrases: list[str] = []
    if has("맛있", "존맛", "개맛", src="pos"): pos_phrases.append("맛이 뛰어남")
    if has("양많", "푸짐",         src="pos"): pos_phrases.append("양이 푸짐함")
    if has("빠른", "빨리",         src="pos"): pos_phrases.append("배달이 빠름")
    if has("친절",                 src="pos"): pos_phrases.append("사장님이 친절함")
    if has("가성비",               src="pos"): pos_phrases.append("가성비가 훌륭함")
    if has("신선",                 src="pos"): pos_phrases.append("재료가 신선함")
    if has("재주문", "강추",       src="pos"): pos_phrases.append("재주문 의사 다수")
    if has("깔끔", "포장",         src="pos"): pos_phrases.append("포장이 깔끔함")
    if has("고소", "담백", "얼큰", src="pos"): pos_phrases.append("맛의 풍미가 좋음")

    neg_phrases: list[str] = []
    if has("느린", "늦게",         src="neg"): neg_phrases.append("배달이 느린 편")
    if has("별로", "실망", "맛없", "노맛", src="neg"): neg_phrases.append("맛이 기대 이하")
    if has("짜다", "간세",         src="neg"): neg_phrases.append("간이 세다는 의견")
    if has("양적", "양이적",       src="neg"): neg_phrases.append("양이 적은 편")
    if has("식어", "식었",         src="neg"): neg_phrases.append("음식이 식어 도착")
    if has("비싸",                 src="neg"): neg_phrases.append("가격이 아쉬움")
    if has("불친절",               src="neg"): neg_phrases.append("불친절 사례 있음")
    if has("포장", "이물",         src="neg"): neg_phrases.append("포장·위생 지적 있음")
    if has("딱딱", "퍽퍽",         src="neg"): neg_phrases.append("식감이 좋지 않다는 의견")

    if pos_phrases and neg_phrases:
        pos_str = ", ".join(pos_phrases[:2])
        neg_str = neg_phrases[0]
        composite = f"{pos_str}는 점은 좋지만, {neg_str}는 점은 아쉬움"
    elif pos_phrases and avg_score >= 0.62:
        pos_str = " · ".join(pos_phrases[:3])
        composite = f"전반적으로 {pos_str}해서 만족스러운 집"
    elif neg_phrases and avg_score < 0.45:
        neg_str = " · ".join(neg_phrases[:2])
        composite = f"{neg_str}는 점이 아쉬워 개선이 필요한 상황"
    elif avg_score >= 0.55:
        composite = "전반적으로 만족도가 높으며 재방문 의사가 있는 고객이 많음"
    elif avg_score >= 0.45:
        composite = "긍정과 부정이 혼재하며 맛은 평범한 수준으로 의견이 엇갈림"
    else:
        composite = "전반적인 만족도가 낮으며 여러 부분에서 개선이 요구됨"

    if avg_score >= 0.75:
        headline = (
            f"{pos_phrases[0]}는 등 높은 만족도"
            if pos_phrases else "대다수 고객이 매우 만족하는 음식점"
        )
    elif avg_score >= 0.62:
        headline = (
            f"{pos_phrases[0].rstrip('음')}으나, {neg_phrases[0]}"
            if pos_phrases and neg_phrases
            else (f"{pos_phrases[0]}는 등 긍정 평가 우세" if pos_phrases
                  else "전반적으로 무난하나 개선 여지 있음")
        )
    elif avg_score >= 0.50:
        headline = (
            f"{pos_phrases[0].rstrip('음')}지만, {neg_phrases[0]}"
            if pos_phrases and neg_phrases
            else "긍정·부정 의견이 고르게 분포"
        )
    elif avg_score >= 0.38:
        headline = (
            f"{neg_phrases[0]}는 등 개선 필요"
            if neg_phrases else "전반적 만족도가 다소 낮음"
        )
    else:
        headline = (
            f"{neg_phrases[0]}는 등 부정 평가 우세"
            if neg_phrases else "대다수 고객이 불만족"
        )

    points = (
        [{"text": p, "tone": "pos"} for p in pos_phrases[:3]] +
        [{"text": p, "tone": "neg"} for p in neg_phrases[:3]]
    )
    if not points:
        points = [{"text": "리뷰 데이터가 부족해 상세 분석이 어렵습니다.", "tone": "neu"}]

    return {
        "composite": composite,
        "headline":  headline,
        "points":    points,
        "avg_score": round(avg_score, 3),
        "pos_ratio": round(pos_r, 3),
        "neu_ratio": round(neu_r, 3),
        "neg_ratio": round(neg_r, 3),
    }


# ══════════════════════════════════════════════════════════
# 5. 차트 유틸
# ══════════════════════════════════════════════════════════

def _setup_font() -> None:
    for font in ["NanumGothic", "Malgun Gothic", "AppleGothic", "DejaVu Sans"]:
        try:
            plt.rcParams["font.family"]        = font
            plt.rcParams["axes.unicode_minus"] = False
            return
        except Exception:
            continue


def chart_donut(pos_r: float, neu_r: float, neg_r: float):
    _setup_font()
    fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor="none")
    ax.set_facecolor("none")
    raw   = [(pos_r, "#38ef7d", "긍정"), (neu_r, "#ffd200", "중립"), (neg_r, "#f44336", "부정")]
    fdata = [(s, c, l) for s, c, l in raw if s > 0] or [(1, "#444", "없음")]
    sizes, colors, labels = zip(*fdata)
    _, _, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.0f%%",
        colors=colors, startangle=90,
        wedgeprops=dict(width=0.52, edgecolor="#1a1a2e", linewidth=2),
        textprops=dict(color="white", fontsize=10),
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight("bold")
        at.set_color("white")
    ax.set_title("감정 분포", color="white", fontsize=11, pad=10)
    plt.tight_layout()
    return fig


def chart_hist(scores: list):
    _setup_font()
    fig, ax = plt.subplots(figsize=(6, 2.6), facecolor="none")
    ax.set_facecolor("none")
    ax.hist(scores, bins=20, range=(0, 1),
            color="#ffd200", alpha=0.72, edgecolor="#1a1a2e")
    ax.axvline(0.40, color="#f44336", linestyle="--", linewidth=1.3, label="부정 경계")
    ax.axvline(0.55, color="#38ef7d", linestyle="--", linewidth=1.3, label="긍정 경계")
    ax.set_xlabel("감정 점수 (0=부정 ↔ 1=긍정)", color="#888", fontsize=8)
    ax.set_ylabel("리뷰 수", color="#888", fontsize=8)
    ax.tick_params(colors="white", labelsize=8)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#333")
    ax.spines["left"].set_color("#333")
    ax.legend(fontsize=8, facecolor="#1a1a2e", edgecolor="#444", labelcolor="white")
    plt.tight_layout()
    return fig


def chart_bar(kw_pairs: list, color: str = "#ffd200"):
    if not kw_pairs or kw_pairs[0][1] == 0:
        return None
    _setup_font()
    labels = [k for k, _ in kw_pairs[:8]]
    values = [v for _, v in kw_pairs[:8]]
    fig, ax = plt.subplots(
        figsize=(6, max(2.5, len(labels) * 0.40)), facecolor="none"
    )
    ax.set_facecolor("none")
    bars = ax.barh(labels[::-1], values[::-1],
                   color=color, alpha=0.82, height=0.55, edgecolor="none")
    for bar, val in zip(bars, values[::-1]):
        ax.text(
            val + 0.08,
            bar.get_y() + bar.get_height() / 2,
            str(val),
            va="center", color="white", fontsize=8.5,
        )
    ax.set_xlabel("등장 횟수", color="#888", fontsize=8)
    ax.tick_params(colors="white", labelsize=8.5)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#333")
    ax.spines["left"].set_color("#333")
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════
# 6. CSV 로더 — 컬럼 자동 감지 + 인코딩 자동 시도
# ══════════════════════════════════════════════════════════

_KNOWN_COLS: list[str] = [
    "review", "comment", "내용", "댓글", "리뷰", "Review", "Comment",
    "text", "Text", "본문", "후기", "평가",
]


def _try_read_csv(source) -> pd.DataFrame | None:
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr", "latin1"):
        try:
            if isinstance(source, str):
                return pd.read_csv(source, encoding=enc)
            else:
                source.seek(0)
                return pd.read_csv(source, encoding=enc)
        except Exception:
            continue
    return None


def _detect_review_column(df: pd.DataFrame) -> str | None:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in _KNOWN_COLS:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]

    str_cols = df.select_dtypes(include="object").columns.tolist()
    if not str_cols:
        return None

    def _korean_ratio(col: str) -> float:
        sample = df[col].dropna().astype(str).head(30).str.cat(sep=" ")
        total  = len(sample)
        if total == 0:
            return 0.0
        kor = len(re.findall(r"[가-힣]", sample))
        return kor / total

    ratios = {col: _korean_ratio(col) for col in str_cols}
    best   = max(ratios, key=ratios.get)
    if ratios[best] >= 0.10:
        return best

    avg_lens = {col: df[col].dropna().astype(str).str.len().mean() for col in str_cols}
    return max(avg_lens, key=avg_lens.get)


def load_reviews_from_df(df: pd.DataFrame) -> tuple:
    col = _detect_review_column(df)
    if col is None:
        return [], ""
    reviews = [str(r).strip() for r in df[col].dropna() if str(r).strip()]
    return reviews, col


# ══════════════════════════════════════════════════════════
# 7. 네이버 플레이스 크롤링
# ══════════════════════════════════════════════════════════

def crawl_naver_reviews(store_name: str, max_reviews: int = 60) -> list:
    try:
        from selenium import webdriver as wd
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import (
            TimeoutException, NoSuchElementException, StaleElementReferenceException,
        )
        from webdriver_manager.chrome import ChromeDriverManager
        from urllib.parse import quote
    except ImportError:
        st.error("❌ Selenium 패키지가 없습니다.\n\n`pip install selenium webdriver-manager` 를 실행 후 재시작해주세요.")
        return []

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    reviews: list[str] = []
    driver = None

    with st.status(f"🕷️ '{store_name}' 리뷰 크롤링 중...", expanded=True) as status_ctx:
        try:
            status_ctx.write("🌐 Chrome 드라이버 초기화 중...")
            driver = wd.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"},
            )
            WAIT_S = WebDriverWait(driver, 12)
            WAIT_L = WebDriverWait(driver, 20)

            search_url = f"https://map.naver.com/v5/search/{quote(store_name)}"
            status_ctx.write(f"🗺️ 네이버 지도 검색 중: '{store_name}'")
            driver.get(search_url)
            time.sleep(random.uniform(2.5, 3.5))

            try:
                status_ctx.write("📦 검색 결과 iframe 진입 중...")
                search_frame = WAIT_L.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe")))
                driver.switch_to.frame(search_frame)
                time.sleep(1.2)
                first_item = WAIT_S.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.UEzoS, .Ryr1F li:first-child, li[data-laim-exp-id]")))
                item_name = ""
                try:
                    item_name = first_item.find_element(By.CSS_SELECTOR, "span.TYaxT, .place_bluelink").text
                except Exception:
                    pass
                status_ctx.write(f"📍 업체 선택: {item_name or '첫 번째 결과'}")
                first_item.click()
                time.sleep(random.uniform(1.8, 2.8))
            except Exception:
                status_ctx.write("⚠️ 검색 결과 iframe 탐지 실패 — 직접 URL 시도")
                driver.switch_to.default_content()

            driver.switch_to.default_content()
            time.sleep(1.0)

            try:
                status_ctx.write("📄 업체 상세 페이지 iframe 진입 중...")
                entry_frame = WAIT_L.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#entryIframe")))
                driver.switch_to.frame(entry_frame)
                status_ctx.write("✅ 업체 상세 페이지 접속 완료")
                time.sleep(random.uniform(1.5, 2.2))
            except Exception:
                status_ctx.write("ℹ️ entryIframe 없음 — 현재 페이지에서 계속 진행")

            tab_clicked = False
            for sel in ["a[href*='review']", "span.veBoZ", "li.lI3Eo a", ".zD5Nm a", "a.tpj9w", ".lnJFt a"]:
                try:
                    tabs = driver.find_elements(By.CSS_SELECTOR, sel)
                    for tab in tabs:
                        if "리뷰" in (tab.text or ""):
                            driver.execute_script("arguments[0].click();", tab)
                            tab_clicked = True
                            time.sleep(random.uniform(1.5, 2.5))
                            break
                    if tab_clicked:
                        break
                except Exception:
                    continue

            review_sels  = ["div.pui__vn15t2", "span.zPfVt", "div.YEtWT span", ".ReviewItem__reviewContent", "p.v7qLN", ".SDXc6", ".zss8e"]
            more_btn_sels = ["a.fvwqf", "div.PGaUy button", "button.hNDfs", "a[class*='more']", ".TeItC a"]

            for attempt in range(25):
                for sel in review_sels:
                    try:
                        for el in driver.find_elements(By.CSS_SELECTOR, sel):
                            try:
                                text = el.text.strip()
                            except Exception:
                                continue
                            if text and len(text) >= 10 and re.search(r"[가-힣]", text) and text not in reviews:
                                reviews.append(text)
                    except Exception:
                        continue

                status_ctx.write(f"🔄 수집 중... {len(reviews)}/{max_reviews}개 (시도 {attempt+1}/25)")
                if len(reviews) >= max_reviews:
                    break

                clicked = False
                for sel in more_btn_sels:
                    try:
                        btn = WAIT_S.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                        driver.execute_script("arguments[0].click();", btn)
                        clicked = True
                        time.sleep(random.uniform(1.2, 2.0))
                        break
                    except Exception:
                        continue

                if not clicked:
                    driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(random.uniform(1.0, 1.6))

            driver.quit()
            driver = None
            reviews = list(dict.fromkeys(reviews))[:max_reviews]

            if reviews:
                status_ctx.update(label=f"✅ '{store_name}' 리뷰 {len(reviews)}개 수집 완료!", state="complete", expanded=False)
            else:
                status_ctx.update(label="❌ 리뷰 수집 실패", state="error", expanded=True)
                st.error("리뷰를 찾지 못했습니다.\n\n• 가게 이름이 네이버 지도에 정확히 등록되어 있는지 확인하세요.\n• 방문자 리뷰가 최소 10개 이상 있어야 합니다.")

        except Exception as exc:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            status_ctx.update(label="❌ 크롤링 오류", state="error", expanded=True)
            st.error(f"크롤링 중 오류 발생: {exc}")

    return reviews


# ══════════════════════════════════════════════════════════
# 8. 결과 렌더링
# ══════════════════════════════════════════════════════════

def render_results(reviews: list, sentiment_results: list, keyword_data: dict, summary: dict, source_label: str = "") -> None:
    total  = len(reviews)
    pos_r  = summary["pos_ratio"]
    neu_r  = summary["neu_ratio"]
    neg_r  = summary["neg_ratio"]
    avg_sc = summary["avg_score"]

    if source_label:
        st.markdown(f'<div style="text-align:center;color:#666;font-size:0.8rem;margin-bottom:1rem;">📊 {source_label}</div>', unsafe_allow_html=True)

    # ── [A] 복합 총평 ──
    st.markdown('<div class="card"><div class="card-title">🏪 먹픽 AI 총평</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="composite-box">{summary["composite"]}</div>', unsafe_allow_html=True)
    for pt in summary["points"]:
        dot_color = {"pos": "#38ef7d", "neg": "#f44336", "neu": "#ffd200"}.get(pt["tone"], "#888")
        st.markdown(
            f'<div class="summary-point">'
            f'<div class="summary-dot" style="background:{dot_color};"></div>'
            f'<span>{pt["text"]}</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── [B] 핵심 지표 ──
    st.markdown('<div class="card"><div class="card-title">📊 핵심 지표</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, color in [
        (c1, "총 리뷰",    f"{total}개",          "#ffd200"),
        (c2, "긍정",       f"{pos_r*100:.0f}%",   "#38ef7d"),
        (c3, "중립",       f"{neu_r*100:.0f}%",   "#ffd200"),
        (c4, "부정",       f"{neg_r*100:.0f}%",   "#f44336"),
        (c5, "평균 점수",  f"{avg_sc:.3f}",        "#a78bfa"),
    ]:
        col.markdown(
            f'<div style="text-align:center;">'
            f'<div class="stat-number" style="color:{color};">{val}</div>'
            f'<div class="stat-label">{label}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── [C] 차트 ──
    st.markdown('<div class="card"><div class="card-title">📈 감정 분포 차트</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns([1, 2])
    with ch1:
        st.pyplot(chart_donut(pos_r, neu_r, neg_r))
    with ch2:
        scores_list = [r["score"] for r in sentiment_results]
        st.pyplot(chart_hist(scores_list))
    st.markdown("</div>", unsafe_allow_html=True)

    # ── [D] 키워드 ──
    st.markdown('<div class="card"><div class="card-title">🔑 키워드 분석</div>', unsafe_allow_html=True)
    kc1, kc2 = st.columns(2)
    for col, title, key, color, css in [
        (kc1, "👍 긍정 키워드", "positive", "#38ef7d", "kw-pos"),
        (kc2, "👎 부정 키워드", "negative", "#f44336", "kw-neg"),
    ]:
        with col:
            col.markdown(f"**{title}**")
            fig = chart_bar(keyword_data.get(key, []), color=color)
            if fig:
                col.pyplot(fig)
            tags_html = "".join(
                f'<span class="kw-tag {css}">{k} <b>{v}</b></span>'
                for k, v in keyword_data.get(key, [])[:8]
                if v > 0
            )
            col.markdown(f'<div class="kw-wrap">{tags_html}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── [E] 리뷰 샘플 ──
    pos_rv = [reviews[i] for i, r in enumerate(sentiment_results) if r["label"] == "긍정"]
    neg_rv = [reviews[i] for i, r in enumerate(sentiment_results) if r["label"] == "부정"]
    neu_rv = [reviews[i] for i, r in enumerate(sentiment_results) if r["label"] == "중립"]

    if pos_rv or neg_rv:
        st.markdown('<div class="card"><div class="card-title">💬 리뷰 샘플</div>', unsafe_allow_html=True)
        rc1, rc2 = st.columns(2)
        for col, rv_list, css, empty_msg in [
            (rc1, pos_rv, "review-pos", "긍정 리뷰 없음"),
            (rc2, neg_rv, "review-neg", "부정 리뷰 없음"),
        ]:
            col.markdown(f'<div class="card-title">{"👍 긍정" if css == "review-pos" else "👎 부정"}</div>', unsafe_allow_html=True)
            if rv_list:
                for rv in rv_list[:3]:
                    disp = rv[:130] + "..." if len(rv) > 130 else rv
                    col.markdown(f'<div class="review-sample {css}">"{disp}"</div>', unsafe_allow_html=True)
            else:
                col.markdown(f'<div style="color:#555">{empty_msg}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if neu_rv:
        st.markdown('<div class="card"><div class="card-title" style="color:#ffd200">😐 중립 리뷰 샘플</div>', unsafe_allow_html=True)
        for rv in neu_rv[:2]:
            disp = rv[:130] + "..." if len(rv) > 130 else rv
            st.markdown(f'<div class="review-sample review-neu">"{disp}"</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── [F] 전체 데이터 ──
    with st.expander("📄 전체 분석 결과 데이터 보기"):
        result_df = pd.DataFrame({
            "리뷰":  reviews,
            "감정": [r["label"] for r in sentiment_results],
            "점수": [r["score"] for r in sentiment_results],
        })
        st.dataframe(result_df, use_container_width=True)
        csv_bytes = result_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 결과 CSV 다운로드", csv_bytes, "mukpick_result.csv", "text/csv")


# ══════════════════════════════════════════════════════════
# 9. 분석 파이프라인 실행
# ══════════════════════════════════════════════════════════

def run_analysis(reviews: list, source_label: str = "") -> None:
    if not reviews:
        st.warning("⚠️ 분석할 리뷰가 없습니다.")
        return

    with st.spinner("🤖 AI 모델 로딩 중... (최초 실행 시 다소 시간이 걸립니다)"):
        model, model_type = load_sentiment_model()

    with st.spinner("📊 감정 분석 중..."):
        sentiment_results = analyze_sentiment(reviews, model, model_type)

    with st.spinner("🔑 키워드 추출 중..."):
        keyword_data = extract_keywords(reviews, sentiment_results, top_n=10)

    with st.spinner("✍️ 복합 총평 생성 중..."):
        summary = generate_summary(reviews, sentiment_results, keyword_data)

    render_results(reviews, sentiment_results, keyword_data, summary, source_label)


# ══════════════════════════════════════════════════════════
# 10. 메인 앱
# ══════════════════════════════════════════════════════════

def main() -> None:

    # ── 헤더 ──
    st.markdown('<div class="main-title">🍔 먹픽(muk pick!)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">AI가 리뷰를 분석해 맛집 인사이트를 제공합니다</div>', unsafe_allow_html=True)
    st.markdown('<div class="version-badge"><span>✦ AI EDITION</span></div>', unsafe_allow_html=True)
    st.markdown("---")

    # ── 입력 방식 선택 ──
    st.markdown("### 📥 입력 방식 선택")
    mode = st.radio(
        label="입력 방식",
        options=["✏️ 직접 입력", "📋 샘플 데이터", "📂 CSV 파일 업로드", "🔍 네이버 플레이스 크롤링"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.markdown("---")

    # ══════════════════════════════════════════════════════
    # 모드 A: 직접 입력 (MUKPICK 기능)
    # ══════════════════════════════════════════════════════
    if "직접 입력" in mode:
        st.markdown(
            '<div class="card" style="border-color:rgba(255,210,0,0.18);">'
            '<div class="card-title">✏️ 직접 입력 모드</div>'
            '<div style="color:#aaa;font-size:0.9rem;">리뷰를 줄바꿈으로 구분해 입력해주세요.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        user_input = st.text_area("리뷰 입력 (줄바꿈으로 구분)", height=200, label_visibility="collapsed", placeholder="예) 진짜 맛있어요!\n배달이 너무 늦어요\n노맛임 다시는 안 시킴")
        reviews = [r.strip() for r in user_input.split("\n") if r.strip()] if user_input else []
        if st.button("🚀 AI 분석 시작", key="direct_btn"):
            if not reviews:
                st.warning("리뷰를 입력해주세요!")
            else:
                run_analysis(reviews, source_label=f"직접 입력 · {len(reviews)}개")

    # ══════════════════════════════════════════════════════
    # 모드 B: 샘플 데이터 (MUKPICK 기능)
    # ══════════════════════════════════════════════════════
    elif "샘플 데이터" in mode:
        sample_reviews = [
            "진짜 맛있어요! 또 시킬게요",
            "배달이 너무 늦어요",
            "맛은 있는데 양이 적어요",
            "완전 최고입니다",
            "별로에요 다시는 안 시킴",
            "배달 빠르고 음식 따뜻함",
            "노맛임 돈 아까워요",
            "존맛 강추합니다!",
            "불친절하고 음식도 식어서 왔어요",
            "가성비 최고 재주문 확정",
        ]
        st.markdown('<div class="card"><div class="card-title">📋 샘플 데이터</div>', unsafe_allow_html=True)
        for rv in sample_reviews:
            st.markdown(f'<div class="review-sample review-neu">"{rv}"</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🚀 샘플 데이터 분석 시작", key="sample_btn"):
            run_analysis(sample_reviews, source_label=f"샘플 데이터 · {len(sample_reviews)}개")

    # ══════════════════════════════════════════════════════
    # 모드 C: CSV 파일 업로드 (realapp 기능)
    # ══════════════════════════════════════════════════════
    elif "CSV" in mode:
        st.markdown(
            """
            <div class="card" style="border-color:rgba(255,210,0,0.18);">
                <div class="card-title">📂 CSV 업로드 모드</div>
                <div style="color:#aaa;font-size:0.9rem;line-height:1.9;">
                    CSV 파일을 업로드하면 AI가 리뷰 컬럼을 <b style="color:#ffd200">자동 감지</b>합니다.<br>
                    <b style="color:#ffd200">인코딩 자동 감지:</b> UTF-8-sig · CP949 · Latin1 순으로 시도
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_up, col_btn = st.columns([3, 1])
        with col_up:
            uploaded_file = st.file_uploader(label="리뷰 CSV 파일 업로드", type=["csv"], help="review / comment / 내용 / 댓글 등 컬럼 자동 인식", label_visibility="collapsed")
            st.markdown('<div class="upload-hint">인식 가능 컬럼: <b>review · comment · 내용 · 댓글</b> 등</div>', unsafe_allow_html=True)
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            run_btn = st.button("🚀 분석 시작", use_container_width=True, key="csv_btn")

        if uploaded_file and run_btn:
            with st.spinner("📂 파일 읽는 중..."):
                df = _try_read_csv(uploaded_file)
            if df is None:
                st.error("❌ 파일을 읽지 못했습니다. UTF-8(BOM 포함)으로 저장 후 다시 시도해주세요.")
                return
            reviews, col_used = load_reviews_from_df(df)
            if not reviews:
                st.error(f"❌ 리뷰 컬럼을 찾지 못했습니다.\n\n현재 컬럼: **{', '.join(df.columns.tolist())}**")
                return
            st.success(f"✅ `{uploaded_file.name}` — **{col_used}** 컬럼 · {len(reviews)}개 리뷰 로드 완료")
            run_analysis(reviews, source_label=f"{uploaded_file.name} · [{col_used}] · {len(reviews)}개")
        elif not uploaded_file:
            st.markdown(
                '<div class="card" style="text-align:center;padding:3rem;">'
                '<div style="font-size:3.5rem">📂</div>'
                '<div style="color:#777;margin-top:1rem;">CSV 파일을 업로드하고 <b style="color:#ffd200">분석 시작</b>을 눌러주세요</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    # ══════════════════════════════════════════════════════
    # 모드 D: 네이버 플레이스 크롤링 (realapp 기능)
    # ══════════════════════════════════════════════════════
    else:
        st.markdown(
            """
            <div class="card" style="border-color:rgba(255,210,0,0.18);">
                <div class="card-title">🔍 네이버 플레이스 크롤링 모드</div>
                <div style="color:#aaa;font-size:0.9rem;line-height:1.9;">
                    가게 이름을 입력하면 네이버 플레이스 방문자 리뷰를 자동 수집합니다.<br>
                    <span style="color:#f44336;font-size:0.82rem;">⚠️ Chrome 및 <code>selenium</code>, <code>webdriver-manager</code> 필요</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_name, col_cnt = st.columns([2, 1])
        with col_name:
            store_name = st.text_input(label="가게 이름 입력", placeholder="예: 맥도날드 강남점, 피자헛 홍대점", label_visibility="collapsed")
        with col_cnt:
            max_cnt = st.slider(label="최대 수집 개수", min_value=20, max_value=100, value=60, step=10, label_visibility="visible")

        if st.button("🕷️ 크롤링 + 분석 시작", key="crawl_btn"):
            if not store_name.strip():
                st.warning("⚠️ 가게 이름을 입력해주세요.")
            else:
                reviews = crawl_naver_reviews(store_name.strip(), max_reviews=max_cnt)
                if reviews:
                    run_analysis(reviews, source_label=f"네이버 플레이스 · {store_name.strip()} · {len(reviews)}개")

    # ── 푸터 ──
    st.markdown(
        '<br><br><div style="text-align:center;color:#2a2a4a;font-size:0.78rem;">'
        '🍔 먹픽(muk pick!) · HuggingFace Transformers + Streamlit</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()