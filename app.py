import streamlit as st
import openai
import anthropic
import google.generativeai as genai

# Set page config first
st.set_page_config(
    page_title="AI 기반 매체 컨설팅",
    page_icon="📊",
    layout="wide"
)

# Initialize API clients using Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
anthropic_client = anthropic.Client(api_key=st.secrets["ANTHROPIC_API_KEY"])
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Title and description
st.title("AI 기반 매체 컨설팅")
st.markdown("""
이 앱은 AI를 활용하여 최적의 광고 매체 전략을 제안합니다.
제품/브랜드 정보를 입력하면 검색광고와 디스플레이 광고의 적절성을 분석하고,
주요 매체별 비중을 제안합니다.
""")

# Sidebar for model selection
st.sidebar.title("LLM 선택")
selected_models = st.sidebar.multiselect(
    "사용할 AI 모델을 선택하세요",
    ["ChatGPT-4", "Claude-3.7", "Gemini Pro"],
    default=["ChatGPT-4"]
)

# Main input form
with st.form("input_form"):
    brand_name = st.text_input("제품/브랜드 명")
    brand_description = st.text_area("제품/브랜드 소개")
    content_goal = st.text_input("컨텐츠 목표 (예: 일간 Click수 100만건)")
    
    submitted = st.form_submit_button("분석 시작")

if submitted:
    if not brand_name or not brand_description or not content_goal:
        st.error("모든 필드를 입력해주세요.")
    else:
        # Create prompt
        prompt = f"""
        제품/브랜드: {brand_name}
        소개: {brand_description}
        목표: {content_goal}

        다음 사항들을 분석해주세요:
        1. 검색광고와 디스플레이 광고 중 어떤 것이 더 적절한지
        2. 주요 매체별 비중 제안
        3. 필요한 생성소재 개수
        4. 업로드용 컨텐츠 제안
        """

        # Initialize results container
        results = {}

        # ChatGPT-4
        if "ChatGPT-4" in selected_models:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "당신은 광고 매체 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ]
                )
                results["ChatGPT-4"] = response.choices[0].message.content
            except Exception as e:
                st.error(f"ChatGPT-4 오류: {str(e)}")

        # Claude-3.7
        if "Claude-3.7" in selected_models:
            try:
                response = anthropic_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                results["Claude-3.7"] = response.content
            except Exception as e:
                st.error(f"Claude-3.7 오류: {str(e)}")

        # Gemini Pro
        if "Gemini Pro" in selected_models:
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                results["Gemini Pro"] = response.text
            except Exception as e:
                st.error(f"Gemini Pro 오류: {str(e)}")

        # Display results
        for model_name, result in results.items():
            with st.expander(f"{model_name} 분석 결과"):
                st.write(result)

# Add footer
st.markdown("---")
st.markdown("© 2024 AI 기반 매체 컨설팅. All rights reserved.") 