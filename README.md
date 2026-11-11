# Team11 – 부산튜브 시민 반응 분석 대시보드

> 앱 URL: (배포 후 여기에 작성)

## 프로젝트 소개
부산광역시 공식 유튜브 채널(부산튜브)의 영상 유형(정책 정보형 vs 숏폼/예능형)별
시민 참여도와 댓글 감성을 분석하는 Streamlit 대시보드입니다.
현재(2단계)는 YouTube Data API v3로 영상 메타데이터와 댓글을 수집해 표로 확인하는 단계입니다.

## 팀원
| 이름 | 역할 |
|---|---|
| 라유리 | 데이터 수집 및 분석 |
| 한지민 | 앱 화면 시각화 및 영상 |

## 실행 방법
```bash
pip install -r requirements.txt
# .streamlit/secrets.toml 파일을 만들고 YOUTUBE_API_KEY 입력 (secrets.toml.example 참고)
streamlit run app.py
```

## 사용 라이브러리
streamlit, pandas, google-api-python-client (3단계에서 kiwipiepy 추가 예정)

## 현재 구현 범위
- YouTube Data API v3 영상 메타데이터(조회수, 좋아요 수, 업로드 일자) 수집
- 영상별 댓글 수집 및 작성자 닉네임 익명화 (user_001 …)
- 수집 데이터 샘플 표 출력

## 개인정보 및 API 키
- 작성자 닉네임은 수집 즉시 `user_001` 형태로 변환하며 원본은 저장하지 않습니다.
- API 키는 코드에 없고 `secrets.toml`(Git 제외)로 관리합니다.

## 실행 화면
![앱 실행 화면](screenshots/app_main.png)
