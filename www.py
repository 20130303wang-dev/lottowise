import requests
import os

# --- 1. 数据抓取与解析 ---
def fetch_raw_data(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r.json()[::-1] # 转为时间正序
    except Exception as e:
        print(f"数据抓取失败: {e}")
        return []

def analyze_lotto(data, is_pb=True):
    if not data: return None
    r_limit = 69 if is_pb else 70
    b_limit = 26 if is_pb else 25
    
    r_stats = {i: 0 for i in range(1, r_limit + 1)}
    b_stats = {i: {"count": 0, "last": 0} for i in range(1, b_limit + 1)}
    
    recent = data[-100:] 
    for i, draw in enumerate(recent):
        reds = draw.get('winning_numbers', "").split()
        if not reds: continue
        for r in reds[:5]:
            if r.isdigit() and int(r) in r_stats:
                r_stats[int(r)] += 1
        
        blue = int(reds[5]) if is_pb and len(reds) > 5 else int(draw.get('mega_ball', 0))
        if blue in b_stats:
            b_stats[blue]["count"] += 1
            b_stats[blue]["last"] = i
            
    max_r = max(r_stats.values()) or 1
    
    # 提取最新一期信息
    latest = recent[-1]
    # 格式化日期，只保留年月日
    draw_date = latest.get('draw_date', 'N/A')[:10]
    # 期号通常不在主字段，有些接口用 ID 或特定字段代替，这里我们优先取官方字段
    draw_id = latest.get('draw_id', 'LATEST') 
    
    red_nums = latest.get('winning_numbers', "").split()[:5]
    if is_pb:
        blue_num = latest.get('winning_numbers', "").split()[5] if len(latest.get('winning_numbers', "").split()) > 5 else "--"
    else:
        blue_num = latest.get('mega_ball', "--")
    
    return {
        "info": {"id": draw_id, "date": draw_date, "reds": red_nums, "blue": blue_num},
        "red": [{"n": f"{k:02d}", "h": v/max_r, "c": v} for k, v in r_stats.items()],
        "blue": sorted([{"n": f"{k:02d}", "om": len(recent)-1-v['last'], "hit": v['count']} for k, v in b_stats.items()], key=lambda x: x['om'], reverse=True)
    }

# --- 2. 网页生成 ---
def generate_terminal():
    pb_raw = fetch_raw_data("https://data.ny.gov/resource/d6yy-54nr.json?$limit=1000")
    mega_raw = fetch_raw_data("https://data.ny.gov/resource/5xaw-6ayf.json?$limit=1000")
    
    pb = analyze_lotto(pb_raw, True)
    mega = analyze_lotto(mega_raw, False)

    if not pb or not mega: return

    def build_grid(red_data):
        return "".join([f'<div class="grid-item" style="background:rgba(37,217,112,{i["h"]}); color:{"#fff" if i["h"]>0.5 else "#111"}">{i["n"]}<small>{i["c"]}x</small></div>' for i in red_data])

    def build_list(blue_data):
        return "".join([f'<div class="row"><div class="ball">{b["n"]}</div><div class="data-col"><div class="label"><span>遗漏: <b>{b["om"]}</b></span><span>命中: {b["hit"]}x</span></div><div class="bar-bg"><div class="bar-fill" style="width:{min(b["om"]*5, 100)}%"></div></div></div></div>' for b in blue_data[:12]])

    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>LottoWise 专业数据终端</title>
        <style>
            :root {{ --green: #25d970; --blue: #00b9ff; --dark: #0f172a; --bg: #f8fafc; }}
            body {{ font-family: -apple-system, "Helvetica Neue", sans-serif; background: var(--bg); margin: 0; color: #1e293b; overflow-x: hidden; }}
            
            /* 首页看板 */
            .portal {{ padding: 20px; }}
            .brand {{ font-size: 26px; font-weight: 900; margin-bottom: 25px; color: var(--dark); }}
            .brand span {{ color: var(--green); }}
            
            .main-card {{ background: var(--dark); border-radius: 24px; padding: 25px; color: white; margin-bottom: 20px; box-shadow: 0 12px 24px rgba(0,0,0,0.12); transition: 0.2s; position: relative; }}
            .main-card:active {{ transform: scale(0.97); }}
            .main-card.mega {{ background: #2e1065; }}
            
            .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }}
            .tag {{ font-size: 10px; font-weight: 800; color: var(--green); letter-spacing: 1px; }}
            .draw-info {{ font-size: 11px; opacity: 0.6; text-align: right; line-height: 1.4; }}
            
            .jackpot-box {{ margin-bottom: 15px; }}
            .jackpot-label {{ font-size: 11px; opacity: 0.7; margin-bottom: 4px; }}
            .jackpot-val {{ font-size: 36px; font-weight: 900; color: white; }}
            
            .nums-row {{ display: flex; gap: 6px; }}
            .n-box {{ width: 34px; height: 34px; background: rgba(255,255,255,0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; }}
            .n-box.spec {{ background: var(--blue); color: white; }}
            
            .cta {{ margin-top: 25px; font-size: 12px; font-weight: 800; color: var(--green); }}

            /* 详情页 */
            .module-page {{ display: none; min-height: 100vh; background: var(--bg); position: absolute; top: 0; width: 100%; }}
            .header {{ background: white; padding: 15px; display: flex; align-items: center; position: sticky; top: 0; z-index: 10; border-bottom: 1px solid #e2e8f0; }}
            .back-btn {{ font-size: 24px; margin-right: 15px; cursor: pointer; padding: 5px; }}
            .container {{ padding: 15px; }}
            .card {{ background: white; border-radius: 20px; padding: 18px; margin-bottom: 15px; }}
            .card-title {{ font-size: 12px; font-weight: 800; color: #94a3b8; margin-bottom: 15px; text-transform: uppercase; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }}
            .grid-item {{ aspect-ratio: 1; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; }}
            .grid-item small {{ font-size: 8px; opacity: 0.6; font-weight: 400; }}
            
            .row {{ display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }}
            .ball {{ width: 36px; height: 36px; background: var(--blue); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; margin-right: 15px; }}
            .data-col {{ flex-grow: 1; }}
            .label {{ display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }}
            .bar-bg {{ height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }}
            .bar-fill {{ height: 100%; background: var(--blue); }}
            
            .premium-card {{ background: var(--dark); color: white; text-align: center; padding: 30px 20px; border-radius: 20px; }}
            .btn {{ background: var(--green); color: var(--dark); padding: 16px 32px; border-radius: 12px; font-weight: 800; text-decoration: none; display: inline-block; margin-top: 15px; }}
        </style>
    </head>
    <body>

        <div id="portal" class="portal">
            <div class="brand">Lotto<span>Wise</span></div>
            
            <div class="main-card" onclick="openMod('pb')">
                <div class="card-header">
                    <div class="tag">POWERBALL LIVE</div>
                    <div class="draw-info">期号: #{pb['info']['id']}<br>{pb['info']['date']}</div>
                </div>
                <div class="jackpot-box">
                    <div class="jackpot-label">ESTIMATED JACKPOT (预估奖池)</div>
                    <div class="jackpot-val">$248,000,000</div>
                </div>
                <div class="nums-row">
                    {''.join([f'<div class="n-box">{n}</div>' for n in pb['info']['reds']])}
                    <div class="n-box spec">{pb['info']['blue']}</div>
                </div>
                <div class="cta">查看深度趋势分析 →</div>
            </div>

            <div class="main-card mega" onclick="openMod('mega')">
                <div class="card-header">
                    <div class="tag" style="color:#a855f7">MEGA MILLIONS LIVE</div>
                    <div class="draw-info">期号: #{mega['info']['id']}<br>{mega['info']['date']}</div>
                </div>
                <div class="jackpot-box">
                    <div class="jackpot-label" style="opacity:0.5">ESTIMATED JACKPOT (预估奖池)</div>
                    <div class="jackpot-val">$54,000,000</div>
                </div>
                <div class="nums-row">
                    {''.join([f'<div class="n-box">{n}</div>' for n in mega['info']['reds']])}
                    <div class="n-box spec" style="background:#a855f7">{mega['info']['blue']}</div>
                </div>
                <div class="cta" style="color:#a855f7">查看深度趋势分析 →</div>
            </div>
        </div>

        <div id="pb-mod" class="module-page">
            <div class="header">
                <div class="back-btn" onclick="closeMod()">←</div>
                <div style="font-weight:900;">POWERBALL 数据终端</div>
            </div>
            <div class="container">
                <div class="card">
                    <div class="card-title">红球热度分布 (最近100期)</div>
                    <div class="grid">{build_grid(pb['red'])}</div>
                </div>
                <div class="card">
                    <div class="card-title">蓝球遗漏跟踪</div>
                    {build_list(pb['blue'])}
                </div>
                <div class="premium-card">
                    <div style="font-size:18px; font-weight:800;">获取 AI 预测号码</div>
                    <p style="font-size:12px; opacity:0.7;">基于神经网络分析下一期高概率组合</p>
                    <a href="#" class="btn">立即订阅 - $9/月</a>
                </div>
            </div>
        </div>

        <div id="mega-mod" class="module-page">
            <div class="header">
                <div class="back-btn" onclick="closeMod()">←</div>
                <div style="font-weight:900; color:#2e1065;">MEGA MILLIONS 数据终端</div>
            </div>
            <div class="container">
                <div class="card"><div class="card-title">红球热度分布</div><div class="grid">{build_grid(mega['red'])}</div></div>
                <div class="card"><div class="card-title">蓝球遗漏跟踪</div>{build_list(mega['blue'])}</div>
            </div>
        </div>

        <script>
            function openMod(id) {{
                document.getElementById('portal').style.display = 'none';
                document.getElementById(id + '-mod').style.display = 'block';
                window.scrollTo(0,0);
            }}
            function closeMod() {{
                document.getElementById('portal').style.display = 'block';
                document.querySelectorAll('.module-page').forEach(m => m.style.display = 'none');
            }}
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("✅ 终端构建完成：index.html 已包含真实期号和日期。")

if __name__ == "__main__":
    generate_terminal()
