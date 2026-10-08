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

            <a href="/sec_dashboard/toy.html" aria-label="Toy">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M7 8h10a4 4 0 0 1 3.8 5.2l-1.1 4a2 2 0 0 1-3.7.4L14.8 15H9.2l-1.2 2.6a2 2 0 0 1-3.7-.4l-1.1-4A4 4 0 0 1 7 8z"></path>
                    <path d="M7 11v4"></path>
                    <path d="M5 13h4"></path>
                    <circle cx="16.5" cy="12" r="1"></circle>
                    <circle cx="18.5" cy="14" r="1"></circle>
                </svg>
            </a>

             <a href="/sec_dashboard/link.html" aria-label="Link">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M10 13a5 5 0 0 0 7.1 0l2-2a5 5 0 0 0-7.1-7.1l-1.2 1.2"></path>
                    <path d="M14 11a5 5 0 0 0-7.1 0l-2 2A5 5 0 0 0 12 20.1l1.2-1.2"></path>
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
