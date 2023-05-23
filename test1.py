import requests

url = "https://space.bilibili.com/428250963"
headers = {
    "cookies":"cookie: buvid3=1D7E78BF-E695-4A04-BEDF-E92E6A4486A4138374infoc; LIVE_BUVID=AUTO5216335757402505; CURRENT_BLACKGAP=0; blackside_state=0; buvid4=D46F838A-D31B-7355-A7D5-5A29E00E3A6588596-022012712-ZLjRPEJ7nKhOaiUwnGwlyQ%3D%3D; i-wanna-go-back=-1; b_nut=100; PVID=1; _uuid=C98E2872-10864-C27E-6852-EE8EA59A44D464311infoc; rpdid=|(umkuYm)m)m0J'uY~kkkYR~Y; buvid_fp_plain=undefined; CURRENT_FNVAL=4048; CURRENT_QUALITY=80; fingerprint=b268dd43373839d34e3ffdd77eb02372; buvid_fp=b268dd43373839d34e3ffdd77eb02372; hit-dyn-v2=1; DedeUserID=512592370; DedeUserID__ckMd5=96b0606004b180ff; b_ut=5; header_theme_version=CLOSE; hit-new-style-dyn=1; CURRENT_PID=91db9bc0-c879-11ed-a31a-3778fdcafaeb; nostalgia_conf=-1; home_feed_column=5; FEED_LIVE_VERSION=V8; bp_video_offset_512592370=783934177174093800; browser_resolution=1536-754; SESSDATA=7183e965%2C1698131496%2Cb0cd3%2A42; bili_jct=a374d7320754349ecfe4b6514ddeae89; sid=5ag6b713; b_lsid=62548E9E_187C59C8F0C; bsource=search_baidu; innersign=1"

}
resp = requests.get(url, headers=headers)
resp.encoding = resp.apparent_encoding
print(resp.text)