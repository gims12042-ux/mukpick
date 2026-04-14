import streamlit as st
import pandas as pd
from transformers import pipeline

st.set_page_config(page_title="먹픽(muk pick!)", layout="wide")
st.markdown("""
<h1 style='text-align: center;'>🍔먹픽 - 리뷰 AI 분석기</h1>
<p style='text-align: center;'>리뷰 데이터를 기반으로 감정 분석 + 요약을 제공합니다</p>
""", unsafe_allow_html=True)

@st.cache_resource
def load_sentiment_model():
    return pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment"
    )

sentiment_pipeline = load_sentiment_model()

# ✅ 부정 / 긍정 키워드 사전
NEGATIVE_KEYWORDS = [
    "노맛", "별로", "최악", "실망", "구림", "구려", "쓰레기",
    "노베", "별로임", "맛없", "안맛", "느림", "불친절", "다신안",
    "다시는", "환불", "토나", "역겨", "짜증", "후회", "별로예요",
    "별로에요", "노맛임", "맛이없", "맛도없", "최악이"
]

POSITIVE_KEYWORDS = [
    "노맛아님", "맛있", "최고", "굿", "존맛", "개맛있", "또올게",
    "강추", "추천", "빠름", "친절", "신선", "대박", "맛집", "완전맛",
    "또시킬", "최고예요", "맛있어요", "맛있었", "좋아요", "좋았"
]

def analyze_sentiment(review):
    # 부정 키워드 먼저 체크
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in review:
            return 1

    # 긍정 키워드 체크
    for keyword in POSITIVE_KEYWORDS:
        if keyword in review:
            return 5

    # 키워드 없으면 모델 결과 사용
    result = sentiment_pipeline(review)[0]
    return int(result['label'][0])

def summarize_reviews(reviews):
    if len(reviews) <= 2:
        return " | ".join(reviews)
    sorted_reviews = sorted(reviews, key=lambda x: len(x))
    top = sorted_reviews[:3]
    return " | ".join(top)

def get_rule_based_summary(scores):
    positive_count = len([s for s in scores if s >= 4])
    negative_count = len([s for s in scores if s <= 2])
    if negative_count > positive_count:
        return "부정적인 리뷰가 많으며 서비스 개선이 필요합니다.", positive_count, negative_count
    elif positive_count > negative_count:
        return "전반적으로 만족도가 높은 가게입니다.", positive_count, negative_count
    else:
        return "평가가 혼합된 가게입니다.", positive_count, negative_count

st.sidebar.header("📂 데이터 입력")
input_type = st.sidebar.radio(
    "입력 방식 선택",
    ["직접 입력", "샘플 데이터", "CSV 업로드"]
)

if input_type == "직접 입력":
    user_input = st.text_area("리뷰 입력 (줄바꿈으로 구분)")
    reviews = user_input.split("\n") if user_input else []
elif input_type == "샘플 데이터":
    reviews = [
        "진짜 맛있어요! 또 시킬게요",
        "배달이 너무 늦어요",
        "맛은 있는데 양이 적어요",
        "완전 최고입니다",
        "별로에요 다시는 안 시킴",
        "배달 빠르고 음식 따뜻함",
    ]
    st.write("샘플 리뷰:")
    st.write(reviews)
else:
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])
    reviews = []
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("업로드 데이터 미리보기:")
        st.dataframe(df.head())
        if "review" in df.columns:
            reviews = df["review"].dropna().tolist()
        else:
            st.error("CSV에 'review' 컬럼이 필요합니다")

if st.button("🚀 AI 분석 시작"):
    if len(reviews) == 0:
        st.warning("리뷰 데이터를 입력해주세요!")
    else:
        with st.spinner("AI 분석 중..."):
            scores = [analyze_sentiment(r) for r in reviews]
            avg_score = sum(scores) / len(scores)
            final_score = round(avg_score, 2)
            ai_summary = summarize_reviews(reviews)
            rule_summary, positive_count, negative_count = get_rule_based_summary(scores)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 AI 신뢰도 점수", f"{final_score} / 5")
        with col2:
            st.metric("📝 리뷰 개수", len(reviews))
        with col3:
            st.metric("👍 긍정 리뷰", positive_count)
        with col4:
            st.metric("👎 부정 리뷰", negative_count)

        st.subheader("🏪 가게 총평")
        st.info(rule_summary)

        st.subheader("💬 대표 리뷰 요약")
        st.success(ai_summary)

        result_df = pd.DataFrame({
            "리뷰": reviews,
            "점수": scores
        })
        st.subheader("📄 리뷰 분석 상세")
        st.dataframe(result_df)

        st.subheader("📈 감정 분포")
        score_label_map = {
            1: "😡 매우 부정",
            2: "😞 부정",
            3: "😐 보통",
            4: "😊 긍정",
            5: "🤩 매우 긍정"
        }
        chart_data = result_df["점수"].value_counts().sort_index()
        chart_data.index = [score_label_map.get(i, str(i)) for i in chart_data.index]
        st.bar_chart(chart_data)