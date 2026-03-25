/* 19 VPN — Гимназия ОдинДевять */

// ─── Navbar ──────────────────────────────
const navbar = document.getElementById('navbar');
if (navbar) {
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
    });
}

function toggleNav() {
    const links = document.getElementById('navLinks');
    if (links) links.classList.toggle('open');
}

// ─── Auth Modals ─────────────────────────
function showModal(type) {
    const overlay = document.getElementById('authModal');
    if (!overlay) return;
    overlay.classList.add('active');
    document.getElementById('loginForm').style.display = type === 'login' ? 'block' : 'none';
    document.getElementById('registerForm').style.display = type === 'register' ? 'block' : 'none';
    const firstInput = overlay.querySelector('div[style*="block"] input');
    if (firstInput) setTimeout(() => firstInput.focus(), 100);
}

function closeModal() {
    const overlay = document.getElementById('authModal');
    if (overlay) overlay.classList.remove('active');
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
        closeKeyModal();
    }
});

// close modal on backdrop click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        closeModal();
        closeKeyModal();
    }
});

// ─── FAQ Accordion ───────────────────────
function toggleFaq(el) {
    const item = el.parentElement;
    const wasOpen = item.classList.contains('open');

    document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));

    if (!wasOpen) item.classList.add('open');
}

// ─── Toast Notifications ─────────────────
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4200);
}

// ─── Dashboard: Key Details ──────────────
async function showKeyDetails(keyId) {
    try {
        const res = await fetch(`/dashboard/key/${keyId}`);
        const data = await res.json();
        if (data.error) { showToast(data.error, 'error'); return; }

        const modal = document.getElementById('keyModal');
        if (!modal) return;

        document.getElementById('keyDeviceName').textContent = data.device_name;
        document.getElementById('keyPlatform').textContent = data.platform;
        document.getElementById('keyIP').textContent = data.ip || 'Pending';
        document.getElementById('keyConfig').textContent = data.config || 'No config available';
        document.getElementById('keyCreated').textContent = formatDate(data.created);

        const qrEl = document.getElementById('keyQR');
        if (data.qr_base64) {
            qrEl.innerHTML = `<img src="data:image/png;base64,${data.qr_base64}" alt="QR Code"><p class="text-muted mt-1" style="font-size:12px">Сканируй в WireGuard на телефоне</p>`;
            qrEl.style.display = 'block';
        } else {
            qrEl.innerHTML = '<p class="text-muted" style="font-size:13px">QR-код появится когда сервер подключён</p>';
            qrEl.style.display = 'block';
        }

        modal.classList.add('active');
    } catch (err) {
        console.error(err);
        showToast('Ошибка загрузки ключа', 'error');
    }
}

function closeKeyModal() {
    const modal = document.getElementById('keyModal');
    if (modal) modal.classList.remove('active');
}

function copyConfig() {
    const el = document.getElementById('keyConfig');
    if (!el) return;
    navigator.clipboard.writeText(el.textContent).then(() => {
        showToast('Конфиг скопирован!');
    }).catch(() => {
        const range = document.createRange();
        range.selectNode(el);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand('copy');
        showToast('Конфиг скопирован!');
    });
}

function downloadConfig() {
    const el = document.getElementById('keyConfig');
    const name = document.getElementById('keyDeviceName');
    if (!el) return;
    const blob = new Blob([el.textContent], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `19vpn_${(name?.textContent || 'device').replace(/\s/g, '_')}.conf`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Конфиг скачан!');
}

// ─── Date Formatting ─────────────────────
function formatDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString('ru-RU', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

// ─── Scroll Animations ──────────────────
const animObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                entry.target.style.animationDelay = `${i * 0.08}s`;
                entry.target.classList.add('animate-in');
                animObserver.unobserve(entry.target);
            }
        });
    },
    { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
);

document.querySelectorAll(
    '.feature-card, .pricing-card, .step, .faq-item, .download-card, .testimonial-card, .dash-stat-card, .admin-stat'
).forEach(el => animObserver.observe(el));

// ─── Smooth scroll for anchor links ─────
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
        const id = a.getAttribute('href');
        if (id === '#') return;
        const target = document.querySelector(id);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            const navLinks = document.getElementById('navLinks');
            if (navLinks) navLinks.classList.remove('open');
        }
    });
});
