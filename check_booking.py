import json
import os
import urllib.parse
import urllib.request

REST_API_KEY = os.environ["KAKAO_REST_API_KEY"]
CLIENT_SECRET = os.environ["KAKAO_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["KAKAO_REFRESH_TOKEN"]

# 현재 테스트 조건
START_DAY = "2026-9-22"
END_DAY = "2026-9-23"
START_TIMESTAMP = "1785510000"
END_TIMESTAMP = "1785596400"


def post(url, data, headers=None):
    encoded = urllib.parse.urlencode(data).encode()
    request = urllib.request.Request(
        url,
        data=encoded,
        headers=headers or {},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode()


def refresh_access_token():
    response = post(
        "https://kauth.kakao.com/oauth/token",
        {
            "grant_type": "refresh_token",
            "client_id": REST_API_KEY,
            "refresh_token": REFRESH_TOKEN,
            "client_secret": CLIENT_SECRET,
        },
        {
            "Content-Type":
                "application/x-www-form-urlencoded;charset=utf-8"
        },
    )

    result = json.loads(response)

    if "access_token" not in result:
        raise RuntimeError(f"카카오 토큰 갱신 실패: {result}")

    return result["access_token"]


def check_booking():
    response = post(
        "https://woraksan.co.kr/booking/html_day_booking.cm",
        {
            "backurl":
                "https://woraksan.co.kr/Reservation---?idx=21",
            "prod_idx": "21",
            "start_day": START_DAY,
            "start_timestamp": START_TIMESTAMP,
            "end_day": END_DAY,
            "end_timestamp": END_TIMESTAMP,
            "person": "0",
            "idx": "21",
        },
        {
            "Content-Type":
                "application/x-www-form-urlencoded;charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://woraksan.co.kr",
            "Referer":
                "https://woraksan.co.kr/Reservation---?idx=21",
            "User-Agent": "Mozilla/5.0",
        },
    )

    result = json.loads(response)
    available = result.get("msg") == "SUCCESS"

    print(f"예약 조회 결과: {result.get('msg')}")
    return available


def send_kakao_message(access_token):
    template = {
        "object_type": "text",
        "text": (
            "🏨 월악산 예약 확인\n"
            "TYPE B - 204\n"
            "2026-09-22 ~ 2026-09-23\n"
            "현재 예약 가능한 상태입니다."
        ),
        "link": {
            "web_url": "https://suya-kim.github.io/susu/",
            "mobile_web_url": "https://suya-kim.github.io/susu/",
        },
        "button_title": "확인하기",
    }

    response = post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        {"template_object": json.dumps(template, ensure_ascii=False)},
        {
            "Authorization": f"Bearer {access_token}",
            "Content-Type":
                "application/x-www-form-urlencoded;charset=utf-8",
        },
    )

    result = json.loads(response)

    if result.get("result_code") != 0:
        raise RuntimeError(f"카카오톡 발송 실패: {result}")

    print("카카오톡 발송 성공")


if __name__ == "__main__":
    if check_booking():
        token = refresh_access_token()
        send_kakao_message(token)
    else:
        print("현재 예약할 수 없습니다.")
