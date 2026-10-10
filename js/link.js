
fetch("config/link.json")
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(links => {
        const ITEMS_PER_PAGE = 5;
        let currentPage = 1;
        const container = document.getElementById("link-list");

        const search = document.createElement("input");
        search.type = "search";
        search.className = "link-search";
        search.placeholder = "キーワードで検索";
        search.setAttribute("aria-label", "リンクをキーワードで検索");

        const filters = document.createElement("div");
        filters.className = "link-filters";

        const selected = {
            category: new Set(),
            topics: new Set(),
            region: new Set()
        };

        const filterDefinitions = [
            { key: "region", label: "地域" },
            { key: "category", label: "カテゴリ" },
            { key: "topics", label: "技術・目的" }
            
        ];

        filterDefinitions.forEach(({ key, label }) => {
            const section = document.createElement("section");
            section.className = "link-filter-section";

            const heading = document.createElement("h3");
            heading.textContent = label;

            const options = document.createElement("div");
            options.className = "link-tag-filters";

            const values = [...new Set(
                links.flatMap(link => {
                    const value = link[key];
                    return Array.isArray(value)
                        ? value
                        : value
                            ? [value]
                            : [];
                })
            )].sort((a, b) => a.localeCompare(b, "ja"));

            values.forEach(value => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "link-tag-filter";
                button.textContent = value;
                button.setAttribute("aria-pressed", "false");

                button.addEventListener("click", () => {
                    if (selected[key].has(value)) {
                        selected[key].delete(value);
                    } else {
                        selected[key].add(value);
                    }

                    button.classList.toggle(
                        "is-selected",
                        selected[key].has(value)
                    );
                    button.setAttribute(
                        "aria-pressed",
                        String(selected[key].has(value))
                    );

                    render();
                });

                options.appendChild(button);
            });

            section.append(heading, options);
            filters.appendChild(section);
        });

        const controls = document.createElement("div");
        controls.className = "link-filter-controls";

        const clearButton = document.createElement("button");
        clearButton.type = "button";
        clearButton.textContent = "条件をクリア ↺";
        clearButton.className = "link-filter-clear";

        clearButton.addEventListener("click", () => {
            Object.values(selected).forEach(set => set.clear());

            filters.querySelectorAll("button").forEach(button => {
                button.classList.remove("is-selected");
                button.setAttribute("aria-pressed", "false");
            });

            search.value = "";
            render();
        });

        controls.appendChild(clearButton);

        const count = document.createElement("p");
        count.className = "link-count";

        const wrapper = document.createElement("div");
        wrapper.className = "link-table-wrapper";
        
        const pagination = document.createElement("div");
        pagination.className = "pagination";

        const table = document.createElement("table");
        table.className = "link-table";

        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");

        ["タイトル", "公開組織", "分類", "最終確認日"].forEach(label => {
            const th = document.createElement("th");
            th.textContent = label;
            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);

        const tbody = document.createElement("tbody");

        function render() {
            const keyword = search.value.trim().toLowerCase();

            const filtered = links.filter(link => {
                const topics = link.topics || [];
                const category = link.category || "";
                const region = link.region || "";

                const searchable = [
                    link.title,
                    link.organization,
                    link.description,
                    category,
                    region,
                    ...topics
                ].join(" ").toLowerCase();

                const matchesKeyword = searchable.includes(keyword);

                const matchesCategory =
                    selected.category.size === 0 ||
                    selected.category.has(category);

                const matchesTopics =
                    selected.topics.size === 0 ||
                    [...selected.topics].some(topic =>
                        topics.includes(topic)
                    );

                const matchesRegion =
                    selected.region.size === 0 ||
                    selected.region.has(region);

                return matchesKeyword &&
                    matchesCategory &&
                    matchesTopics &&
                    matchesRegion;
            });

            filtered.sort((a, b) =>
                (a.organization || "").localeCompare(
                    b.organization || "",
                    "ja",
                    { numeric: true, sensitivity: "base" }
                ) ||
                (a.title || "").localeCompare(
                    b.title || "",
                    "ja",
                    { numeric: true, sensitivity: "base" }
                )
            );

            const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);

            if (currentPage > totalPages) {
                currentPage = Math.max(totalPages, 1);
            }

            const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
            const pageItems = filtered.slice(startIndex, startIndex + ITEMS_PER_PAGE);

            tbody.replaceChildren();

            pageItems.forEach(link => {
                const row = document.createElement("tr");

                const titleCell = document.createElement("td");

                const anchor = document.createElement("a");
                anchor.href = link.url;
                anchor.target = "_blank";
                anchor.rel = "noopener noreferrer";
                anchor.textContent = link.title;

                const description = document.createElement("div");
                description.className = "link-description";
                description.textContent = link.description || "";

                titleCell.append(anchor, description);

                const organizationCell = document.createElement("td");
                organizationCell.textContent = link.organization || "";

                const tagsCell = document.createElement("td");
                tagsCell.className = "link-tags";

                [
                    link.category,
                    ...(link.topics || []),
                    link.region
                ].filter(Boolean).forEach(value => {
                    const badge = document.createElement("span");
                    badge.className = "link-tag";
                    badge.textContent = value;
                    tagsCell.appendChild(badge);
                });

                const dateCell = document.createElement("td");
                dateCell.className = "link-date";
                dateCell.textContent = link.last_checked || "未確認";

                row.append(titleCell, organizationCell, tagsCell, dateCell);
                tbody.appendChild(row);
            });

            count.textContent = `${filtered.length} / ${links.length} 件`;

            pagination.replaceChildren();

            if (totalPages > 1) {
                for (let page = 1; page <= totalPages; page++) {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className = "page-button";
                    button.textContent = page;

                    if (page === currentPage) {
                        button.classList.add("active");
                    }

                    button.addEventListener("click", () => {
                        currentPage = page;
                        render();
                    });

                    pagination.appendChild(button);
                }
            }
        }

        table.append(thead, tbody);
        wrapper.appendChild(table);
        container.append(
            filters,
            search,
            controls,
            count,
            wrapper,
            pagination
        );

        search.addEventListener("input", () => {
            currentPage = 1;render();
        });

        currentPage = 1;
        render();
    })
    .catch(error => {
        const container = document.getElementById("link-list");
        const message = document.createElement("p");
        message.className = "error";
        message.textContent = "リンク一覧を読み込めませんでした。";
        container.appendChild(message);
        console.error("Failed to load config/link.json:", error);
    });
