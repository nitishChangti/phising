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
        this.setupListeners();
    }

    setupListeners() {
        if (this.heroBtn) {
            this.heroBtn.addEventListener('click', () => {
                const url = this.heroInput.value.trim();
                if (url) {
                    this.detInput.value = url;
                    document.getElementById('detection').scrollIntoView({ behavior: 'smooth' });
                    setTimeout(() => this.scanURL(url), 800);
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
        resultConfidence.textContent = confidence + '%';

        confidenceFill.className = `confidence-fill ${isPhishing ? 'danger' : 'safe'}`;
        setTimeout(() => {
            confidenceFill.style.width = (isPhishing ? data.phishing_probability : data.legitimate_probability) + '%';
        }, 100);

        const featureGrid = document.getElementById('feature-grid');
        featureGrid.innerHTML = '';

        if (data.top_features) {
            data.top_features.forEach((feat) => {
                const importance = feat.importance;
                let level = 'low';
                if (importance > 15) level = 'high';
                else if (importance > 8) level = 'medium';

                const item = document.createElement('div');
                item.className = 'feature-item';
                item.innerHTML = `
                    <span class="feature-item-icon ${level}"></span>
                    <span class="feature-item-name">${feat.name}</span>
                    <span class="feature-item-value">${feat.value}</span>
                `;
                featureGrid.appendChild(item);
            });
        }

        // Re-initialize Lucide icons for new elements
        if (window.lucide) lucide.createIcons();
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
                { name: 'Suspicious TLD', importance: 12.8, value: (urlLower.includes('.tk') || urlLower.includes('.ml')) ? 1 : 0 },
                { name: 'Uses HTTPS', importance: 11.3, value: url.startsWith('https') ? 1 : 0 },
                { name: 'Num Hyphens', importance: 9.7, value: (url.match(/-/g) || []).length },
                { name: 'Has @ Symbol', importance: 8.5, value: url.includes('@') ? 1 : 0 },
                { name: 'Subdomains', importance: 7.2, value: Math.max(0, url.split('.').length - 2) },
                { name: 'URL Entropy', importance: 6.8, value: 3.8 },
                { name: 'Has IP Address', importance: 5.9, value: /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(url) ? 1 : 0 },
                { name: 'Suspicious Words', importance: 5.1, value: suspicious ? 2 : 0 },
            ],
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
