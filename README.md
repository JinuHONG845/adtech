# AI 기반 광고 컨설팅 플랫폼

Google Performance MAX 스타일의 AI 기반 광고 컨설팅 플랫폼입니다. 이 앱은 다양한 AI 모델을 활용하여 브랜드/제품에 맞는 최적의 광고 전략을 추천합니다.

## 주요 기능

- **여러 AI 모델 지원**: ChatGPT, Claude, Gemini, DeepSeek, Grok 등 다양한 AI 모델을 통한 분석
- **광고 유형 추천**: 검색광고와 디스플레이 광고 중 최적의 전략 추천
- **매체별 예산 배분**: Google, Meta, Naver, Kakao, TTD 등 주요 매체에 대한 예산 배분 제안
- **광고 소재 추천**: 필요한 광고 소재 유형과 개수 추천
- **성과 시뮬레이션**: 12주간의 광고 성과 예측 및 시각화
- **사용하기 쉬운 인터페이스**: Google Performance MAX 스타일의 직관적인 UI

## 설치 및 실행 방법

1. 저장소 클론
   ```
   git clone https://github.com/yourusername/adtech.git
   cd adtech
   ```

2. 필요한 패키지 설치
   ```
   pip install -r requirements.txt
   ```

3. API 키 설정
   - `.streamlit/secrets.toml` 파일에 필요한 API 키 입력
   - 또는 Streamlit Cloud에서 앱을 배포할 경우 대시보드에서 시크릿 설정

4. 앱 실행
   ```
   streamlit run app.py
   ```

## API 키 설정 방법

### 로컬 개발 시

`.streamlit/secrets.toml` 파일에 다음과 같이 API 키를 설정합니다:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"
GOOGLE_API_KEY = "your-google-api-key-here"
DEEPSEEK_API_KEY = "your-deepseek-api-key-here"
GROK_API_KEY = "your-grok-api-key-here"
```

### Streamlit Cloud 배포 시

1. Streamlit Cloud 대시보드에서 앱 선택
2. "Settings" > "Secrets" 메뉴로 이동
3. 위의 API 키들을 동일한 이름으로 추가

## 사용 방법

1. 브랜드/제품명, 브랜드 설명, 캠페인 목표를 입력
2. 분석에 사용할 AI 모델 선택
3. "분석 시작" 버튼 클릭
4. AI 분석 결과 확인
5. "시뮬레이션 실행" 버튼을 클릭하여 광고 성과 예측 결과 확인

## 주의 사항

- 모든 API 키는 보안을 위해 안전하게 관리해야 합니다
- 일부 API 모델은 사용량에 따른 비용이 발생할 수 있습니다
- 실제 광고 집행 전에 전문가의 검토를 권장합니다 