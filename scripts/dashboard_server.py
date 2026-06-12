#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reasonix 智能交互服务器
启动后在浏览器打开 http://localhost:8080

提供：
- 工作区实时状态面板
- 一键触发自动化操作
- 交互式控制
"""
import sys, os, json, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

WORKSPACE = r'D:\reasonix-workspace'
HOST = 'localhost'
PORT = 8080

def get_status():
    """获取工作区状态"""
    docs = {}
    for name in ['99-全局控制台.md', '92-工作区架构与命名规则.md',
                 '93-新项目创建SOP.md', '91-全局复利与踩坑日志.md', 'AGENTS.md']:
        path = os.path.join(WORKSPACE, name)
        docs[name] = {
            'exists': os.path.isfile(path),
            'size': os.path.getsize(path) if os.path.isfile(path) else 0
        }
    projects = []
    if os.path.isdir(WORKSPACE):
        for item in sorted(os.listdir(WORKSPACE)):
            if item.startswith('Project_') and os.path.isdir(os.path.join(WORKSPACE, item)):
                projects.append(item)
    return {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'docs': docs,
        'doc_count': sum(1 for d in docs.values() if d['exists']),
        'projects': projects,
        'project_count': len(projects),
        'has_templates': os.path.isdir(os.path.join(WORKSPACE, 'templates')),
        'has_scripts': os.path.isdir(os.path.join(WORKSPACE, 'scripts')),
    }

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path == '/api/status':
            data = json.dumps(get_status(), ensure_ascii=False)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))
        elif self.path.startswith('/api/run/'):
            cmd = self.path[9:]
            out = self.run_command(cmd)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'result': out}).encode('utf-8'))
        elif self.path == '/api/refresh':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def run_command(self, cmd):
        try:
            if cmd == 'explorer':
                subprocess.Popen(['explorer', WORKSPACE])
                return '已打开工作区'
            elif cmd == 'notify':
                import ctypes
                s = get_status()
                msg = f'文档: {s["doc_count"]}/5  项目: {s["project_count"]}'
                ctypes.windll.user32.MessageBoxW(0, msg, 'Reasonix 工作区', 0x40)
                return '已弹出通知'
            elif cmd == 'scan':
                result = subprocess.run(
                    [sys.executable, os.path.join(WORKSPACE, 'scripts', 'intelligent_automation.py'), 'status'],
                    capture_output=True, text=True, cwd=WORKSPACE, timeout=30)
                return result.stdout[-500:] if result.stdout else 'scan done'
            elif cmd == 'wechat':
                return '请使用: /api/run/wechat/联系人/消息'
            elif cmd.startswith('wechat/'):
                parts = cmd.split('/')
                if len(parts) >= 3:
                    contact = parts[1]
                    msg = '/'.join(parts[2:])
                    r = subprocess.run(
                        [sys.executable, os.path.join(WORKSPACE, 'scripts', 'reasonix_automation.py'),
                         'wechat', contact, msg],
                        capture_output=True, text=True, timeout=30)
                    return r.stdout or 'sent'
                return '参数不足'
            elif cmd == 'open-scripts':
                subprocess.Popen(['explorer', os.path.join(WORKSPACE, 'scripts')])
                return '已打开scripts目录'
            elif cmd == 'github':
                import webbrowser
                webbrowser.open('https://github.com/WYH07243/reasonix-workspace')
                return '已打开GitHub'
            return f'未知命令: {cmd}'
        except Exception as e:
            return f'错误: {str(e)}'

    def log_message(self, format, *args):
        pass  # 静默日志

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reasonix 智能交互面板</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:"Microsoft YaHei","PingFang SC",sans-serif;
  background:linear-gradient(135deg,#0a0a1a 0%,#1a1a3e 100%);
  min-height:100vh;color:#e0e0e0;padding:20px;
}
.container{max-width:1000px;margin:0 auto}
.header{
  text-align:center;padding:30px 0 20px;
  border-bottom:1px solid rgba(100,150,255,0.15);margin-bottom:30px;
}
.header h1{
  font-size:28px;font-weight:300;letter-spacing:6px;
  background:linear-gradient(90deg,#6688ff,#aa88ff);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.header p{color:rgba(180,190,220,0.5);font-size:14px;margin-top:8px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:30px}
.card{
  background:rgba(255,255,255,0.03);border:1px solid rgba(100,150,255,0.1);
  border-radius:16px;padding:24px;backdrop-filter:blur(10px);
  transition:all 0.3s;
}
.card:hover{border-color:rgba(100,150,255,0.3);transform:translateY(-2px)}
.card h3{
  font-size:14px;font-weight:400;color:rgba(180,190,220,0.7);
  letter-spacing:2px;margin-bottom:15px;text-transform:uppercase;
}
.card.full{grid-column:1/-1}
.stat{font-size:36px;font-weight:700;color:#8899ff}
.stat-label{font-size:12px;color:rgba(180,190,220,0.5);margin-top:4px}
.doc-item{
  display:flex;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.03);
  font-size:13px;
}
.doc-item:last-child{border:none}
.doc-status{width:24px;height:24px;border-radius:50%;margin-right:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:12px}
.doc-status.ok{background:rgba(76,175,80,0.2);color:#4CAF50}
.doc-status.miss{background:rgba(244,67,54,0.2);color:#f44336}
.doc-name{flex:1;color:rgba(200,210,240,0.8)}
.doc-size{color:rgba(180,190,220,0.4);font-size:11px}
.actions{display:flex;flex-wrap:wrap;gap:10px}
.btn{
  padding:10px 20px;border:1px solid rgba(100,150,255,0.2);
  border-radius:10px;background:rgba(100,150,255,0.05);
  color:#b0c0e0;cursor:pointer;font-size:13px;
  transition:all 0.3s;font-family:inherit;
}
.btn:hover{
  background:rgba(100,150,255,0.15);border-color:rgba(100,150,255,0.4);
  transform:translateY(-1px);color:#d0e0ff;
}
.btn.primary{
  background:linear-gradient(135deg,rgba(100,150,255,0.2),rgba(170,136,255,0.2));
  border-color:rgba(100,150,255,0.3);
}
.btn.primary:hover{background:linear-gradient(135deg,rgba(100,150,255,0.3),rgba(170,136,255,0.3))}
.output{
  background:rgba(0,0,0,0.3);border-radius:12px;padding:16px;
  font-family:monospace;font-size:12px;color:rgba(180,220,180,0.7);
  min-height:60px;white-space:pre-wrap;margin-top:15px;line-height:1.6;
  border:1px solid rgba(100,150,255,0.05);
}
.wechat-input{display:flex;gap:10px;margin-top:10px}
.wechat-input input{
  flex:1;padding:8px 14px;border-radius:8px;
  border:1px solid rgba(100,150,255,0.15);
  background:rgba(255,255,255,0.05);color:#e0e0e0;
  font-size:13px;font-family:inherit;
  outline:none;transition:border-color 0.3s;
}
.wechat-input input:focus{border-color:rgba(100,150,255,0.4)}
.wechat-input input::placeholder{color:rgba(180,190,220,0.3)}
.footer{text-align:center;padding:20px;color:rgba(180,190,220,0.2);font-size:12px}
.online{color:#4CAF50}.offline{color:#f44336}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>* REASONIX 智能交互面板</h1>
    <p>自动化工作区管理体系 · <span id="statusTime">加载中...</span></p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>📁 工作区</h3>
      <div class="stat" id="docCount">-</div>
      <div class="stat-label">全局文档</div>
    </div>
    <div class="card">
      <h3>📂 项目</h3>
      <div class="stat" id="projectCount">-</div>
      <div class="stat-label">项目总数</div>
    </div>
  </div>

  <div class="grid">
    <div class="card full">
      <h3>📄 全局文档</h3>
      <div id="docList"></div>
    </div>
  </div>

  <div class="grid">
    <div class="card full">
      <h3>⚡ 智能操作</h3>
      <div class="actions">
        <button class="btn primary" onclick="runCmd('scan')">🔍 扫描工作区</button>
        <button class="btn" onclick="runCmd('explorer')">📂 打开文件夹</button>
        <button class="btn" onclick="runCmd('notify')">🔔 桌面通知</button>
        <button class="btn" onclick="runCmd('open-scripts')">📜 脚本目录</button>
        <button class="btn" onclick="runCmd('github')">🐙 GitHub 仓库</button>
        <button class="btn" onclick="refresh()">🔄 刷新状态</button>
      </div>
      <div class="wechat-input">
        <input id="wcContact" placeholder="联系人（如：小光）">
        <input id="wcMsg" placeholder="消息内容" style="flex:1.5">
        <button class="btn primary" onclick="sendWechat()">📱 发微信</button>
      </div>
      <div class="output" id="output">就绪，等待操作...</div>
    </div>
  </div>

  <div class="footer">Reasonix Workspace · 智能自动化人机交互</div>
</div>

<script>
async function refresh(){
  document.getElementById('statusTime').textContent='刷新中...';
  try{
    const r=await fetch('/api/status');
    const d=await r.json();
    document.getElementById('docCount').textContent=d.doc_count+'/5';
    document.getElementById('projectCount').textContent=d.project_count;
    document.getElementById('statusTime').textContent=d.time;
    const dl=document.getElementById('docList');
    dl.innerHTML='';
    for(const[name,info]of Object.entries(d.docs)){
      const div=document.createElement('div');div.className='doc-item';
      const status=document.createElement('div');
      status.className='doc-status '+(info.exists?'ok':'miss');
      status.textContent=info.exists?'✓':'✗';
      const nameSpan=document.createElement('span');nameSpan.className='doc-name';
      nameSpan.textContent=name;
      const sizeSpan=document.createElement('span');sizeSpan.className='doc-size';
      sizeSpan.textContent=info.exists?info.size+'B':'缺失';
      div.appendChild(status);div.appendChild(nameSpan);div.appendChild(sizeSpan);
      dl.appendChild(div);
    }
  }catch(e){
    document.getElementById('statusTime').textContent='连接失败';
  }
}

let lastOutput='';
async function runCmd(cmd){
  const out=document.getElementById('output');
  out.textContent='执行中...';
  try{
    const r=await fetch('/api/run/'+cmd);
    const d=await r.json();
    out.textContent=d.result||'完成';
  }catch(e){out.textContent='请求失败: '+e.message}
}

async function sendWechat(){
  const contact=document.getElementById('wcContact').value.trim();
  const msg=document.getElementById('wcMsg').value.trim();
  if(!contact||!msg){document.getElementById('output').textContent='请输入联系人和消息';return}
  const out=document.getElementById('output');
  out.textContent='发送中...';
  try{
    const r=await fetch('/api/run/wechat/'+encodeURIComponent(contact)+'/'+encodeURIComponent(msg));
    const d=await r.json();
    out.textContent='已发送: '+contact+' → '+msg;
  }catch(e){out.textContent='发送失败: '+e.message}
}

refresh();
setInterval(refresh,30000);
</script>
</body>
</html>
'''

if __name__ == '__main__':
    print(f'* Reasonix 智能交互面板')
    print(f'  启动地址: http://{HOST}:{PORT}')
    print(f'  Press Ctrl+C to stop')
    server = HTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')
        server.server_close()
