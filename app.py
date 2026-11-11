"""Team11 - 부산튜브 시민 반응 분석 대시보드 (2단계: 데이터 수집 + 표 확인)"""
import os

import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

st.set_page_config(page_title="부산튜브 시민 반응 분석", layout="wide")


# ---------- API 키 ----------
def get_api_key():
    """Streamlit secrets 또는 환경변수에서 API 키를 읽는다 (코드에 직접 쓰지 않음)."""
    try:
        return st.secrets["YOUTUBE_API_KEY"]
    except Exception:
        return os.environ.get("YOUTUBE_API_KEY")


# ---------- 수집 함수 ----------
def resolve_channel(youtube, query):
    """입력(채널 ID / @핸들 / 채널 이름)을 받아 (채널 ID, 채널 제목, 업로드 재생목록 ID)를 반환."""
    query = query.strip()
    if query.startswith("UC"):
        res = youtube.channels().list(part="snippet,contentDetails", id=query).execute()
    elif query.startswith("@"):
        res = youtube.channels().list(part="snippet,contentDetails", forHandle=query).execute()
    else:
        found = youtube.search().list(part="snippet", q=query, type="channel", maxResults=1).execute()
        if not found.get("items"):
            return None
        cid = found["items"][0]["snippet"]["channelId"]
        res = youtube.channels().list(part="snippet,contentDetails", id=cid).execute()
    if not res.get("items"):
        return None
    item = res["items"][0]
    return item["id"], item["snippet"]["title"], item["contentDetails"]["relatedPlaylists"]["uploads"]


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_videos(api_key, uploads_id, max_videos):
    """입력: 업로드 재생목록 ID, 최대 영상 수 / 출력: 영상 메타데이터 DataFrame."""
    youtube = build("youtube", "v3", developerKey=api_key)
    ids, token = [], None
    while len(ids) < max_videos:
        res = youtube.playlistItems().list(
            part="contentDetails", playlistId=uploads_id,
            maxResults=min(50, max_videos - len(ids)), pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in res["items"]]
        token = res.get("nextPageToken")
        if not token:
            break

    rows = []
    for i in range(0, len(ids), 50):
        res = youtube.videos().list(part="snippet,statistics", id=",".join(ids[i:i + 50])).execute()
        for v in res["items"]:
            s = v.get("statistics", {})
            rows.append({
                "video_id": v["id"],
                "title": v["snippet"]["title"],
                "published_at": v["snippet"]["publishedAt"][:10],
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comment_count": int(s.get("commentCount", 0)),
            })
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_comments(api_key, video_ids, per_video):
    """입력: 영상 ID 목록, 영상당 최대 댓글 수 / 출력: 익명화된 댓글 DataFrame.
    작성자 닉네임은 user_001 형태로 바꾸고 원본은 저장하지 않는다."""
    youtube = build("youtube", "v3", developerKey=api_key)
    rows, alias = [], {}
    for vid in video_ids:
        got, token = 0, None
        while got < per_video:
            try:
                res = youtube.commentThreads().list(
                    part="snippet", videoId=vid, maxResults=min(100, per_video - got),
                    order="time", textFormat="plainText", pageToken=token).execute()
            except HttpError:  # 댓글이 막힌 영상 등은 건너뜀
                break
            for it in res["items"]:
                c = it["snippet"]["topLevelComment"]["snippet"]
                name = c.get("authorDisplayName", "")
                if name not in alias:
                    alias[name] = f"user_{len(alias) + 1:03d}"
                rows.append({
                    "video_id": vid,
                    "author": alias[name],
                    "comment": c["textDisplay"],
                    "likes": c.get("likeCount", 0),
                    "published_at": c["publishedAt"][:10],
                })
                got += 1
            token = res.get("nextPageToken")
            if not token:
                break
    return pd.DataFrame(rows)


# ---------- 화면 ----------
st.title("부산튜브 시민 반응 분석 대시보드")
st.caption("Team11 | 부산시 공식 유튜브 영상 메타데이터와 댓글 수집 (중간 단계)")

api_key = get_api_key()
if not api_key:
    st.error("API 키가 없습니다. `.streamlit/secrets.toml`에 YOUTUBE_API_KEY를 설정하세요.")
    st.stop()

with st.sidebar:
    st.header("수집 설정")
    channel_q = st.text_input("채널 (이름, @핸들 또는 채널 ID)", value="부산튜브")
    max_videos = st.slider("수집할 영상 수", 5, 100, 20, step=5)
    per_video = st.slider("영상당 최대 댓글 수", 10, 200, 50, step=10)
    run = st.button("데이터 수집 시작", type="primary")

if run:
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        ch = resolve_channel(youtube, channel_q)
        if ch is None:
            st.warning("채널을 찾지 못했습니다. 채널 ID(UC로 시작)를 직접 입력해 보세요.")
            st.stop()
        _, ch_title, uploads_id = ch
        with st.spinner("영상 정보를 수집하는 중..."):
            videos = fetch_videos(api_key, uploads_id, max_videos)
        with st.spinner("댓글을 수집하는 중..."):
            comments = fetch_comments(api_key, tuple(videos["video_id"]), per_video)
        st.session_state["data"] = (ch_title, videos, comments)
    except HttpError as e:
        st.error(f"YouTube API 오류: {e}")
        st.stop()

if "data" not in st.session_state:
    st.info("왼쪽 사이드바에서 설정 후 '데이터 수집 시작'을 눌러 주세요.")
    st.stop()

ch_title, videos, comments = st.session_state["data"]
st.subheader(f"수집 채널: {ch_title}")

c1, c2, c3 = st.columns(3)
c1.metric("수집한 영상 수", len(videos))
c2.metric("수집한 댓글 수", len(comments))
c3.metric("영상 평균 조회수", f"{int(videos['views'].mean()):,}" if len(videos) else 0)

st.markdown("### 영상 메타데이터")
st.dataframe(videos, use_container_width=True)

st.markdown("### 댓글 데이터 샘플 (작성자 익명화됨)")
st.dataframe(comments.head(100), use_container_width=True)
