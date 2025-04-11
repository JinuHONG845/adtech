import streamlit as st
from openai import OpenAI
import google.generativeai as genai
import requests
import json
import time

# Set page config
st.set_page_config(
    page_title="AI 기반 매체 컨설팅",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
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
    .step-container {
        background-color: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 2px 0 rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #f1f8ff;
        padding: 1rem;
        border-radius: 4px;
        border-left: 4px solid #1a73e8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Title
st.title("🎯 AI 기반 매체 컨설팅")

# Progress bar
progress_text = "분석 진행률"
if st.session_state.current_step == 1:
    progress = 0
elif st.session_state.current_step == 2:
    progress = 50
else:
    progress = 100
progress_bar = st.progress(progress)

# Step 1: Campaign Information
if st.session_state.current_step == 1:
    with st.container():
        st.markdown("### Step 1: 캠페인 정보 입력")
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
                
                submitted = st.form_submit_button("다음 단계로")
                
                if submitted:
                    if not brand_name or not brand_description or not content_goal:
                        st.error("모든 필드를 입력해주세요.")
                    else:
                        st.session_state.campaign_info = {
                            "brand_name": brand_name,
                            "brand_description": brand_description,
                            "content_goal": content_goal
                        }
                        st.session_state.current_step = 2
                        st.rerun()
        
        with col2:
            st.info("""
            💡 **입력 가이드**
            
            - 브랜드의 핵심 가치와 차별점을 명확히 설명해주세요
            - 구체적인 마케팅 목표를 설정해주세요
            - 타겟 고객층이 있다면 함께 기재해주세요
            """)

# Step 2: AI Model Selection and Analysis
elif st.session_state.current_step == 2:
    with st.container():
        st.markdown("### Step 2: AI 분석 모델 선택")
        st.markdown("분석에 사용할 AI 모델을 선택하고 분석을 시작하세요.")
        
        col1, col2 = st.columns([2,1])
        with col1:
            selected_models = st.multiselect(
                "사용할 AI 모델을 선택하세요",
                ["GPT-4", "Gemini"],
                default=["GPT-4"],
                help="여러 모델을 선택하여 결과를 비교할 수 있습니다."
            )
            
            if st.button("분석 시작"):
                if not selected_models:
                    st.error("최소 하나의 AI 모델을 선택해주세요.")
                else:
                    with st.spinner("AI 분석 진행 중..."):
                        # Create prompt
                        prompt = f"""
                        제품/브랜드: {st.session_state.campaign_info['brand_name']}
                        소개: {st.session_state.campaign_info['brand_description']}
                        목표: {st.session_state.campaign_info['content_goal']}

                        다음 사항들을 분석해주세요:
                        1. 검색광고와 디스플레이 광고 중 어떤 것이 더 적절한지 구체적인 이유와 함께 설명
                        2. 주요 매체별 비중 제안 (퍼센트로 표시)
                        3. 필요한 생성소재 개수와 종류
                        4. 업로드용 컨텐츠 제안 (실제 광고문구 예시 포함)
                        """

                        results = {}

                        # GPT-4
                        if "GPT-4" in selected_models:
                            try:
                                client = OpenAI()
                                client.api_key = st.secrets["OPENAI_API_KEY"]
                                response = client.chat.completions.create(
                                    model="gpt-4-turbo-preview",
                                    messages=[
                                        {"role": "system", "content": "당신은 광고 매체 전문가입니다."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    temperature=0.7
                                )
                                results["GPT-4"] = response.choices[0].message.content
                            except Exception as e:
                                st.error(f"GPT-4 오류: {str(e)}")

                        # Gemini
                        if "Gemini" in selected_models:
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
                                results["Gemini"] = response.text
                            except Exception as e:
                                st.error(f"Gemini 오류: {str(e)}")

                        st.session_state.results = results
                        st.session_state.current_step = 3
                        st.rerun()
        
        with col2:
            st.info("""
            💡 **AI 모델 특징**
            
            - **GPT-4**: 광범위한 마케팅 지식과 상세한 분석
            - **Gemini**: 최신 트렌드 반영과 창의적인 제안
            """)

# Step 3: Results
elif st.session_state.current_step == 3:
    with st.container():
        st.markdown("### Step 3: 분석 결과")
        st.markdown("AI가 제안하는 광고 전략을 확인하세요.")
        
        for model_name, result in st.session_state.results.items():
            with st.expander(f"📊 {model_name} 분석 결과", expanded=True):
                st.markdown(result)
        
        if st.button("새로운 분석 시작"):
            st.session_state.current_step = 1
            st.session_state.results = {}
            st.rerun()

# Footer
st.markdown("---")
st.markdown("© 2024 AI 기반 매체 컨설팅. All rights reserved.") 