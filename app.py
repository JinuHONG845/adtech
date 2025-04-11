import streamlit as st
import os
from openai import OpenAI
import google.generativeai as genai

# 페이지 설정
st.set_page_config(
    page_title="AI 기반 매체 컨설팅",
    page_icon="📊",
    layout="wide"
)

# 스타일 적용
st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    .stButton>button {
        width: 100%;
        background-color: #1a73e8;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    .stButton>button:hover {
        background-color: #1557b0;
    }
</style>
""", unsafe_allow_html=True)

# 타이틀
st.title("🎯 AI 기반 매체 컨설팅")

# 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = "input"
if "results" not in st.session_state:
    st.session_state.results = {}

# API 키 확인 함수
def has_valid_api_keys():
    try:
        return "OPENAI_API_KEY" in st.secrets and "GOOGLE_API_KEY" in st.secrets
    except:
        return False

# GPT-4 분석 함수
def get_gpt4_analysis(prompt):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "당신은 광고 매체 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"GPT-4 분석 오류: {str(e)}")
        return None

# Gemini 분석 함수
def get_gemini_analysis(prompt):
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
        )
        return response.text
    except Exception as e:
        st.error(f"Gemini 분석 오류: {str(e)}")
        return None

# API 키 유효성 확인
if not has_valid_api_keys():
    st.error("API 키가 설정되지 않았습니다. Streamlit secrets에 OPENAI_API_KEY와 GOOGLE_API_KEY를 설정해주세요.")
else:
    # 입력 단계
    if st.session_state.step == "input":
        st.markdown("### 캠페인 정보 입력")
        st.markdown("효과적인 광고 전략 수립을 위해 기본 정보를 입력해주세요.")
        
        col1, col2 = st.columns([2,1])
        with col1:
            with st.form("campaign_form"):
                brand_name = st.text_input("제품/브랜드 명", 
                    help="광고할 제품이나 브랜드의 이름을 입력하세요")
                brand_description = st.text_area("제품/브랜드 소개",
                    help="제품/브랜드의 주요 특징과 장점을 설명해주세요")
                content_goal = st.text_input("캠페인 목표",
                    help="예: 일간 Click수 100만건, 전환율 5% 달성 등")
                
                selected_models = st.multiselect(
                    "사용할 AI 모델을 선택하세요",
                    ["GPT-4", "Gemini"],
                    default=["GPT-4"]
                )
                
                submitted = st.form_submit_button("분석 시작")
                
                if submitted:
                    if not (brand_name and brand_description and content_goal and selected_models):
                        st.error("모든 필드를 입력해주세요.")
                    else:
                        with st.spinner("AI 분석 진행 중..."):
                            prompt = f"""
                            제품/브랜드: {brand_name}
                            소개: {brand_description}
                            목표: {content_goal}

                            다음 사항들을 분석해주세요:
                            1. 검색광고와 디스플레이 광고 중 어떤 것이 더 적절한지 구체적인 이유와 함께 설명
                            2. 주요 매체별 비중 제안 (퍼센트로 표시)
                            3. 필요한 생성소재 개수와 종류
                            4. 업로드용 컨텐츠 제안 (실제 광고문구 예시 포함)
                            """

                            results = {}

                            if "GPT-4" in selected_models:
                                gpt4_result = get_gpt4_analysis(prompt)
                                if gpt4_result:
                                    results["GPT-4"] = gpt4_result

                            if "Gemini" in selected_models:
                                gemini_result = get_gemini_analysis(prompt)
                                if gemini_result:
                                    results["Gemini"] = gemini_result

                            if results:
                                st.session_state.results = results
                                st.session_state.step = "results"
                                st.rerun()
        
        with col2:
            st.info("""
            💡 **입력 가이드**
            
            - 브랜드의 핵심 가치와 차별점을 명확히 설명해주세요
            - 구체적인 마케팅 목표를 설정해주세요
            - 타겟 고객층이 있다면 함께 기재해주세요
            """)

    # 결과 단계
    elif st.session_state.step == "results":
        st.markdown("### 분석 결과")
        st.markdown("AI가 제안하는 광고 전략을 확인하세요.")
        
        for model_name, result in st.session_state.results.items():
            with st.expander(f"📊 {model_name} 분석 결과", expanded=True):
                st.markdown(result)
        
        if st.button("새로운 분석 시작"):
            st.session_state.step = "input"
            st.session_state.results = {}
            st.rerun()

# 푸터
st.markdown("---")
st.markdown("© 2024 AI 기반 매체 컨설팅. All rights reserved.") 