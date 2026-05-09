import tkinter as tk
from tkinter import ttk, messagebox
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET
import webbrowser
import json
import html
import os


# ===============================
# 1. 공공데이터포털 인증키
# ===============================
SERVICE_KEY = "7f289808366c14da8be96529d6c468dcfec6187f0c9848ddfbbe8151242bada6"

API_URL = "http://apis.data.go.kr/B552584/EvCharger/getChargerInfo"


# ===============================
# 2. 지역 코드
# ===============================
REGION_CODES = {
    "전북특별자치도": ["52", "45"],
    "서울특별시": ["11"],
    "부산광역시": ["26"],
    "대구광역시": ["27"],
    "인천광역시": ["28"],
    "광주광역시": ["29"],
    "대전광역시": ["30"],
    "울산광역시": ["31"],
    "세종특별자치시": ["36"],
    "경기도": ["41"],
    "강원특별자치도": ["51", "42"],
    "충청북도": ["43"],
    "충청남도": ["44"],
    "전라남도": ["46"],
    "경상북도": ["47"],
    "경상남도": ["48"],
    "제주특별자치도": ["50"]
}


# ===============================
# 3. API 오류 시 보여줄 예시 데이터
# ===============================
SAMPLE_DATA = [
    {
        "statNm": "전주시청 전기차 충전소",
        "addr": "전북특별자치도 전주시 완산구 노송광장로 10",
        "chgerType": "04",
        "stat": "2",
        "busiNm": "환경부",
        "useTime": "24시간 이용 가능",
        "output": "100",
        "lat": "35.8242",
        "lng": "127.1480"
    },
    {
        "statNm": "전주역 공영주차장 충전소",
        "addr": "전북특별자치도 전주시 덕진구 동부대로 680",
        "chgerType": "02",
        "stat": "3",
        "busiNm": "한국전력",
        "useTime": "09:00~18:00",
        "output": "7",
        "lat": "35.8495",
        "lng": "127.1615"
    },
    {
        "statNm": "전북대학교 전기차 충전소",
        "addr": "전북특별자치도 전주시 덕진구 백제대로 567",
        "chgerType": "04",
        "stat": "2",
        "busiNm": "환경부",
        "useTime": "24시간 이용 가능",
        "output": "50",
        "lat": "35.8468",
        "lng": "127.1293"
    },
    {
        "statNm": "한옥마을 공영주차장 충전소",
        "addr": "전북특별자치도 전주시 완산구 기린대로 99",
        "chgerType": "02",
        "stat": "5",
        "busiNm": "전주시",
        "useTime": "24시간 이용 가능",
        "output": "7",
        "lat": "35.8151",
        "lng": "127.1534"
    }
]


# ===============================
# 4. API에서 충전소 데이터 가져오기
# ===============================
def fetch_chargers(region_name):
    zcodes = REGION_CODES[region_name]
    all_items = []

    for zcode in zcodes:
        params = {
            "ServiceKey": SERVICE_KEY,
            "pageNo": "1",
            "numOfRows": "300",
            "zcode": zcode
        }

        url = API_URL + "?" + urlencode(params)

        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urlopen(request, timeout=15) as response:
            xml_text = response.read().decode("utf-8", errors="replace")

        root = ET.fromstring(xml_text)

        for item in root.findall(".//item"):
            charger = {
                "statNm": get_xml_text(item, "statNm"),
                "statId": get_xml_text(item, "statId"),
                "chgerId": get_xml_text(item, "chgerId"),
                "chgerType": get_xml_text(item, "chgerType"),
                "addr": get_xml_text(item, "addr"),
                "lat": get_xml_text(item, "lat"),
                "lng": get_xml_text(item, "lng"),
                "useTime": get_xml_text(item, "useTime"),
                "busiNm": get_xml_text(item, "busiNm"),
                "busiCall": get_xml_text(item, "busiCall"),
                "stat": get_xml_text(item, "stat"),
                "statUpdDt": get_xml_text(item, "statUpdDt"),
                "output": get_xml_text(item, "output"),
                "parkingFree": get_xml_text(item, "parkingFree")
            }

            if charger["lat"] and charger["lng"]:
                all_items.append(charger)

    return remove_duplicates(all_items)


def get_xml_text(parent, tag):
    element = parent.find(tag)

    if element is None or element.text is None:
        return ""

    return element.text


def remove_duplicates(items):
    result = {}
    for item in items:
        key = item.get("statId", "") + "-" + item.get("chgerId", "")
        if key not in result:
            result[key] = item

    return list(result.values())


# ===============================
# 5. 검색어 필터링
# ===============================
def filter_chargers(data, keyword):
    keyword = keyword.strip()

    if keyword == "":
        return data

    filtered = []

    for item in data:
        name = item.get("statNm", "")
        addr = item.get("addr", "")

        if keyword in name or keyword in addr:
            filtered.append(item)

    return filtered


# ===============================
# 6. 상태 코드 변환
# ===============================
def get_status_text(stat):
    if stat == "1":
        return "통신이상"
    if stat == "2":
        return "충전대기"
    if stat == "3":
        return "충전중"
    if stat == "4":
        return "운영중지"
    if stat == "5":
        return "점검중"
    if stat == "9":
        return "상태미확인"
    return "정보 없음"


def get_status_color(stat):
    if stat == "2":
        return "green"
    if stat == "3":
        return "orange"
    if stat in ["4", "5"]:
        return "red"
    return "gray"


def get_charger_type(code):
    if code == "01":
        return "DC차데모"
    if code == "02":
        return "AC완속"
    if code == "03":
        return "DC차데모 + AC3상"
    if code == "04":
        return "DC콤보"
    if code == "05":
        return "DC차데모 + DC콤보"
    if code == "06":
        return "DC차데모 + AC3상 + DC콤보"
    if code == "07":
        return "AC3상"
    if code == "08":
        return "DC콤보 완속"
    if code == "09":
        return "NACS"
    return "정보 없음"


# ===============================
# 7. 지도 HTML 만들기
# ===============================
def create_map_html(data, region_name, keyword):
    if len(data) == 0:
        messagebox.showinfo("검색 결과 없음", "검색 결과가 없습니다.")
        return

    first_lat = float(data[0]["lat"])
    first_lng = float(data[0]["lng"])

    marker_data = []

    cards_html = ""

    for item in data:
        stat = item.get("stat", "")
        status_text = get_status_text(stat)
        status_color = get_status_color(stat)
        charger_type = get_charger_type(item.get("chgerType", ""))

        name = item.get("statNm", "충전소명 없음")
        addr = item.get("addr", "주소 없음")
        busi = item.get("busiNm", "정보 없음")
        use_time = item.get("useTime", "정보 없음")
        output = item.get("output", "정보 없음")

        marker_data.append({
            "name": name,
            "addr": addr,
            "lat": float(item["lat"]),
            "lng": float(item["lng"]),
            "status": status_text,
            "chargerType": charger_type
        })

        cards_html += f"""
        <div class="card">
          <h3>{html.escape(name)}</h3>
          <span class="badge {status_color}">{status_text}</span>
          <p><b>주소:</b> {html.escape(addr)}</p>
          <p><b>충전기 타입:</b> {charger_type}</p>
          <p><b>운영기관:</b> {html.escape(busi)}</p>
          <p><b>이용시간:</b> {html.escape(use_time)}</p>
          <p><b>출력:</b> {html.escape(output)} kW</p>
        </div>
        """

    marker_json = json.dumps(marker_data, ensure_ascii=False)

    html_code = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>EV Charge Finder</title>

  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">

  <style>
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background-color: #f1f5f4;
      color: #222;
    }}

    header {{
      background-color: #16835c;
      color: white;
      text-align: center;
      padding: 24px;
    }}

    header h1 {{
      margin: 0;
      font-size: 30px;
    }}

    header p {{
      margin-top: 8px;
      font-size: 15px;
    }}

    .container {{
      width: 90%;
      max-width: 1100px;
      margin: 25px auto;
    }}

    #map {{
      height: 430px;
      border-radius: 12px;
      margin-bottom: 20px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }}

    .info {{
      background-color: white;
      padding: 15px;
      border-radius: 12px;
      margin-bottom: 18px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    }}

    .card-list {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 15px;
    }}

    .card {{
      background-color: white;
      padding: 17px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
      line-height: 1.6;
    }}

    .card h3 {{
      margin-top: 0;
      color: #16835c;
    }}

    .badge {{
      display: inline-block;
      padding: 5px 10px;
      border-radius: 20px;
      color: white;
      font-weight: bold;
      font-size: 13px;
      margin-bottom: 8px;
    }}

    .green {{
      background-color: #16835c;
    }}

    .orange {{
      background-color: #d58b00;
    }}

    .red {{
      background-color: #b00020;
    }}

    .gray {{
      background-color: #777;
    }}
  </style>
</head>

<body>

<header>
  <h1>EV Charge Finder</h1>
  <p>공공데이터포털 API 기반 전기차 충전소 검색 지도</p>
</header>

<div class="container">

  <div class="info">
    <h2>검색 지역: {html.escape(region_name)}</h2>
    <p>검색어: {html.escape(keyword) if keyword else "없음"}</p>
    <p>검색 결과: {len(data)}개</p>
  </div>

  <div id="map"></div>

  <div class="card-list">
    {cards_html}
  </div>

</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
  const chargers = {marker_json};

  const map = L.map("map").setView([{first_lat}, {first_lng}], 13);

  L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
    attribution: "© OpenStreetMap"
  }}).addTo(map);

  chargers.forEach(charger => {{
    const marker = L.marker([charger.lat, charger.lng]).addTo(map);

    marker.bindPopup(`
      <b>${{charger.name}}</b><br>
      ${{charger.addr}}<br>
      상태: ${{charger.status}}<br>
      타입: ${{charger.chargerType}}
    `);
  }});
</script>

</body>
</html>
"""

    file_name = "ev_charge_finder_result.html"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(html_code)

    file_path = os.path.abspath(file_name)
    webbrowser.open("file://" + file_path)


# ===============================
# 8. 검색 버튼 기능
# ===============================
def search():
    region_name = region_combo.get()
    keyword = keyword_entry.get()

    status_label.config(text="공공데이터 API를 불러오는 중입니다...")
    window.update()

    try:
        data = fetch_chargers(region_name)

        if len(data) == 0:
            status_label.config(text="API 데이터가 없어 예시 데이터를 사용합니다.")
            data = SAMPLE_DATA
        else:
            status_label.config(text=f"API 데이터 {len(data)}개를 불러왔습니다.")

    except HTTPError as e:
        status_label.config(text="API HTTP 오류가 발생하여 예시 데이터를 사용합니다.")
        data = SAMPLE_DATA

    except URLError as e:
        status_label.config(text="인터넷 또는 API 서버 오류가 발생하여 예시 데이터를 사용합니다.")
        data = SAMPLE_DATA

    except Exception as e:
        status_label.config(text="오류가 발생하여 예시 데이터를 사용합니다.")
        data = SAMPLE_DATA

    filtered_data = filter_chargers(data, keyword)

    if len(filtered_data) == 0:
        messagebox.showinfo("검색 결과", "검색 결과가 없습니다.")
        return

    create_map_html(filtered_data, region_name, keyword)


# ===============================
# 9. Tkinter 화면 만들기
# ===============================
window = tk.Tk()
window.title("EV Charge Finder")
window.geometry("520x300")
window.resizable(False, False)

title_label = tk.Label(
    window,
    text="EV Charge Finder",
    font=("Arial", 22, "bold"),
    fg="#16835c"
)
title_label.pack(pady=15)

desc_label = tk.Label(
    window,
    text="공공데이터포털 API를 활용한 전기차 충전소 검색 앱",
    font=("Arial", 11)
)
desc_label.pack(pady=5)

frame = tk.Frame(window)
frame.pack(pady=15)

region_label = tk.Label(frame, text="지역 선택")
region_label.grid(row=0, column=0, padx=5, pady=5)

region_combo = ttk.Combobox(
    frame,
    values=list(REGION_CODES.keys()),
    width=20,
    state="readonly"
)
region_combo.set("전북특별자치도")
region_combo.grid(row=0, column=1, padx=5, pady=5)

keyword_label = tk.Label(frame, text="검색어")
keyword_label.grid(row=1, column=0, padx=5, pady=5)

keyword_entry = tk.Entry(frame, width=23)
keyword_entry.grid(row=1, column=1, padx=5, pady=5)
keyword_entry.insert(0, "전주")

search_button = tk.Button(
    window,
    text="충전소 지도 검색",
    command=search,
    bg="#16835c",
    fg="white",
    font=("Arial", 12, "bold"),
    padx=20,
    pady=8
)
search_button.pack(pady=10)

status_label = tk.Label(
    window,
    text="지역과 검색어를 입력한 뒤 버튼을 누르세요.",
    fg="#555"
)
status_label.pack(pady=8)

window.mainloop()