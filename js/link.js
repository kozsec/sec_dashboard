
fetch("config/link.json")
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(links => {
        const container = document.getElementById("link-list");

        const search = document.createElement("input");
        search.type = "search";
        search.className = "link-search";
        search.placeholder = "キーワードで検索";
        search.setAttribute("aria-label", "リンクをキーワードで検索");

        const count = document.createElement("p");
        count.className = "link-count";

        const wrapper = document.createElement("div");
        wrapper.className = "link-table-wrapper";

        const table = document.createElement("table");
        table.className = "link-table";

        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");

        ["タイトル", "公開組織", "タグ", "最終確認日"].forEach(label => {
            const th = document.createElement("th");
            th.textContent = label;
            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);

        const tbody = document.createElement("tbody");

        function render() {
            const keyword = search.value.trim().toLowerCase();

            const filtered = links.filter(link => {
                const searchable = [
                    link.title,
                    link.organization,
                    link.type,
                    link.description,
                    ...(link.tags || [])
                ].join(" ").toLowerCase();

                return searchable.includes(keyword);
            });

            tbody.replaceChildren();

            filtered.forEach(link => {
                const row = document.createElement("tr");

                const titleCell = document.createElement("td");
                const anchor = document.createElement("a");
                anchor.href = link.url;
                anchor.target = "_blank";
                anchor.rel = "noopener noreferrer";
                anchor.textContent = link.title;
                titleCell.appendChild(anchor);

                const organizationCell = document.createElement("td");
                organizationCell.textContent = link.organization;

                const tagsCell = document.createElement("td");
                tagsCell.className = "link-tags";

                (link.tags || []).forEach(tag => {
                    const badge = document.createElement("span");
                    badge.className = "link-tag";
                    badge.textContent = tag;
                    tagsCell.appendChild(badge);
                });

                const dateCell = document.createElement("td");
                dateCell.className = "link-date";
                dateCell.textContent = link.last_checked || "未確認";

                row.append(
                    titleCell,
                    organizationCell,
                    tagsCell,
                    dateCell
                );

                tbody.appendChild(row);
            });

            count.textContent = `${filtered.length} / ${links.length} 件`;
        }

        table.append(thead, tbody);
        wrapper.appendChild(table);
        container.append(search, count, wrapper);

        search.addEventListener("input", render);
        render();
    })
    .catch(error => {
        const container = document.getElementById("link-list");
        const message = document.createElement("p");
        message.className = "error";
        message.textContent = "リンク一覧を読み込めませんでした。JSONファイルの配置と形式をご確認ください。";
        container.appendChild(message);
        console.error("Failed to load config/link.json:", error);
    });
