# 修改 build_html 函数中的模板部分
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>LottoWise Terminal</title>
    <style>
        :root { --primary: #25d970; --blue: #00b9ff; --dark: #111827; --card-bg: #ffffff; }
        body { font-family: -apple-system, sans-serif; background: #f3f4f6; margin: 0; color: #1f2937; }
        
        /* 首页看板卡片 */
        .portal { padding: 20px; }
        .welcome { margin-bottom: 25px; }
        .welcome h2 { margin: 0; font-size: 28px; font-weight: 800; }
        .welcome p { margin: 5px 0; color: #6b7280; font-size: 14px; }
        
        .main-card { 
            background: var(--dark); border-radius: 24px; padding: 24px; color: white;
            margin-bottom: 20px; position: relative; overflow: hidden;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); transition: transform 0.2s;
        }
        .main-card:active { transform: scale(0.98); }
        .main-card.mega { background: #2d1b4d; } /* Mega Millions 专用紫色 */
        
        .card-tag { font-size: 10px; font-weight: 800; color: var(--primary); letter-spacing: 1px; margin-bottom: 12px; }
        .jackpot-amt { font-size: 36px; font-weight: 900; margin-bottom: 5px; }
        .card-numbers { display: flex; gap: 6px; margin-top: 15px; }
        .card-num { width: 32px; height: 32px; background: rgba(255,255,255,0.1); border-radius: 8px; 
                    display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; }
        .card-num.spec { background: var(--blue); }
        
        /* 内部模块页（默认隐藏） */
        .module-page { display: none; position: absolute; top: 0; left: 0; width: 100%; min-height: 100vh; background: #f3f4f6; z-index: 100; }
        .nav-header { background: white; padding: 15px; display: flex; align-items: center; border-bottom: 1px solid #e5e7eb; }
        .back-btn { font-size: 20px; margin-right: 15px; cursor: pointer; }
        
        /* 这里的 CSS 复用之前的矩阵和列表样式... */
        .grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; padding: 15px; }
        .grid-item { aspect-ratio: 1; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; }
    </style>
</head>
<body>

    <div id="portal-page" class="portal">
        <div class="welcome">
            <h2>LottoWise</h2>
            <p>Smart Analysis Terminal</p>
        </div>

        <div class="main-card" onclick="openModule('pb')">
            <div class="card-tag">POWERBALL LIVE</div>
            <div class="jackpot-amt">$248M</div>
            <div style="font-size: 12px; opacity: 0.6;">Est. Cash Value: $119.8M</div>
            <div class="card-numbers">
                <div class="card-num">27</div><div class="card-num">29</div><div class="card-num">30</div>
                <div class="card-num">37</div><div class="card-num">58</div><div class="card-num spec">15</div>
            </div>
            <div style="margin-top: 20px; font-size: 12px; font-weight: 700; color: var(--primary);">TAP TO ANALYZE →</div>
        </div>

        <div class="main-card mega" onclick="openModule('mega')">
            <div class="card-tag" style="color:#a855f7">MEGA MILLIONS LIVE</div>
            <div class="jackpot-amt">$54M</div>
            <div class="card-numbers">
                <div class="card-num">05</div><div class="card-num">31</div><div class="card-num">34</div>
                <div class="card-num">51</div><div class="card-num">61</div><div class="card-num spec" style="background:#a855f7">20</div>
            </div>
            <div style="margin-top: 20px; font-size: 12px; font-weight: 700; color: #a855f7;">TAP TO ANALYZE →</div>
        </div>
    </div>

    <div id="pb-module" class="module-page">
        <div class="nav-header">
            <div class="back-btn" onclick="closeModule()">←</div>
            <div style="font-weight: 800;">Powerball Analysis</div>
        </div>
        <div class="grid">
            </div>
    </div>

    <script>
        function openModule(id) {
            document.getElementById('portal-page').style.display = 'none';
            document.getElementById(id + '-module').style.display = 'block';
            window.scrollTo(0,0);
        }
        function closeModule() {
            document.getElementById('portal-page').style.display = 'block';
            document.querySelectorAll('.module-page').forEach(p => p.style.display = 'none');
        }
    </script>
</body>
</html>
"""
