// custom_admin.js - Custom Admin Panel Enhancements
// Initialize custom admin panel functionality
document.addEventListener("DOMContentLoaded", function() {
    console.log("پنل مدیریت سفارشی لود شد! 🌱");

    // Update page title with custom branding
    document.title = "🎓 پنل مدیریت اختصاصی من";

    // Add custom styles to admin panel
    const style = document.createElement('style');
    style.textContent = `
        /* Custom Admin Panel Styling */
        body {
            font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            direction: rtl;
            background-color: #f5f7fa;
        }

        .admin-header {
            background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .admin-nav {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .admin-nav a {
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            color: #2c3e50;
            transition: all 0.3s ease;
        }

        .admin-nav a:hover {
            background-color: #3498db;
            color: white;
        }

        .admin-section {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
    `;
    document.head.appendChild(style);

    // Create custom header
    const header = document.createElement('div');
    header.className = 'admin-header';
    header.innerHTML = `
        <h1>پنل مدیریت پیشرفته</h1>
        <p>خوش آمدید به سیستم مدیریت اختصاصی</p>
    `;
    document.body.insertBefore(header, document.body.firstChild);

    // Create navigation menu
    const nav = document.createElement('nav');
    nav.className = 'admin-nav';
    nav.innerHTML = `
        <a href="#dashboard">داشبورد</a>
        <a href="#users">کاربران</a>
        <a href="#settings">تنظیمات</a>
        <a href="#reports">گزارشات</a>
    `;
    document.body.insertBefore(nav, document.body.children[1]);

    // Smooth scroll for navigation
    document.querySelectorAll('.admin-nav a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            alert('ذخیره تغییرات با موفقیت انجام شد!');
        }
    });

    // Add responsive behavior
    const checkResponsive = () => {
        const nav = document.querySelector('.admin-nav');
        if (window.innerWidth < 768) {
            nav.style.flexDirection = 'column';
        } else {
            nav.style.flexDirection = 'row';
        }
    };

    window.addEventListener('resize', checkResponsive);
    checkResponsive();

    // Add loading animation for async operations
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'loading-overlay';
    loadingOverlay.style.cssText = `
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 1000;
        align-items: center;
        justify-content: center;
    `;
    loadingOverlay.innerHTML = `
        <div style="background: white; padding: 1rem; border-radius: 8px;">
            <p>در حال بارگذاری...</p>
        </div>
    `;
    document.body.appendChild(loadingOverlay);

    // Function to show/hide loading overlay
    window.showLoading = () => {
        document.getElementById('loading-overlay').style.display = 'flex';
    };
    window.hideLoading = () => {
        document.getElementById('loading-overlay').style.display = 'none';
    };
});