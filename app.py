import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import random
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import time
import requests

# 페이지 설정
st.set_page_config(
    page_title="AI 기반 광고 컨설팅 플랫폼",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API 클라이언트 초기화
try:
    openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    anthropic_client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    deepseek_client = OpenAI(
        api_key=st.secrets["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com"
    )
    grok_client = OpenAI(
        api_key=st.secrets["GROK_API_KEY"],
        base_url="https://api.x.ai/v1"
    )
except Exception as e:
    st.error(f"API 클라이언트 초기화 중 오류가 발생했습니다: {str(e)}")

# CSS 스타일 적용 (Google Performance Max 스타일)
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        padding: 1rem;
    }
    .stButton>button {
        background-color: #1a73e8;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #1557b0;
    }
    .step-container {
        background-color: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
        margin-bottom: 1.5rem;
    }
    .header-title {
        color: #202124;
        font-size: 1.8rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    .subheader {
        color: #5f6368;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .result-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 500;
        color: #1a73e8;
    }
    .metric-label {
        color: #5f6368;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 초기 세션 상태 설정
if "step" not in st.session_state:
    st.session_state.step = 1
if "campaign_data" not in st.session_state:
    st.session_state.campaign_data = {
        "brand_name": "",
        "brand_description": "",
        "campaign_goal": "",
        "selected_models": []
    }
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "simulation_results" not in st.session_state:
    st.session_state.simulation_results = None

# 헤더 섹션
def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="header-title">AI 기반 광고 컨설팅 플랫폼</div>', unsafe_allow_html=True)
        st.markdown('<div class="subheader">최적의 매체 전략을 AI가 추천해 드립니다</div>', unsafe_allow_html=True)
    with col2:
        if st.session_state.step > 1:
            if st.button("처음으로 돌아가기"):
                st.session_state.step = 1
                st.session_state.campaign_data = {
                    "brand_name": "",
                    "brand_description": "",
                    "campaign_goal": "",
                    "selected_models": []
                }
                st.session_state.analysis_results = {}
                st.session_state.simulation_results = None
                st.rerun()

# 단계 표시 함수
def show_progress():
    if st.session_state.step == 1:
        steps = ["1️⃣ 캠페인 정보 입력", "2️⃣ AI 분석", "3️⃣ 시뮬레이션"]
    elif st.session_state.step == 2:
        steps = ["✅ 캠페인 정보 입력", "2️⃣ AI 분석", "3️⃣ 시뮬레이션"]
    else:
        steps = ["✅ 캠페인 정보 입력", "✅ AI 분석", "3️⃣ 시뮬레이션"]
    
    cols = st.columns(3)
    for i, step in enumerate(steps):
        with cols[i]:
            if i+1 < st.session_state.step:
                st.markdown(f"<div style='text-align: center; color: #1a73e8; font-weight: 500;'>{step}</div>", unsafe_allow_html=True)
            elif i+1 == st.session_state.step:
                st.markdown(f"<div style='text-align: center; color: #1a73e8; font-weight: 700;'>{step}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center; color: #5f6368;'>{step}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# AI 모델 호출 함수
def get_ai_analysis(prompt, model_name):
    try:
        if model_name == "ChatGPT":
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 광고 및 마케팅 전략 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        
        elif model_name == "Claude":
            response = anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.7,
                system="당신은 광고 및 마케팅 전략 전문가입니다.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        
        elif model_name == "Gemini":
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                )
            )
            return response.text
        
        elif model_name == "DeepSeek":
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "당신은 광고 및 마케팅 전략 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        
        elif model_name == "Grok":
            response = grok_client.chat.completions.create(
                model="grok-1",
                messages=[
                    {"role": "system", "content": "당신은 광고 및 마케팅 전략 전문가입니다. 독특하고 창의적인 시각으로 분석해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            return response.choices[0].message.content
    
    except Exception as e:
        st.error(f"{model_name} 모델 호출 중 오류가 발생했습니다: {str(e)}")
        return None

# 광고 분석 결과 처리 및 파싱
def parse_ad_recommendations(analysis_text):
    # 여기서는 분석 텍스트에서 핵심 정보만 추출하는 간단한 예시입니다.
    # 실제 구현에서는 LLM의 구조화된 출력이나 정규식을 사용할 수 있습니다.
    try:
        lines = analysis_text.strip().split('\n')
        
        # 기본값 설정
        ad_type = "균형적"
        media_distribution = {
            "Google": 25,
            "Meta": 25,
            "Naver": 20,
            "Kakao": 20,
            "TTD": 10
        }
        
        # 광고 유형 찾기 (검색 vs 디스플레이)
        for line in lines:
            if "검색광고" in line and "추천" in line:
                ad_type = "검색광고"
                break
            elif "디스플레이광고" in line and "추천" in line:
                ad_type = "디스플레이광고"
                break
        
        # 더 정교한 파싱 로직 구현 가능
        
        return {
            "ad_type": ad_type,
            "media_distribution": media_distribution
        }
    except Exception as e:
        st.error(f"분석 결과 파싱 중 오류 발생: {str(e)}")
        return {
            "ad_type": "균형적",
            "media_distribution": {
                "Google": 25,
                "Meta": 25,
                "Naver": 20,
                "Kakao": 20,
                "TTD": 10
            }
        }

# 시뮬레이션 결과 생성
def generate_simulation_results(campaign_data, ad_type):
    # 광고 유형에 따라 시뮬레이션 결과 조정
    if ad_type == "검색광고":
        base_ctr = 0.05  # 클릭률 (평균 5%)
        base_conversion = 0.04  # 전환율 (평균 4%)
        base_reach = 0.4  # 도달률 (40%)
    elif ad_type == "디스플레이광고":
        base_ctr = 0.02  # 클릭률 (평균 2%)
        base_conversion = 0.02  # 전환율 (평균 2%)
        base_reach = 0.7  # 도달률 (70%)
    else:
        base_ctr = 0.035  # 중간값
        base_conversion = 0.03  # 중간값
        base_reach = 0.55  # 중간값
    
    # 브랜드 설명 길이에 따른 조정 (더 자세한 설명 = 더 좋은 타겟팅)
    description_factor = min(1 + len(campaign_data["brand_description"]) / 1000, 1.2)
    
    # 임의성 추가
    random_factor = random.uniform(0.9, 1.1)
    
    # 시뮬레이션 기간 (주)
    weeks = 12
    
    # 주별 데이터 생성
    weekly_data = []
    impressions_base = 100000  # 주당 기본 노출수
    
    for week in range(1, weeks+1):
        # 시간에 따른 성장 모델링
        time_factor = 1 + 0.05 * (week - 1)  # 매주 5% 성능 향상
        if week > 8:  # 8주 이후 점차 정체
            time_factor = 1 + 0.05 * 7 + 0.02 * (week - 8)
        
        # 주요 지표 계산
        impressions = int(impressions_base * time_factor * random.uniform(0.95, 1.05))
        reach = base_reach * description_factor * time_factor * random.uniform(0.9, 1.1)
        ctr = base_ctr * description_factor * time_factor * random.uniform(0.85, 1.15)
        clicks = int(impressions * ctr)
        conversions = int(clicks * base_conversion * description_factor * random.uniform(0.9, 1.1))
        
        weekly_data.append({
            "week": week,
            "impressions": impressions,
            "reach": min(reach, 0.95),  # 도달률 최대 95%
            "clicks": clicks,
            "ctr": ctr,
            "conversions": conversions,
            "conversion_rate": conversions / clicks if clicks > 0 else 0
        })
    
    return weekly_data

# 단계 1: 캠페인 정보 입력 화면
def render_step_1():
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown("### 캠페인 정보 입력")
    st.markdown("효과적인 광고 전략 수립을 위해 아래 정보를 입력해주세요.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        with st.form("campaign_form"):
            brand_name = st.text_input("브랜드/제품명", 
                help="광고할 브랜드나 제품의 이름을 입력하세요")
            
            brand_description = st.text_area("브랜드 설명", 
                help="브랜드/제품의 특징, 타깃 고객층, 차별화 포인트 등을 자세히 설명해주세요")
            
            campaign_goal = st.text_input("캠페인 목표", 
                help="예: 브랜드 인지도 향상, 웹사이트 트래픽 증가, 전환율 개선 등")
            
            st.markdown("### 분석에 사용할 AI 모델")
            selected_models = st.multiselect(
                "하나 이상의 AI 모델을 선택하세요",
                ["ChatGPT", "Claude", "Gemini", "DeepSeek", "Grok"],
                default=["ChatGPT"]
            )
            
            submitted = st.form_submit_button("분석 시작")
            
            if submitted:
                if not brand_name or not brand_description or not campaign_goal or not selected_models:
                    st.error("모든 필드를 입력해주세요!")
                else:
                    # 데이터 저장 및 다음 단계로 이동
                    st.session_state.campaign_data = {
                        "brand_name": brand_name,
                        "brand_description": brand_description,
                        "campaign_goal": campaign_goal,
                        "selected_models": selected_models
                    }
                    st.session_state.step = 2
                    st.rerun()
    
    with col2:
        st.info("""
        💡 **입력 가이드**
        
        - 브랜드의 핵심 가치와 차별점을 명확히 설명해 주세요
        - 타겟 고객층이 있다면 함께 기재해 주세요
        - 구체적인 마케팅 목표를 설정해 주세요
        - 여러 AI 모델을 선택하면 다양한 시각의 분석을 받아볼 수 있습니다
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 단계 2: AI 분석 결과 화면
def render_step_2():
    campaign_data = st.session_state.campaign_data
    
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown("### AI 분석 중...")
    
    # 프롬프트 생성
    prompt = f"""
    다음 브랜드/제품에 대한 광고 전략을 분석해 주세요:
    
    브랜드/제품명: {campaign_data['brand_name']}
    브랜드 설명: {campaign_data['brand_description']}
    캠페인 목표: {campaign_data['campaign_goal']}
    
    다음 내용을 포함해 분석해 주세요:
    
    1. 검색광고와 디스플레이 광고 중 어떤 것이 더 적합한지 구체적인 이유와 함께 추천해 주세요.
    2. 주요 매체별 예산 배분 비율을 제안해 주세요 (Google, Meta, Naver, Kakao, TTD).
    3. 필요한 광고 소재 유형과 개수를 추천해 주세요.
    4. 효과적인 광고 문구 예시를 3개 이상 제공해 주세요.
    
    결과는 마케팅 초보자도 이해할 수 있도록 명확하게 설명해 주세요.
    """
    
    # 각 선택된 모델에 대해 분석 실행
    total_models = len(campaign_data["selected_models"])
    progress_bar = st.progress(0)
    analysis_results = {}
    
    for i, model_name in enumerate(campaign_data["selected_models"]):
        status_text = st.empty()
        status_text.text(f"{model_name} 모델이 분석 중입니다...")
        
        # AI 모델 호출
        result = get_ai_analysis(prompt, model_name)
        if result:
            analysis_results[model_name] = {
                "raw_text": result,
                "parsed_data": parse_ad_recommendations(result)
            }
        
        # 진행 상황 업데이트
        progress_bar.progress((i + 1) / total_models)
    
    st.session_state.analysis_results = analysis_results
    st.session_state.step = 3
    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# 단계 3: 분석 결과 및 시뮬레이션 화면
def render_step_3():
    if not st.session_state.analysis_results:
        st.error("분석 결과가 없습니다. 다시 시도해주세요.")
        if st.button("처음으로 돌아가기"):
            st.session_state.step = 1
            st.rerun()
        return

    campaign_data = st.session_state.campaign_data
    analysis_results = st.session_state.analysis_results
    
    # 결과 요약 섹션
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown("### 📊 AI 분석 결과")
    
    # 각 모델별 분석 탭 표시
    tabs = st.tabs([model_name for model_name in analysis_results.keys()])
    
    for i, model_name in enumerate(analysis_results.keys()):
        with tabs[i]:
            result = analysis_results[model_name]
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown("#### 전체 분석")
                st.markdown(result["raw_text"])
            
            with col2:
                st.markdown("#### 추천 광고 유형")
                st.info(f"**{result['parsed_data']['ad_type']}** 중심의 전략이 추천됩니다.")
                
                st.markdown("#### 매체별 예산 배분")
                media_data = pd.DataFrame({
                    '매체': list(result['parsed_data']['media_distribution'].keys()),
                    '비율(%)': list(result['parsed_data']['media_distribution'].values())
                })
                
                fig = px.pie(media_data, values='비율(%)', names='매체', 
                            color_discrete_sequence=px.colors.qualitative.Set2,
                            hole=0.4)
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 시뮬레이션 섹션
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown("### 📈 캠페인 시뮬레이션")
    
    # 시뮬레이션 실행 버튼
    if st.button("시뮬레이션 실행") or st.session_state.simulation_results:
        # 선택된 첫 번째 모델의 추천을 기반으로 시뮬레이션
        first_model = list(analysis_results.keys())[0]
        ad_type = analysis_results[first_model]["parsed_data"]["ad_type"]
        
        if not st.session_state.simulation_results:
            with st.spinner("시뮬레이션 데이터 생성 중..."):
                st.session_state.simulation_results = generate_simulation_results(campaign_data, ad_type)
        
        # 시뮬레이션 결과 표시
        sim_data = pd.DataFrame(st.session_state.simulation_results)
        
        # 주요 지표 요약
        total_impressions = sum(week["impressions"] for week in st.session_state.simulation_results)
        avg_ctr = sum(week["ctr"] for week in st.session_state.simulation_results) / len(st.session_state.simulation_results)
        total_conversions = sum(week["conversions"] for week in st.session_state.simulation_results)
        final_reach = st.session_state.simulation_results[-1]["reach"] * 100
        
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        with metrics_col1:
            st.metric("총 노출 수", f"{total_impressions:,}")
        with metrics_col2:
            st.metric("평균 클릭률", f"{avg_ctr:.2%}")
        with metrics_col3:
            st.metric("총 전환 수", f"{total_conversions:,}")
        with metrics_col4:
            st.metric("최종 도달률", f"{final_reach:.1f}%")
        
        # 추세 그래프
        st.markdown("#### 시간에 따른 성과 추이")
        tab1, tab2, tab3 = st.tabs(["클릭 및 전환", "도달률", "세부 데이터"])
        
        with tab1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sim_data['week'], 
                y=sim_data['clicks'],
                mode='lines+markers',
                name='클릭 수',
                marker=dict(color='#1a73e8')
            ))
            fig.add_trace(go.Scatter(
                x=sim_data['week'], 
                y=sim_data['conversions'],
                mode='lines+markers',
                name='전환 수',
                marker=dict(color='#ea4335')
            ))
            fig.update_layout(
                title='주간 클릭 및 전환 추이',
                xaxis_title='주차',
                yaxis_title='수치',
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sim_data['week'], 
                y=sim_data['reach']*100,
                mode='lines+markers',
                name='도달률',
                marker=dict(color='#34a853'),
                fill='tozeroy'
            ))
            fig.update_layout(
                title='주간 도달률 추이',
                xaxis_title='주차',
                yaxis_title='도달률 (%)',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.dataframe(
                sim_data.style
                .format({
                    'impressions': '{:,.0f}',
                    'reach': '{:.1%}',
                    'clicks': '{:,.0f}',
                    'ctr': '{:.2%}',
                    'conversions': '{:,.0f}',
                    'conversion_rate': '{:.2%}'
                })
                .rename(columns={
                    'week': '주차',
                    'impressions': '노출 수',
                    'reach': '도달률',
                    'clicks': '클릭 수',
                    'ctr': '클릭률',
                    'conversions': '전환 수',
                    'conversion_rate': '전환율'
                }),
                use_container_width=True
            )
    else:
        st.info("'시뮬레이션 실행' 버튼을 클릭하면 12주간의 캠페인 성과 예측 결과를 볼 수 있습니다.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 메인 앱 실행
def main():
    render_header()
    show_progress()
    
    if st.session_state.step == 1:
        render_step_1()
    elif st.session_state.step == 2:
        render_step_2()
    elif st.session_state.step == 3:
        render_step_3()

if __name__ == "__main__":
    main() 