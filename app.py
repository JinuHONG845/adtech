import streamlit as st
import google.generativeai as genai
import requests
import json

# Set page config
st.set_page_config(
    page_title="AI 기반 매체 컨설팅",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("AI 기반 매체 컨설팅")
st.markdown("""
이 앱은 AI를 활용하여 최적의 광고 매체 전략을 제안합니다.
제품/브랜드 정보를 입력하면 검색광고와 디스플레이 광고의 적절성을 분석하고,
주요 매체별 비중을 제안합니다.
""")

# Configure Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Sidebar for model selection
st.sidebar.title("LLM 선택")
selected_models = st.sidebar.multiselect(
    "사용할 AI 모델을 선택하세요",
    ["GPT-4", "Gemini"],
    default=["GPT-4"]
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

        # GPT-4
        if "GPT-4" in selected_models:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
                }
                
                payload = {
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {"role": "system", "content": "당신은 광고 매체 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    results["GPT-4"] = response_data["choices"][0]["message"]["content"]
                else:
                    st.error(f"GPT-4 오류: API 응답 코드 {response.status_code}")
                    
            except Exception as e:
                st.error(f"GPT-4 오류: {str(e)}")

        # Gemini
        if "Gemini" in selected_models:
            try:
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

        # Display results
        for model_name, result in results.items():
            with st.expander(f"{model_name} 분석 결과"):
                st.write(result)

# Add footer
st.markdown("---")
st.markdown("© 2024 AI 기반 매체 컨설팅. All rights reserved.") 