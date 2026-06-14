import os

footer_content = '''                <div class="footer-col">
                    <h4 class="footer-col-title">NEWSLETTER</h4>
                    <p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:10px;">Get the latest cybersecurity updates.</p>
                    <form class="newsletter-form" style="display:flex;flex-direction:column;gap:8px;">
                        <input type="email" class="newsletter-email" placeholder="Your email address" required style="padding:10px 12px; border-radius:6px; border:1px solid rgba(255,255,255,0.1); background:rgba(0,0,0,0.3); color:#fff; font-size:0.85rem; font-family:var(--font-sans); outline:none;">
                        <button type="submit" style="padding:10px; border-radius:6px; background:var(--accent-cyan); color:#000; font-weight:600; font-size:0.85rem; border:none; cursor:pointer; font-family:var(--font-sans); transition:all 0.2s;">Subscribe</button>
                    </form>
                    <p class="newsletter-message" style="margin-top:8px;font-size:0.75rem;"></p>
                </div>
            </div>'''

folder=r'c:\Users\LRC\OneDrive\Documents\internship details\title and ieee paper\phising\frontend'
for f in os.listdir(folder):
    if f.endswith('.html'):
        path = os.path.join(folder, f)
        text = open(path, 'r', encoding='utf-8').read()
        
        if 'class="newsletter-form"' not in text:
            new_text = text.replace('            </div>\n            <div class="footer-bottom">', footer_content + '\n            <div class="footer-bottom">')
            new_text = new_text.replace('            </div>\r\n            <div class="footer-bottom">', footer_content + '\r\n            <div class="footer-bottom">')
            open(path, 'w', encoding='utf-8', newline='').write(new_text)
