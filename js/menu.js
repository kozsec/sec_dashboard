const bottomNav = document.getElementById("bottom-nav");

if (bottomNav) {
    bottomNav.innerHTML = `
        <footer>
            Security Watch by koz / セキュリティを、もっと身近に
        </footer>
        <nav class="bottom-nav">
            <a href="/sec_dashboard/" aria-label="Dashboard">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <rect x="3" y="3" width="7" height="7" rx="1"></rect>
                    <rect x="14" y="3" width="7" height="7" rx="1"></rect>
                    <rect x="3" y="14" width="7" height="7" rx="1"></rect>
                    <rect x="14" y="14" width="7" height="7" rx="1"></rect>
                </svg>
            </a>

            <a href="/sec_dashboard/movie.html" aria-label="Movie">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <rect x="3" y="5" width="18" height="14" rx="2"></rect>
                    <polygon points="10,9 10,15 16,12"></polygon>
                </svg>
            </a>

            <a href="/sec_dashboard/post.html" aria-label="Post">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4z"></path>
                    <path d="M13.5 6.5l4 4"></path>
                </svg>
            </a>

            <a href="/sec_dashboard/profile.html" aria-label="Profile">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="12" cy="8" r="4"></circle>
                    <path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"></path>
                </svg>
            </a>
        </nav>
    `;
}
