const roadmapData = [
    {
        title: "آشنایی با مفاهیم اولیه",
        description: "یادگیری HTML و CSS پایه",
        status: "completed",
        details: "در این مرحله، شما با ساختار وب و استایل‌دهی آشنا می‌شوید. مفاهیم HTML مانند تگ‌ها، ویژگی‌ها و ساختار صفحه و همچنین CSS برای طراحی ظاهر صفحات وب شامل رنگ‌ها، فونت‌ها و چیدمان را یاد خواهید گرفت."
    },
    {
        title: "جاوااسکریپت مقدماتی",
        description: "آشنایی با متغیرها، توابع و DOM",
        status: "completed",
        details: "این بخش به یادگیری اصول اولیه جاوااسکریپت اختصاص دارد. شما با متغیرها، انواع داده‌ها، توابع، حلقه‌ها و نحوه تعامل با DOM برای دستکاری محتوای صفحات وب آشنا می‌شوید."
    },
    {
        title: "جاوااسکریپت پیشرفته",
        description: "کار با APIها و برنامه‌نویسی غیرهمزمان",
        status: "current",
        details: "در این مرحله، مفاهیم پیشرفته جاوااسکریپت مانند برنامه‌نویسی غیرهمزمان (Promises و async/await)، کار با APIها برای دریافت داده‌های خارجی، و مدیریت رویدادهای پیچیده را یاد خواهید گرفت."
    },
    {
        title: "فریم‌ورک‌های فرانت‌اند",
        description: "یادگیری React یا Vue",
        status: "pending",
        details: "این بخش به یادگیری فریم‌ورک‌های مدرن فرانت‌اند مانند React یا Vue اختصاص دارد. شما با مفاهیم کامپوننت‌ها، مدیریت حالت، و ساخت رابط‌های کاربری پویا و مقیاس‌پذیر آشنا خواهید شد."
    },
    {
        title: "پروژه نهایی",
        description: "ساخت یک اپلیکیشن کامل",
        status: "pending",
        details: "در این مرحله، تمام مهارت‌های خود را در یک پروژه واقعی به کار خواهید گرفت. شما یک اپلیکیشن وب کامل طراحی و پیاده‌سازی خواهید کرد که شامل فرانت‌اند، تعامل با APIها و طراحی کاربرپسند است."
    }
];

const videoData = [
    {
        title: "ویدیو ۱",
        description: "معرفی دوره",
        duration: "۵ دقیقه",
        src: "assets/videos/video.mp4",
        watched: false
    },
    {
        title: "ویدیو ۲",
        description: "مفاهیم اولیه",
        duration: "۸ دقیقه",
        src: "assets/videos/video.mp4",
        watched: false
    },
    {
        title: "ویدیو ۳",
        description: "تمرین عملی",
        duration: "۱۰ دقیقه",
        src: "assets/videos/video.mp4",
        watched: false
    },
    {
        title: "ویدیو ۴",
        description: "جمع‌بندی",
        duration: "۷ دقیقه",
        src: "assets/videos/video.mp4",
        watched: false
    }
];

const resourceData = [
    {
        session: "جلسه ۱: معرفی HTML",
        chapter: "فصل ۱: مفاهیم اولیه",
        links: [
            { title: "مستندات MDN برای HTML", url: "https://developer.mozilla.org/en-US/docs/Web/HTML" },
            { title: "آموزش W3Schools HTML", url: "https://www.w3schools.com/html/" }
        ]
    },
    {
        session: "جلسه ۲: استایل‌دهی با CSS",
        chapter: "فصل ۱: مفاهیم اولیه",
        links: [
            { title: "مستندات MDN برای CSS", url: "https://developer.mozilla.org/en-US/docs/Web/CSS" },
            { title: "CSS Tricks", url: "https://css-tricks.com/" }
        ]
    },
    {
        session: "جلسه ۳: جاوااسکریپت مقدماتی",
        chapter: "فصل ۲: جاوااسکریپت",
        links: [
            { title: "مستندات MDN برای جاوااسکریپت", url: "https://developer.mozilla.org/en-US/docs/Web/JavaScript" }
        ]
    },
    {
        session: "جلسه ۴: کار با APIها",
        chapter: "فصل ۳: جاوااسکریپت پیشرفته",
        links: [
            { title: "آموزش Fetch API", url: "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API" },
            { title: "مقاله async/await", url: "https://javascript.info/async-await" }
        ]
    }
];

function renderRoadmap() {
    const roadmapContainer = document.getElementById('roadmap');
    if (!roadmapContainer) return;

    roadmapContainer.innerHTML = '';
    roadmapData.forEach((step, index) => {
        const stepElement = document.createElement('div');
        stepElement.className = `step ${step.status}`;
        stepElement.innerHTML = `
            <div class="step-title">${step.title}</div>
            <div class="step-description">${step.description}</div>
        `;
        stepElement.onclick = () => openModal(step);
        roadmapContainer.appendChild(stepElement);
    });
}

function openModal(step) {
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalDescription = document.getElementById('modal-description');
    const modalDetails = document.getElementById('modal-details');

    if (!modal || !modalTitle || !modalDescription || !modalDetails) return;

    modalTitle.textContent = step.title;
    modalDescription.textContent = step.description;
    modalDetails.textContent = step.details;
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) modal.style.display = 'none';
}

function renderVideos() {
    const videoGrid = document.getElementById('videoGrid');
    if (!videoGrid) return;

    videoGrid.innerHTML = '';
    videoData.forEach((video, index) => {
        const videoItem = document.createElement('div');
        videoItem.className = `video-item ${video.watched ? 'watched' : ''}`;
        videoItem.innerHTML = `
            <h3>${video.title}</h3>
            <div class="metadata">${video.description} - ${video.duration}</div>
            <video width="100%" height="200" controls>
                <source src="${video.src}" type="video/mp4">
                مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند.
            </video>
            <div class="video-buttons">
                <a href="${video.src}" download class="download-btn">دانلود ویدیو</a>
                <button class="watched-btn ${video.watched ? 'watched' : ''}" onclick="toggleWatched(${index})">
                    ${video.watched ? 'تماشا شده' : 'علامت‌گذاری به‌عنوان تماشا شده'}
                </button>
            </div>
        `;
        videoGrid.appendChild(videoItem);
    });
}

function toggleWatched(index) {
    videoData[index].watched = !videoData[index].watched;
    renderVideos();
}

function renderResources() {
    const resourceList = document.getElementById('resourceList');
    if (!resourceList) return;

    resourceList.innerHTML = '';
    resourceData.forEach((resource) => {
        const resourceItem = document.createElement('div');
        resourceItem.className = 'resource-item';
        resourceItem.innerHTML = `
            <h3>${resource.session}</h3>
            <div class="chapter">${resource.chapter}</div>
            <div class="links">
                ${resource.links.map(link => `<a href="${link.url}" target="_blank">${link.title}</a>`).join('')}
            </div>
        `;
        resourceList.appendChild(resourceItem);
    });
}

function toggleNotifications() {
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) dropdown.classList.toggle('active');
}

window.onclick = function(event) {
    const modal = document.getElementById('modal');
    const dropdown = document.getElementById('notificationDropdown');
    if (modal && event.target === modal) {
        closeModal();
    }
    if (dropdown && !event.target.closest('.notifications') && dropdown.classList.contains('active')) {
        dropdown.classList.remove('active');
    }
};

window.onload = function() {
    renderRoadmap();
    renderVideos();
    renderResources();
};

const dateBox = document.getElementById('today-date');
const today = new Date().toLocaleDateString('fa-IR-u-nu-latn', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});
dateBox.textContent = `امروز: ${today}`;
