// RUDRAM Client Application Core
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Lucide Icons
    if (window.lucide) {
        lucide.createIcons();
    }

    initThemeToggle();
    initCookieBanner();
    initPageUtilities();

    // 2. Browser Geolocation Handling
    initUserLocation();

    // 3. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // 4. Global Demo Scenario Trigger
    const startDemoBtns = document.querySelectorAll('.btn-start-demo');
    startDemoBtns.forEach(btn => {
        btn.addEventListener('click', () => runEmergencyDemo());
    });

    // 5. Navbar Location Search Event Listener & Autocomplete
    const navSearchForm = document.getElementById('navLocationSearchForm');
    if (navSearchForm) {
        navSearchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            e.stopPropagation();
            handleNavLocationSearchSubmit(e);
            return false;
        });
        setupNavSearchAutocomplete();
    }
});

let navSearchDebounceTimer = null;
let navSearchAbortController = null;

function setupNavSearchAutocomplete() {
    const inputEl = document.getElementById('navSearchInput');
    const autocompleteEl = document.getElementById('navSearchAutocomplete');
    if (!inputEl || !autocompleteEl) return;

    inputEl.addEventListener('input', () => {
        const query = inputEl.value.trim();
        if (query.length < 2) {
            autocompleteEl.style.display = 'none';
            autocompleteEl.innerHTML = '';
            inputEl.setAttribute('aria-expanded', 'false');
            return;
        }

        const pageMatches = getSiteSearchPages()
            .filter(page => page.label.toLowerCase().includes(query.toLowerCase()))
            .slice(0, 5);
        renderNavSearchResults(autocompleteEl, pageMatches, []);

        clearTimeout(navSearchDebounceTimer);
        navSearchDebounceTimer = setTimeout(async () => {
            if (navSearchAbortController) {
                navSearchAbortController.abort();
            }
            navSearchAbortController = new AbortController();

            try {
                const res = await fetch(`/api/location/search/?q=${encodeURIComponent(query)}`, {
                    signal: navSearchAbortController.signal
                });
                const data = await res.json();
                const locations = res.ok && data.success && Array.isArray(data.results) ? data.results : [];
                renderNavSearchResults(autocompleteEl, pageMatches, locations, locations.length ? '' : 'No India locations matched.');
            } catch (err) {
                if (err.name !== 'AbortError') {
                    renderNavSearchResults(autocompleteEl, pageMatches, [], 'Location search is temporarily unavailable.');
                }
            }
        }, 300);
    });

    document.addEventListener('click', (e) => {
        if (!inputEl.contains(e.target) && !autocompleteEl.contains(e.target)) {
            autocompleteEl.style.display = 'none';
            inputEl.setAttribute('aria-expanded', 'false');
        }
    });
}

function getSiteSearchPages() {
    const seen = new Set();
    return Array.from(document.querySelectorAll('#mobileNavOffcanvas a[href]'))
        .map(link => ({
            label: link.textContent.trim().replace(/\s+/g, ' '),
            href: link.getAttribute('href')
        }))
        .filter(page => {
            if (!page.label || !page.href || page.href.startsWith('#') || seen.has(page.href)) return false;
            seen.add(page.href);
            return true;
        });
}

function renderNavSearchResults(container, pages, locations, emptyMessage = '') {
    container.replaceChildren();

    if (pages.length) {
        const heading = document.createElement('h6');
        heading.className = 'dropdown-header';
        heading.textContent = 'Pages';
        container.appendChild(heading);

        pages.forEach(page => {
            const link = document.createElement('a');
            link.className = 'dropdown-item py-2';
            link.href = page.href;
            link.setAttribute('role', 'option');
            link.textContent = page.label;
            container.appendChild(link);
        });
    }

    if (locations.length) {
        const heading = document.createElement('h6');
        heading.className = 'dropdown-header';
        heading.textContent = 'Locations';
        container.appendChild(heading);

        locations.slice(0, 5).forEach(location => {
            const button = document.createElement('button');
            const placeName = location.place_name || location.name || location.display_name || 'Location';
            button.type = 'button';
            button.className = 'dropdown-item py-2 text-start w-100';
            button.setAttribute('role', 'option');
            button.addEventListener('click', () => selectNavSearchResult(location));

            const title = document.createElement('strong');
            title.className = 'd-block text-info';
            title.textContent = placeName;
            button.appendChild(title);

            const address = document.createElement('span');
            address.className = 'd-block text-secondary small text-wrap';
            address.textContent = location.display_name || '';
            button.appendChild(address);
            container.appendChild(button);
        });
    }

    if (!pages.length && !locations.length) {
        const status = document.createElement('div');
        status.className = 'p-2 text-muted text-center small';
        status.textContent = emptyMessage || 'No matching pages or locations found.';
        container.appendChild(status);
    }

    container.style.display = 'block';
    const input = document.getElementById('navSearchInput');
    if (input) input.setAttribute('aria-expanded', 'true');
}

function selectNavSearchResult(geoData) {
    const inputEl = document.getElementById('navSearchInput');
    const autocompleteEl = document.getElementById('navSearchAutocomplete');
    const placeName = geoData.place_name || geoData.name || geoData.display_name || 'Location';
    if (inputEl) {
        inputEl.value = placeName;
        inputEl.setAttribute('aria-expanded', 'false');
    }
    if (autocompleteEl) autocompleteEl.style.display = 'none';

    const locName = geoData.display_name || geoData.place_name;
    const lat = geoData.latitude;
    const lon = geoData.longitude;

    sessionStorage.setItem('rudram_searched_name', locName);
    sessionStorage.setItem('rudram_searched_lat', lat);
    sessionStorage.setItem('rudram_searched_lon', lon);

    const locBadge = document.getElementById('userLocationDisplay');
    if (locBadge) {
        locBadge.innerHTML = `<span class="badge bg-info text-dark fw-bold me-1">SEARCH</span> ${placeName}`;
    }

    showToast(`📍 Location: ${locName}`, 'success');

    if (typeof window.handleSearchedLocation === 'function') {
        window.handleSearchedLocation(geoData);
    } else {
        window.location.href = `/dashboard/?lat=${lat}&lon=${lon}&name=${encodeURIComponent(locName)}`;
    }
}

async function handleNavLocationSearchSubmit(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const inputEl = document.getElementById('navSearchInput');
    const btnEl = document.getElementById('btnNavSearch');
    if (!inputEl) return false;

    const query = inputEl.value.trim();
    if (!query) return false;

    const matchingPage = getSiteSearchPages().find(page => page.label.toLowerCase() === query.toLowerCase())
        || getSiteSearchPages().find(page => page.label.toLowerCase().includes(query.toLowerCase()));
    if (matchingPage) {
        window.location.assign(matchingPage.href);
        return false;
    }

    if (btnEl) {
        btnEl.disabled = true;
        btnEl.innerHTML = '<span class="spinner-border spinner-border-sm" style="width: 12px; height: 12px;"></span>';
    }

    try {
        const res = await fetch(`/api/location/search/?q=${encodeURIComponent(query)}`);
        const data = await res.json();

        if (res.ok && data.success && data.results && data.results.length > 0) {
            selectNavSearchResult(data.results[0]);
        } else if (res.ok && data.success && data.latitude && data.longitude) {
            selectNavSearchResult(data);
        } else {
            showToast(data.message || 'Location search failed. No matching place found.', 'error');
        }
    } catch (err) {
        console.error('Navbar search error:', err);
        showToast('Network error while searching location.', 'error');
    } finally {
        if (btnEl) {
            btnEl.disabled = false;
            btnEl.innerHTML = '<i data-lucide="search" style="width: 14px; height: 14px;"></i>';
            if (window.lucide) lucide.createIcons();
        }
    }
    return false;
}

function initUserLocation() {
    const locBadge = document.getElementById('userLocationDisplay');
    if (!navigator.geolocation) {
        if (locBadge) locBadge.innerHTML = '<i data-lucide="map-pin" class="me-1"></i> Bhubaneswar, Odisha (Demo Default)';
        return;
    }

    // Check localStorage or request
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude.toFixed(4);
            const lon = position.coords.longitude.toFixed(4);
            sessionStorage.setItem('rudram_lat', lat);
            sessionStorage.setItem('rudram_lon', lon);
            if (locBadge) {
                locBadge.innerHTML = `<span class="badge bg-success me-1">GPS</span> Lat: ${lat}, Lon: ${lon}`;
            }
        },
        (error) => {
            // Permission denied or error
            console.log('Location permission info:', error.message);
            if (locBadge) {
                locBadge.innerHTML = `<span class="badge badge-demo me-1">DEMO GPS</span> Bhubaneswar, Odisha (20.2961, 85.8245)`;
            }
            sessionStorage.setItem('rudram_lat', '20.2961');
            sessionStorage.setItem('rudram_lon', '85.8245');
        },
        { timeout: 5000 }
    );
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const toastEl = document.createElement('div');
    const toastType = { error: 'danger', success: 'success', warning: 'warning', info: 'primary' }[type] || 'primary';
    toastEl.className = `toast align-items-center text-white bg-${toastType} border-0 show mb-2`;
    toastEl.setAttribute('role', 'alert');
    const content = document.createElement('div');
    content.className = 'd-flex';
    const body = document.createElement('div');
    body.className = 'toast-body';
    body.textContent = message;
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close notification');
    content.append(body, closeButton);
    toastEl.appendChild(content);
    toastContainer.appendChild(toastEl);
    setTimeout(() => toastEl.remove(), 4500);
}

async function runEmergencyDemo() {
    const btn = document.getElementById('btnStartDemoScenario');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Simulating Scenario...';
    }

    try {
        const response = await fetch('/api/demo/run-scenario/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ intensity: 'CRITICAL' })
        });
        const data = await response.json();
        if (data.success) {
            showToast('🚨 Flood Emergency Demo Triggered! Reloading incident room...', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1200);
        } else {
            showToast('Demo execution error: ' + (data.error || 'Unknown error'), 'error');
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '⚡ START FLOOD EMERGENCY DEMO';
            }
        }
    } catch (e) {
        showToast('Network error triggering demo scenario', 'error');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '⚡ START FLOOD EMERGENCY DEMO';
        }
    }
}

function initThemeToggle() {
            const toggle = document.getElementById('themeToggle');
            const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
            applyRudramTheme(currentTheme, false);

            if (toggle) {
                toggle.addEventListener('click', () => {
                    const nextTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                    applyRudramTheme(nextTheme, true);
                });
            }
        }

        function applyRudramTheme(theme, persist = true) {
            const selectedTheme = theme === 'dark' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', selectedTheme);
            document.documentElement.setAttribute('data-bs-theme', selectedTheme);
            if (persist) localStorage.setItem('rudram_theme', selectedTheme);
            updateThemeToggleButton();
        }

        function updateThemeToggleButton() {
            const toggle = document.getElementById('themeToggle');
            if (!toggle) return;

            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            const label = isDark ? 'Switch to light mode' : 'Switch to dark mode';
            toggle.setAttribute('aria-label', label);
            toggle.setAttribute('title', label);
            toggle.innerHTML = `<i data-lucide="${isDark ? 'sun' : 'moon'}" style="width: 16px; height: 16px;" aria-hidden="true"></i><span class="visually-hidden">${label}</span>`;
            if (window.lucide) lucide.createIcons();
        }

        window.updateRudramThemeToggle = updateThemeToggleButton;

        function initCookieBanner() {
            const banner = document.getElementById('cookieBanner');
            const acceptButton = document.getElementById('cookieAcceptTracking');
            const essentialButton = document.getElementById('cookieEssentialOnly');
            if (!banner || !acceptButton || !essentialButton) return;

            const consent = localStorage.getItem('rudram_cookie_consent');
            banner.hidden = consent === 'accepted' || consent === 'essential';
            if (consent === 'accepted') captureUtmParameters();

            acceptButton.addEventListener('click', () => {
                localStorage.setItem('rudram_cookie_consent', 'accepted');
                banner.hidden = true;
                captureUtmParameters();
            });

            essentialButton.addEventListener('click', () => {
                localStorage.setItem('rudram_cookie_consent', 'essential');
                document.cookie = 'rudram_utm=; Max-Age=0; Path=/; SameSite=Lax';
                banner.hidden = true;
            });
        }

        function captureUtmParameters() {
            const params = new URLSearchParams(window.location.search);
            const campaign = {};
            ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach(key => {
                const value = params.get(key);
                if (value) campaign[key] = value.slice(0, 200);
            });

            if (!Object.keys(campaign).length) return;

            const secure = window.location.protocol === 'https:' ? '; Secure' : '';
            document.cookie = `rudram_utm=${encodeURIComponent(JSON.stringify(campaign))}; Max-Age=2592000; Path=/; SameSite=Lax${secure}`;
        }

        function initPageUtilities() {
            const progress = document.getElementById('scrollProgress');
            const progressBar = progress ? progress.querySelector('span') : null;
            const backToTop = document.getElementById('backToTop');
            const loadingIndicator = document.getElementById('pageLoadingIndicator');
            const confirmModalElement = document.getElementById('confirmationModal');
            const confirmMessage = document.getElementById('confirmationMessage');
            const confirmButton = document.getElementById('confirmActionButton');
            let pendingForm = null;

            const updateScrollState = () => {
                const scrollable = document.documentElement.scrollHeight - window.innerHeight;
                const percent = scrollable > 0 ? Math.min(100, Math.round((window.scrollY / scrollable) * 100)) : 0;
                if (progressBar) progressBar.style.transform = `scaleX(${percent / 100})`;
                if (progress) progress.setAttribute('aria-valuenow', String(percent));
                if (backToTop) backToTop.hidden = window.scrollY < 320;
            };

            updateScrollState();
            window.addEventListener('scroll', updateScrollState, { passive: true });
            window.addEventListener('resize', updateScrollState);

            if (backToTop) {
                backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
            }

            const copyButton = document.getElementById('copyPageLink');
            if (copyButton) {
                copyButton.addEventListener('click', async () => {
                    try {
                        if (!navigator.clipboard || !navigator.clipboard.writeText) {
                            throw new Error('Clipboard access is unavailable in this browser.');
                        }
                        await navigator.clipboard.writeText(window.location.href);
                        showToast('Page link copied to clipboard.', 'success');
                    } catch (error) {
                        console.error('Could not copy the page link:', error);
                        showToast('Could not copy the page link. Check clipboard permissions and try again.', 'error');
                    }
                });
            }

            const startLoading = () => {
                if (loadingIndicator) loadingIndicator.classList.add('is-active');
            };
            const stopLoading = () => {
                if (loadingIndicator) loadingIndicator.classList.remove('is-active');
            };

            window.addEventListener('pageshow', stopLoading);
            document.addEventListener('click', event => {
                const link = event.target.closest('a[href]');
                if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
                if (link.target === '_blank' || link.hasAttribute('download')) return;

                const destination = new URL(link.href, window.location.href);
                if (destination.origin !== window.location.origin) return;
                if (destination.pathname === window.location.pathname && destination.search === window.location.search) return;
                startLoading();
            });

            document.addEventListener('invalid', event => {
                if (event.target.form) event.target.form.classList.add('was-validated');
            }, true);

            document.addEventListener('submit', event => {
                const form = event.target;
                if (!(form instanceof HTMLFormElement)) return;
                form.classList.add('was-validated');

                if (form.dataset.confirm && form.dataset.confirmed !== 'true') {
                    event.preventDefault();
                    pendingForm = form;
                    if (confirmMessage) confirmMessage.textContent = form.dataset.confirm;
                    if (confirmModalElement && window.bootstrap) {
                        bootstrap.Modal.getOrCreateInstance(confirmModalElement).show();
                    }
                    return;
                }

                if (!event.defaultPrevented) startLoading();
                if (form.dataset.confirmed === 'true') delete form.dataset.confirmed;
            });

            if (confirmButton && confirmModalElement) {
                confirmButton.addEventListener('click', () => {
                    if (!pendingForm) return;
                    const form = pendingForm;
                    pendingForm = null;
                    form.dataset.confirmed = 'true';
                    bootstrap.Modal.getOrCreateInstance(confirmModalElement).hide();
                    if (typeof form.requestSubmit === 'function') form.requestSubmit();
                    else form.submit();
                });
                confirmModalElement.addEventListener('hidden.bs.modal', () => {
                    pendingForm = null;
                });
            }
        }
