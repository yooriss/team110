# 🌊 부산광역시 공식 유튜브 시민 반응 및 소통 효과 분석

> 앱 URL: (https://team11-qvqdgjkayhysinnfk5lnfz.streamlit.app)

## 프로젝트 소개
부산광역시 공식 유튜브 채널(부산튜브)의 영상 유형(정책 정보형 vs 숏폼/예능형)별
시민 참여도와 댓글 감성을 분석하는 Streamlit 대시보드입니다.

## 팀원
| 이름(학번) | 역할 |
|---|---|
| 라유리(202605110] | 데이터 수집 및 분석,Streamlit 대시보드 UI 구현 |
| 한지민(202606257) | 텍스트 분석,Streamlit 대시보드 UI 구현 |


## 실행 방법
```bash
pip install -r requirements.txt
# .streamlit/secrets.toml 에 YOUTUBE_API_KEY 설정
streamlit run app.py
```

## 사용 라이브러리
streamlit, pandas, google-api-python-client, kiwipiepy

## 현재 구현 범위 (중간 단계)
- YouTube Data API v3 영상 메타데이터·댓글 수집
- 작성자 닉네임 익명화 (user_001 …)
- 수집 데이터 샘플 표 출력

## 실행 화면
 ![메타데이터 수집 화면](./screenshot.png) | ![댓글 표 출력 화면](./screenshot2.png) |

