// Client-side OGP loader: replaces top bookmarks links with preview cards.
// - Runs on DOMContentLoaded
// - Processes up to LIMIT links to avoid overwhelming browsers
// - Attempts to fetch target page and extract og: meta tags (CORS may block some requests)
(function () {
    const LIMIT = 200; // number of links to attempt
    const CONCURRENCY = 6;

    function selectAnchors() {
        return Array.from(document.querySelectorAll('dl dt > a'));
    }

    function escapeHtml(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function createCard(a) {
        const url = a.href;
        const title = a.textContent.trim();
        const card = document.createElement('div');
        card.className = 'ogp-card';
        // Simple flat structure: title, description, image (all full-width)
        card.innerHTML = `
            <a class="ogp-link" href="${url}" target="_blank" rel="noopener noreferrer">
                <h3 class="ogp-title">${escapeHtml(title)}</h3>
                <p class="ogp-desc">Loading preview…</p>
                <div class="ogp-thumb"><img src="" alt="" style="display:none"/></div>
            </a>`;
        return card;
    }

    async function fetchMeta(url) {
        try {
            const resp = await fetch(url, { credentials: 'omit' });
            if (!resp.ok) throw new Error('fetch failed');
            const text = await resp.text();
            const doc = new DOMParser().parseFromString(text, 'text/html');
            const get = sel => doc.querySelector(sel)?.getAttribute('content')?.trim();
            const ogTitle = get('meta[property="og:title"]') || get('meta[name="twitter:title"]') || doc.title || '';
            const ogDesc = get('meta[property="og:description"]') || get('meta[name="description"]') || get('meta[name="twitter:description"]') || '';
            const ogImage = get('meta[property="og:image"]') || get('meta[name="twitter:image"]') || '';
            return { ogTitle, ogDesc, ogImage };
        } catch (e) {
            return null;
        }
    }

    async function worker(tasks) {
        for (const task of tasks) {
            const { a, card } = task;
            const meta = await fetchMeta(a.href);
            const link = card.querySelector('.ogp-link');
            const titleEl = link.querySelector('.ogp-title');
            const descEl = link.querySelector('.ogp-desc');
            const imgEl = link.querySelector('.ogp-thumb img');
            if (meta) {
                const title = meta.ogTitle || a.textContent.trim();
                const desc = meta.ogDesc || '';
                titleEl.textContent = title;
                descEl.textContent = desc;
                if (meta.ogImage && imgEl) {
                    imgEl.src = meta.ogImage;
                    imgEl.style.display = 'block';
                } else if (imgEl) {
                    imgEl.style.display = 'none';
                }
            } else {
                if (descEl) descEl.textContent = '';
                if (imgEl) imgEl.style.display = 'none';
            }
        }
    }

    document.addEventListener('DOMContentLoaded', async () => {
        const anchors = selectAnchors();
        const limit = Math.min(LIMIT, anchors.length);
        const tasks = [];
        for (let i = 0; i < limit; i++) {
            const a = anchors[i];
            const dt = a.closest('dt');
            const card = createCard(a);
            // replace DT element visually with card
            try { dt.parentNode.replaceChild(card, dt); } catch (e) { continue; }
            tasks.push({ a, card });
        }

        // process with simple concurrency
        let idx = 0;
        async function runBatch() {
            while (idx < tasks.length) {
                const batch = [];
                for (let i = 0; i < CONCURRENCY && idx < tasks.length; i++, idx++) batch.push(tasks[idx]);
                await worker(batch);
            }
        }
        runBatch().catch(() => { });
    });
})();
