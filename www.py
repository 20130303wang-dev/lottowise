import requests
import datetime
import os

# --- 1. 配置与抓取 ---
def fetch_lottery(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r.json()[::-1] # 保持时间正序
    except: return []

# --- 2. 核心分析逻辑 ---
def get_stats(data, is_pb=True):
    r_limit = 69 if is_pb else 70
    b_limit = 26 if is_pb else 25
    r_stats = {i: 0 for i in range(1, r_limit + 1)}
    b_stats = {i: {"count": 0, "last": 0} for i in range(1, b_limit + 1)}
    
    recent = data[-100:] # 只分析最近100期
    for i, draw in enumerate(recent):
        nums = draw.get('winning_numbers', "").split()
        if len(nums) < 6: continue
        for r in nums[:5]: r_stats[int(r)] += 1
        blue = int(nums[5]) if is_pb else int(draw.get('mega_ball', 1))
        if blue in b_stats:
            b_stats[blue]["count"] += 1
            b_stats[blue]["last"] = i
            
    max_r = max(r_stats.values()) or 1
    red_res = [{"n": f"{k:02d}", "h": v/max_r, "c": v} for k, v in r_stats.items()]
    blue_res = [{"n": f"{k:02d}", "om": len(recent)-1-v["last"], "hit": v["count"]} for k, v in b_stats.items()]
    return red_res, sorted(blue_res, key=lambda x: x['om'], reverse=True)

# --- 3. 生成手机端 HTML ---
def build_html(pb_data, mega_data):
    pb_r, pb_b = get_stats(pb_data, True)
    
    # 构造红球矩阵 HTML
    red_grid_html = "".join([f'''
        <div class="grid-item" style="background:rgba(37,217,112,{i['h']}); color:{'#fff' if i['h']>0.5 else '#163300'}">
            {i['n']} <small>{i['c']}x</small>
        </div>''' for i in pb_r])
    
    # 构造蓝球列表 HTML
    blue_list_html = "".join([f'''
        <div class="row">
            <div class="ball">{b['n']}</div>
            <div class="data">
                <div class="label"><span>Omission: <b>{b['om']}</b></span><span>Hit: {b['hit']}x</span></div>
                <div class="bar-bg"><div class="bar-fill" style="width:{min(b['om']*5, 100)}%"></div></div>
            </div>
        </div>''' for b in pb_b[:12]])

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>LottoWise Pro</title>
        <style>
            :root {{ --green: #25d970; --blue: #00b9ff; --dark: #163300; --bg: #f8fafc; }}
            body {{ font-family: -apple-system, sans-serif; background: var(--bg); margin: 0; padding-bottom: 80px; }}
            .nav {{ background: var(--dark); color: white; padding: 20px 15px; position: sticky; top: 0; z-index: 100; }}
            .tabs {{ display: flex; background: white; border-bottom: 1px solid #e2e8f0; }}
            .tab {{ flex: 1; text-align: center; padding: 15px; font-size: 12px; font-weight: 800; color: #94a3b8; }}
            .tab.active {{ color: var(--dark); border-bottom: 3px solid var(--green); }}
            .container {{ padding: 15px; }}
            .card {{ background: white; border-radius: 16px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
            .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }}
            .grid-item {{ aspect-ratio: 1; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; }}
            .grid-item small {{ font-size: 8px; font-weight: 400; opacity: 0.8; }}
            .row {{ display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }}
            .ball {{ width: 34px; height: 34px; background: var(--blue); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; margin-right: 12px; }}
            .data {{ flex-grow: 1; }}
            .label {{ display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }}
            .bar-bg {{ height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }}
            .bar-fill {{ height: 100%; background: var(--blue); }}
            .btn-pay {{ display: block; background: var(--green); color: var(--dark); text-align: center; padding: 15px; border-radius: 12px; font-weight: 800; text-decoration: none; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="nav">
            <div style="font-size:10px; color:var(--green); font-weight:800;">● SYSTEM ACTIVE</div>
            <h2 style="margin:0;">LottoWise <span style="color:var(--green)">Pro</span></h2>
        </div>
        <div class="tabs">
            <div id="t1" class="tab active" onclick="sw('r')">RED HEAT</div>
            <div id="t2" class="tab" onclick="sw('b')">BLUE COLD</div>
            <div id="t3" class="tab" onclick="sw('p')">PREMIUM</div>
        </div>
        <div class="container" id="rc"><div class="card"><div class="grid">{red_grid_html}</div></div></div>
        <div class="container" id="bc" style="display:none;"><div class="card">{blue_list_html}</div></div>
        <div class="container" id="pc" style="display:none;">
            <div class="card" style="text-align:center; padding: 40px 20px;">
                <h3 style="margin:0;">Unlock AI Predictions</h3>
                <p style="font-size:13px; color:#64748b;">Get the most probable 3-ball combo based on neural analysis.</p>
                <a href="#" class="btn-pay">Subscribe for $9.90/mo</a>
            </div>
        </div>
        <script>
            function sw(t){{
                document.getElementById('rc').style.display = t=='r'?'block':'none';
                document.getElementById('bc').style.display = t=='b'?'block':'none';
                document.getElementById('pc').style.display = t=='p'?'block':'none';
                document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
                if(t=='r')document.getElementById('t1').classList.add('active');
                if(t=='b')document.getElementById('t2').classList.add('active');
                if(t=='p')document.getElementById('t3').classList.add('active');
            }}
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    pb_url = "https://data.ny.gov/resource/d6yy-54nr.json?$limit=1000&$order=draw_date DESC"
    mega_url = "https://data.ny.gov/resource/5xaw-6ayf.json?$limit=1000&$order=draw_date DESC"
    build_html(fetch_lottery(pb_url), fetch_lottery(mega_url))
    print("DONE: index.html is ready for GitHub Pages.")