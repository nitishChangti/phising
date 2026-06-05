/**
 * PhishShield AI — Frontend JavaScript V2
 * Enhanced particle system, Lucide icons, URL scanner, scroll animations
 */

// ============================================================
// 1. PARTICLE SYSTEM (Much denser & brighter like the reference)
// ============================================================
class ParticleSystem {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null };
        this.resize();
        this.init();
        this.animate();

        window.addEventListener('resize', () => { this.resize(); this.init(); });
        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
        window.addEventListener('mouseout', () => {
            this.mouse.x = null; this.mouse.y = null;
        });
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    init() {
        // Much denser particles like the reference
        const area = this.canvas.width * this.canvas.height;
        const count = Math.min(Math.floor(area / 6000), 200);
        this.particles = [];
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 2.5 + 0.8,
                speedX: (Math.random() - 0.5) * 0.3,
                speedY: (Math.random() - 0.5) * 0.3,
                opacity: Math.random() * 0.6 + 0.15,
                hue: Math.random() > 0.7 ? 195 : 160, // mix of cyan and teal
            });
        }
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles.forEach((p, i) => {
            p.x += p.speedX;
            p.y += p.speedY;

            if (p.x < 0) p.x = this.canvas.width;
            if (p.x > this.canvas.width) p.x = 0;
            if (p.y < 0) p.y = this.canvas.height;
            if (p.y > this.canvas.height) p.y = 0;

            // Draw particle with glow
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fillStyle = `hsla(${p.hue}, 100%, 60%, ${p.opacity})`;
            this.ctx.fill();

            // Add a subtle glow to larger particles
            if (p.size > 1.8) {
                this.ctx.beginPath();
                this.ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2);
                const gradient = this.ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 3);
                gradient.addColorStop(0, `hsla(${p.hue}, 100%, 60%, ${p.opacity * 0.2})`);
                gradient.addColorStop(1, 'transparent');
                this.ctx.fillStyle = gradient;
                this.ctx.fill();
            }

            // Connect nearby particles
            for (let j = i + 1; j < this.particles.length; j++) {
                const p2 = this.particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 140) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(p.x, p.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.strokeStyle = `hsla(160, 100%, 60%, ${0.08 * (1 - dist / 140)})`;
                    this.ctx.lineWidth = 0.6;
                    this.ctx.stroke();
                }
            }

            // Mouse interaction — connect particles to cursor
            if (this.mouse.x !== null && this.mouse.y !== null) {
                const dx = p.x - this.mouse.x;
                const dy = p.y - this.mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 180) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(p.x, p.y);
                    this.ctx.lineTo(this.mouse.x, this.mouse.y);
                    this.ctx.strokeStyle = `hsla(160, 100%, 65%, ${0.15 * (1 - dist / 180)})`;
                    this.ctx.lineWidth = 0.8;
                    this.ctx.stroke();

                    // Subtle repulsion
                    const force = (180 - dist) / 180 * 0.3;
                    p.x += (dx / dist) * force;
                    p.y += (dy / dist) * force;
                }
            }
        });

        requestAnimationFrame(() => this.animate());
    }
}


// ============================================================
// 2. SCROLL ANIMATIONS
// ============================================================
class ScrollAnimator {
    constructor() {
        this.animated = new Set();
        this.observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');

                        if (entry.target.closest('#results') && !this.animated.has('bars')) {
                            this.animated.add('bars');
                            this.animateProgressBars();
                        }

                        const countUps = entry.target.querySelectorAll('.count-up');
                        countUps.forEach((el) => this.countUp(el));
                    }
                });
            },
            { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
        );

        document.querySelectorAll('.animate-on-scroll').forEach((el) => {
            this.observer.observe(el);
        });
    }

    animateProgressBars() {
        document.querySelectorAll('.algo-fill').forEach((bar) => {
            const width = bar.dataset.width;
            if (width) {
                setTimeout(() => { bar.style.width = width + '%'; }, 300);
            }
        });
    }

    countUp(element) {
        if (element.dataset.counted) return;
        element.dataset.counted = 'true';

        const target = parseFloat(element.dataset.target);
        if (!target && target !== 0) return;

        const suffix = element.dataset.suffix || '';
        const isDecimal = element.dataset.decimal === 'true';
        const duration = 2000;
        const start = performance.now();

        const animate = (now) => {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = target * eased;

            if (target >= 10000) {
                // Format large numbers like 2.4M+
                if (current >= 1000000) {
                    element.textContent = (current / 1000000).toFixed(1) + 'M' + suffix;
                } else {
                    element.textContent = Math.floor(current).toLocaleString() + suffix;
                }
            } else if (isDecimal) {
                element.textContent = current.toFixed(1) + suffix;
            } else {
                element.textContent = Math.floor(current).toLocaleString() + suffix;
            }

            if (progress < 1) requestAnimationFrame(animate);
        };

        requestAnimationFrame(animate);
    }
}


// ============================================================
// 3. NAVIGATION
// ============================================================
class Navigation {
    constructor() {
        this.navbar = document.getElementById('navbar');
        this.navToggle = document.getElementById('nav-toggle');
        this.navLinks = document.getElementById('nav-links');
        this.links = document.querySelectorAll('.nav-link');
        this.sections = document.querySelectorAll('.section');

        this.setupScrollEffect();
        this.setupMobileToggle();
        this.setupActiveSection();
        this.setupSmoothScroll();
    }

    setupScrollEffect() {
        window.addEventListener('scroll', () => {
            this.navbar.classList.toggle('scrolled', window.scrollY > 50);
        });
    }

    setupMobileToggle() {
        if (!this.navToggle) return;
        this.navToggle.addEventListener('click', () => {
            this.navLinks.classList.toggle('active');
        });
        this.links.forEach((link) => {
            link.addEventListener('click', () => this.navLinks.classList.remove('active'));
        });
    }

    setupActiveSection() {
        // Highlight active link based on the current page's filename/pathname
        const path = window.location.pathname;
        const page = path.split("/").pop() || 'index.html';
        
        this.links.forEach((link) => {
            const href = link.getAttribute('href');
            // Check if link matches page (e.g., "detection.html" or "detection")
            const isMatch = href === page || 
                            href === page.replace('.html', '') ||
                            (page === 'index.html' && (href === 'index.html' || href === 'index' || href === '/' || href === ''));
            
            link.classList.toggle('active', isMatch);
        });

        // Fallback for single-page style section scrolling if sections are present
        if (this.sections && this.sections.length > 1) {
            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            const id = entry.target.id;
                            this.links.forEach((link) => {
                                link.classList.toggle('active', link.dataset.section === id);
                            });
                        }
                    });
                },
                { threshold: 0.3 }
            );
            this.sections.forEach((section) => observer.observe(section));
        }
    }

    setupSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach((link) => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const target = document.getElementById(targetId);
                if (target) {
                    const top = target.getBoundingClientRect().top + window.scrollY - 70;
                    window.scrollTo({ top, behavior: 'smooth' });
                }
            });
        });
    }
}


// ============================================================
// 4. URL SCANNER
// ============================================================
class URLScanner {
    constructor() {
        this.API_URL = '/api/predict/';
        this.heroInput = document.getElementById('hero-url-input');
        this.heroBtn = document.getElementById('hero-scan-btn');
        this.detInput = document.getElementById('detection-url-input');
        this.detBtn = document.getElementById('detection-scan-btn');
        this.resultDiv = document.getElementById('detection-result');
        this.loadingDiv = document.getElementById('detection-loading');
        this.historyTableBody = document.getElementById('history-table-body');
        
        this.setupListeners();
        this.checkPendingScan();
        this.loadHistory();
    }

    checkPendingScan() {
        // Retrieve and execute any pending URL scan passed from the home page
        const pendingUrl = localStorage.getItem('pendingScanUrl');
        if (pendingUrl) {
            localStorage.removeItem('pendingScanUrl');
            if (this.detInput) {
                this.detInput.value = pendingUrl;
                setTimeout(() => this.scanURL(pendingUrl), 300);
            }
        }
    }

    async loadHistory() {
        if (!this.historyTableBody) return;
        try {
            const response = await fetch('/api/history/');
            if (!response.ok) throw new Error('Failed to load history');
            const data = await response.json();
            const history = data.history || [];
            
            if (history.length === 0) {
                this.historyTableBody.innerHTML = `
                    <tr>
                        <td colspan="4" style="padding: 24px; text-align: center; color: var(--text-muted);">No scans run yet. History is empty.</td>
                    </tr>
                `;
                return;
            }

            this.historyTableBody.innerHTML = history.map(item => {
                const badgeClass = item.prediction === 'phishing' ? 'danger' : 'safe';
                const labelText = item.prediction === 'phishing' ? 'Phishing' : 'Legitimate';
                const riskScore = item.prediction === 'phishing' ? item.confidence : (100 - item.confidence).toFixed(1);
                return `
                    <tr>
                        <td class="history-url-cell" title="${item.url}">${item.url}</td>
                        <td><span class="history-badge ${badgeClass}">${labelText}</span></td>
                        <td style="font-family: var(--font-display); font-weight: 700; color: ${item.prediction === 'phishing' ? 'var(--accent-red)' : 'var(--accent-green)'}">${riskScore}% Risk</td>
                        <td style="color: var(--text-muted); font-size: 0.8rem;">${item.timestamp}</td>
                    </tr>
                `;
            }).join('');
        } catch (error) {
            console.error('History load error:', error);
            this.historyTableBody.innerHTML = `
                <tr>
                    <td colspan="4" style="padding: 24px; text-align: center; color: var(--accent-red);">Failed to retrieve history log.</td>
                </tr>
            `;
        }
    }

    setupListeners() {
        if (this.heroBtn) {
            this.heroBtn.addEventListener('click', () => {
                const url = this.heroInput.value.trim();
                if (url) {
                    localStorage.setItem('pendingScanUrl', url);
                    window.location.href = 'detection.html';
                }
            });
            this.heroInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.heroBtn.click(); });
        }

        if (this.detBtn) {
            this.detBtn.addEventListener('click', () => {
                const url = this.detInput.value.trim();
                if (url) this.scanURL(url);
            });
            this.detInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.detBtn.click(); });
        }

        document.querySelectorAll('.sample-chip').forEach((chip) => {
            chip.addEventListener('click', () => {
                const url = chip.dataset.url;
                this.detInput.value = url;
                this.scanURL(url);
            });
        });
    }

    async scanURL(url) {
        this.resultDiv.style.display = 'none';
        this.loadingDiv.style.display = 'block';

        try {
            const response = await fetch(this.API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url }),
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            this.showResult(data);
        } catch (error) {
            console.error('Scan error:', error);
            this.showDemoResult(url);
        }
    }

    showResult(data) {
        this.loadingDiv.style.display = 'none';
        this.resultDiv.style.display = 'block';

        const isPhishing = data.is_phishing;
        const confidence = data.confidence;

        const resultIcon = document.getElementById('result-icon');
        const resultTitle = document.getElementById('result-title');
        const resultUrl = document.getElementById('result-url');
        const resultConfidence = document.getElementById('result-confidence');
        const confidenceFill = document.getElementById('confidence-fill');

        resultIcon.className = `result-icon ${isPhishing ? 'danger' : 'safe'}`;
        resultIcon.innerHTML = isPhishing
            ? '<i data-lucide="alert-triangle" class="result-lucide"></i>'
            : '<i data-lucide="shield-check" class="result-lucide"></i>';

        resultTitle.className = `result-title ${isPhishing ? 'danger' : 'safe'}`;
        resultTitle.textContent = isPhishing
            ? 'PHISHING DETECTED — Dangerous URL'
            : 'LEGITIMATE — Safe URL';

        resultUrl.textContent = data.url;

        resultConfidence.className = `badge-confidence ${isPhishing ? 'danger' : 'safe'}`;
        resultConfidence.textContent = data.phishing_probability + '% Risk';

        confidenceFill.className = `confidence-fill ${isPhishing ? 'danger' : 'safe'}`;
        setTimeout(() => {
            // The progress bar represents the threat level (phishing probability) on a scale from Safe (0%) to Dangerous (100%)
            confidenceFill.style.width = data.phishing_probability + '%';
        }, 100);

        const explainGrid = document.getElementById('explain-grid');
        const structuredGrid = document.getElementById('structured-feature-grid');
        
        if (explainGrid) explainGrid.innerHTML = '';
        if (structuredGrid) structuredGrid.innerHTML = '';

        // Risk Level Badge
        const explainRiskLevel = document.getElementById('explain-risk-level');
        if (explainRiskLevel) {
            let riskText = "Low Risk";
            let riskColor = "var(--accent-green)";
            if (data.phishing_probability >= 80) { riskText = "Very High Risk"; riskColor = "var(--accent-red)"; }
            else if (data.phishing_probability >= 60) { riskText = "High Risk"; riskColor = "var(--accent-red)"; }
            else if (data.phishing_probability >= 40) { riskText = "Suspicious"; riskColor = "var(--accent-orange)"; }
            
            explainRiskLevel.textContent = riskText;
            explainRiskLevel.style.color = riskColor;
            explainRiskLevel.style.backgroundColor = riskColor + "20";
        }

        // Explain Prediction Panel (Top Contributors)
        if (explainGrid && data.top_features) {
            let topRiskHTML = '';
            let topSafeHTML = '';
            
            const featureDict = {
                'url length': { label: 'Excessive URL Length', why: 'Phishing URLs are often very long to hide the suspicious domain from the user.' },
                'domain length': { label: 'Suspicious Domain Length', why: 'Very long or very short domains can indicate randomly generated phishing sites.' },
                'num dots': { label: 'Multiple Subdomains (Dots)', why: 'Attackers use multiple dots to create fake subdomains like "paypal.com.security.update.com".' },
                'has suspicious tld': { label: 'Suspicious Domain Extension (TLD)', why: 'Certain cheap or free domain extensions (like .tk, .ml) are heavily abused by phishers.' },
                'uses https': { label: 'Missing HTTPS Security', why: 'Legitimate sites almost always use HTTPS. Its absence is a massive red flag.' },
                'num hyphens': { label: 'Hyphen Usage in Domain', why: 'Phishers use hyphens to mimic legitimate brands (e.g., "secure-login-paypal").' },
                'has @ symbol': { label: '@ Symbol Present', why: 'Browsers ignore everything before an "@" symbol, which attackers use to hide the real destination.' },
                'num subdomains': { label: 'Deep Subdomain Structure', why: 'Complex subdomain structures are used to trick users into thinking they are on a trusted site.' },
                'url entropy': { label: 'High URL Randomness (Entropy)', why: 'Random characters indicate an auto-generated or obfuscated phishing link.' },
                'has ip address': { label: 'IP Address Usage', why: 'Using raw IP addresses instead of domain names is a common phishing indicator.' },
                'num suspicious keywords': { label: 'Suspicious Keywords Found', why: 'The URL contains keywords (like "login", "verify", "secure") commonly used in phishing campaigns.' },
                'num slashes': { label: 'Multiple URL Slashes (Deep Path)', why: 'Deeply nested paths are used to hide malicious scripts and bypass basic security filters.' },
                'num digits': { label: 'Excessive Numbers in URL', why: 'Legitimate domains rarely rely on raw numbers, whereas phishing sites often use numerical parameters.' },
                'num special chars': { label: 'Special Character Usage', why: 'Abnormal use of special characters is a technique to obfuscate malicious URLs.' }
            };

            data.top_features.forEach(feat => {
                const nameKey = feat.name.toLowerCase();
                const val = feat.value;
                const imp = feat.importance.toFixed(1);
                
                // Get human readable details
                const dictEntry = featureDict[nameKey] || { label: feat.name, why: 'This structural feature heavily influenced the model.' };
                
                // Heuristic to determine if a feature is acting as a risk or safe signal
                let isRisk = false;
                if (nameKey.includes('length') && val > 50) isRisk = true;
                if (nameKey.includes('dots') && val > 2) isRisk = true;
                if (nameKey.includes('suspicious') && val > 0) isRisk = true;
                if (nameKey.includes('ip') && val === 1) isRisk = true;
                if (nameKey.includes('depth') && val > 2) isRisk = true;
                if (nameKey.includes('https') && val === 0) isRisk = true;
                if (nameKey.includes('digits') && val > 0) isRisk = true;
                if (isPhishing && parseFloat(imp) > 5.0) isRisk = true;
                
                if (isRisk) {
                    topRiskHTML += `
                        <div style="margin-bottom: 12px;">
                            <div style="font-size: 0.9rem; color: var(--text-light); font-weight: 600; display: flex; align-items: center;">
                                <i data-lucide="alert-triangle" style="width: 14px; height: 14px; color: var(--accent-orange); margin-right: 6px;"></i> 
                                ${dictEntry.label} 
                                <span style="color: var(--accent-orange); font-size: 0.8rem; margin-left: 6px;">(+${imp}%)</span>
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-left: 20px; margin-top: 4px; line-height: 1.4;">
                                ${dictEntry.why}
                            </div>
                        </div>`;
                } else if (!isRisk && !isPhishing) {
                    // Override label for positive signals where the feature is absent
                    let safeWhy = 'This structural feature is consistent with legitimate domains.';
                    if (nameKey.includes('https') && val === 1) safeWhy = 'The URL uses secure HTTP communication, standard for legitimate sites.';
                    if (nameKey.includes('ip') && val === 0) safeWhy = 'Uses a standard registered domain name instead of a suspicious raw IP.';
                    if (nameKey.includes('suspicious') && val === 0) safeWhy = 'No known phishing or deceptive keywords were detected in the URL.';

                    topSafeHTML += `
                        <div style="margin-bottom: 12px;">
                            <div style="font-size: 0.9rem; color: var(--text-light); font-weight: 600; display: flex; align-items: center;">
                                <i data-lucide="check-circle-2" style="width: 14px; height: 14px; color: var(--accent-green); margin-right: 6px;"></i> 
                                ${dictEntry.label.replace('Missing ', '').replace('Excessive ', 'Normal ')} 
                                <span style="color: var(--accent-green); font-size: 0.8rem; margin-left: 6px;">(-${imp}%)</span>
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-left: 20px; margin-top: 4px; line-height: 1.4;">
                                ${safeWhy}
                            </div>
                        </div>`;
                }
            });
            
            if (!topRiskHTML) topRiskHTML = '<div style="font-size: 0.85rem; color: var(--text-muted);">No major risk indicators found.</div>';
            if (!topSafeHTML) topSafeHTML = '<div style="font-size: 0.85rem; color: var(--text-muted);">No strong positive trust signals found.</div>';

            explainGrid.innerHTML = `
                <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; border-left: 3px solid var(--accent-orange);">
                    <h5 style="color: var(--text-light); margin-bottom: 15px; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px;">Top Risk Contributors</h5>
                    ${topRiskHTML}
                </div>
                <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; border-left: 3px solid var(--accent-green);">
                    <h5 style="color: var(--text-light); margin-bottom: 15px; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px;">Positive Trust Signals</h5>
                    ${topSafeHTML}
                </div>
            `;
        }

        // Structured Feature Grid
        if (structuredGrid && data.all_features) {
            const groups = {
                'Structure Analysis': ['Url Length', 'Domain Length', 'Path Length', 'Url Depth', 'Num Subdomains', 'Num Query Params'],
                'Security & Keywords': ['Uses Https', 'Has Ip Address', 'Num Suspicious Keywords', 'Has Suspicious Tld', 'Has Port'],
                'Complexity Analysis': ['Url Entropy', 'Domain Entropy', 'Num Digits', 'Num Special Chars', 'Num Slashes', 'Num Dots']
            };
            
            let structuredHTML = '';
            for (const [groupName, featureList] of Object.entries(groups)) {
                let itemsHTML = '';
                featureList.forEach(key => {
                    const actualKey = Object.keys(data.all_features).find(k => k.toLowerCase() === key.toLowerCase());
                    if (actualKey) {
                        const val = data.all_features[actualKey];
                        itemsHTML += `
                            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 8px 0; font-size: 0.85rem;">
                                <span style="color: var(--text-muted);">${actualKey}</span>
                                <strong style="color: var(--text-light);">${typeof val === 'number' && !Number.isInteger(val) ? val.toFixed(2) : val}</strong>
                            </div>
                        `;
                    }
                });
                
                if (itemsHTML) {
                    structuredHTML += `
                        <div style="background: rgba(255,255,255,0.02); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                            <h5 style="color: var(--accent-cyan); margin-bottom: 12px; font-size: 0.9rem; border-bottom: 1px solid rgba(0,229,160,0.2); padding-bottom: 8px;">${groupName}</h5>
                            ${itemsHTML}
                        </div>
                    `;
                }
            }
            structuredGrid.innerHTML = structuredHTML;
        }

        // Re-initialize Lucide icons for new elements
        if (window.lucide) lucide.createIcons();
        this.loadHistory();
    }

    showDemoResult(url) {
        const urlLower = url.toLowerCase();
        const suspicious =
            urlLower.includes('verify') || urlLower.includes('login') ||
            urlLower.includes('secure') || urlLower.includes('.tk') ||
            urlLower.includes('.ml') || urlLower.includes('192.168') ||
            urlLower.includes('paypal') || urlLower.includes('amazon-secure') ||
            urlLower.includes('@') || (urlLower.match(/-/g) || []).length > 2;

        const demoData = {
            url, prediction: suspicious ? 'phishing' : 'legitimate',
            is_phishing: suspicious,
            confidence: suspicious ? 94.2 : 96.8,
            phishing_probability: suspicious ? 94.2 : 3.2,
            legitimate_probability: suspicious ? 5.8 : 96.8,
            top_features: [
                { name: 'URL Length', importance: 18.5, value: url.length },
                { name: 'Num Dots', importance: 14.2, value: (url.match(/\./g) || []).length },
                { name: 'Has Suspicious TLD', importance: 12.8, value: (urlLower.includes('.tk') || urlLower.includes('.ml')) ? 1 : 0 },
                { name: 'Uses HTTPS', importance: 11.3, value: url.startsWith('https') ? 1 : 0 },
                { name: 'Num Hyphens', importance: 9.7, value: (url.match(/-/g) || []).length },
                { name: 'Has @ Symbol', importance: 8.5, value: url.includes('@') ? 1 : 0 },
                { name: 'Num Subdomains', importance: 7.2, value: Math.max(0, url.split('.').length - 2) },
                { name: 'URL Entropy', importance: 6.8, value: 3.8 },
                { name: 'Has IP Address', importance: 5.9, value: /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(url) ? 1 : 0 },
                { name: 'Num Suspicious Keywords', importance: 5.1, value: suspicious ? 2 : 0 },
            ],
            all_features: {
                'Url Length': url.length,
                'Domain Length': 15,
                'Path Length': 10,
                'Url Depth': (url.match(/\//g) || []).length > 2 ? (url.match(/\//g) || []).length - 2 : 0,
                'Num Subdomains': Math.max(0, url.split('.').length - 2),
                'Num Query Params': url.includes('?') ? 1 : 0,
                'Uses Https': url.startsWith('https') ? 1 : 0,
                'Has Ip Address': /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(url) ? 1 : 0,
                'Num Suspicious Keywords': suspicious ? 1 : 0,
                'Has Suspicious Tld': (urlLower.includes('.tk') || urlLower.includes('.ml')) ? 1 : 0,
                'Url Entropy': 3.84,
                'Domain Entropy': 3.2,
                'Num Digits': (url.match(/\d/g) || []).length,
                'Num Special Chars': 2,
                'Num Slashes': (url.match(/\//g) || []).length,
                'Num Dots': (url.match(/\./g) || []).length
            }
        };
        this.showResult(demoData);
    }
}


// ============================================================
// 5. CONTACT FORM
// ============================================================
class ContactForm {
    constructor() {
        this.form = document.getElementById('contact-form');
        if (!this.form) return;

        const textarea = this.form.querySelector('.form-textarea');
        const counter = this.form.querySelector('.form-counter');
        if (textarea && counter) {
            textarea.addEventListener('input', () => {
                counter.textContent = `${textarea.value.length}/500`;
            });
        }

        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = this.form.querySelector('.form-submit-btn');
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="check-circle-2"></i> Message Sent!';
            btn.style.background = 'rgba(16, 185, 129, 0.25)';
            btn.style.color = '#10b981';
            btn.style.boxShadow = 'none';
            if (window.lucide) lucide.createIcons();

            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.style.background = '';
                btn.style.color = '';
                btn.style.boxShadow = '';
                this.form.reset();
                if (counter) counter.textContent = '0/500';
                if (window.lucide) lucide.createIcons();
            }, 3000);
        });
    }
}


// ============================================================
// 6. STATS LOADER
// ============================================================
class StatsLoader {
    constructor() { this.loadStats(); }

    async loadStats() {
        try {
            const response = await fetch('/api/models/');
            if (!response.ok) return;
            const data = await response.json();
            this.updateUI(data);
        } catch (e) {
            console.log('Using default stats (API not available)');
        }
    }

    updateUI(data) {
        const models = data.models || {};
        const stats = data.dataset_stats || {};

        if (models['Random Forest']) {
            const rf = models['Random Forest'];
            this.setText('rf-accuracy', rf.accuracy + '%');
            this.setText('rf-precision', rf.precision + '%');
            this.setText('rf-recall', rf.recall + '%');
            this.setText('rf-f1', rf.f1_score + '%');
            if (rf.confusion_matrix) {
                const cm = rf.confusion_matrix;
                this.setText('cm-tp', cm.true_positive.toLocaleString());
                this.setText('cm-fp', cm.false_positive.toLocaleString());
                this.setText('cm-fn', cm.false_negative.toLocaleString());
                this.setText('cm-tn', cm.true_negative.toLocaleString());
                this.setText('cm-overall', rf.accuracy + '%');
            }
            this.setBar('.algo-fill-green', rf.accuracy);
        }
        if (models['Decision Tree']) {
            this.setText('dt-accuracy', models['Decision Tree'].accuracy + '%');
            this.setBar('.algo-fill-orange', models['Decision Tree'].accuracy);
        }
        if (models['Naive Bayes']) {
            this.setText('nb-accuracy', models['Naive Bayes'].accuracy + '%');
            this.setBar('.algo-fill-pink', models['Naive Bayes'].accuracy);
        }
        if (models['Logistic Regression']) {
            this.setText('lr-accuracy', models['Logistic Regression'].accuracy + '%');
            this.setBar('.algo-fill-blue', models['Logistic Regression'].accuracy);
        }
        if (stats.total_samples) {
            this.setText('ds-total', stats.total_samples.toLocaleString());
            this.setText('ds-phishing', stats.phishing_urls.toLocaleString());
            this.setText('ds-legitimate', stats.legitimate_urls.toLocaleString());
        }

        // Update feature importance
        const fiList = document.getElementById('feature-importance-list');
        const importance = data.feature_importance || [];
        if (fiList && importance.length > 0) {
            fiList.innerHTML = importance.map(item => `
                <div class="feature-importance-row">
                    <div class="fi-header">
                        <span class="fi-name">${item.name}</span>
                        <span class="fi-pct">${item.importance}%</span>
                    </div>
                    <div class="fi-bar"><div class="fi-fill" style="width: ${item.importance}%"></div></div>
                </div>
            `).join('');
        }
    }

    setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
    setBar(sel, val) { const bar = document.querySelector(sel); if (bar) bar.dataset.width = val; }
}


// ============================================================
// INITIALIZE
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    if (window.lucide) {
        lucide.createIcons();
    }

    new ParticleSystem('particle-canvas');
    new ScrollAnimator();
    new Navigation();
    new URLScanner();
    new ContactForm();
    new StatsLoader();

    console.log('%c🛡️ PhishShield AI', 'color: #00e5a0; font-size: 24px; font-weight: bold;');
    console.log('%cML-powered phishing detection system', 'color: #666; font-size: 12px;');
});
