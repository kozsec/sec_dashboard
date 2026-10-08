fetch("data/links.json")
    .then(response => response.json())
    .then(links => {
        const container = document.getElementById("link-list");

        const categories = [...new Set(links.map(link => link.category))];

        categories.forEach(category => {
            const section = document.createElement("details");
            section.className = "cvss-vector-section";

            const summary = document.createElement("summary");
            summary.textContent = category;

            const columns = document.createElement("div");
            columns.className = "cvss-vector-columns";

            const description = document.createElement("div");
            description.className = "cvss-vector-description";

            links
                .filter(link => link.category === category)
                .forEach(link => {
                    const item = document.createElement("p");

                    item.innerHTML = `
                        <a href="${link.url}" target="_blank" rel="noopener noreferrer">
                            ${link.title}
                        </a>
                        - ${link.organization}
                        <br>
                        <small>${link.type} / ${link.description}</small>
                    `;

                    description.appendChild(item);
                });

            columns.appendChild(description);
            section.appendChild(summary);
            section.appendChild(columns);
            container.appendChild(section);
        });
    })
    .catch(error => {
        console.error("Failed to load links.json:", error);
    });
