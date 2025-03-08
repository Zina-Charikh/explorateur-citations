const API_BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ Page chargée !");

    // Sélection des boutons
    const homeBtn = document.getElementById("homeBtn");
    const allQuotesBtn = document.getElementById("allQuotesBtn");
    const aboutBtn = document.getElementById("aboutBtn");

    // Sélection des sections
    const homeSection = document.getElementById("home-section");
    const allQuotesPage = document.getElementById("all-quotes-page");
    const aboutSection = document.getElementById("about-section");

    // ✅ Fonction pour afficher une section spécifique
    function showSection(section) {
        homeSection.style.display = section === "home" ? "flex" : "none";
        allQuotesPage.style.display = section === "quotes" ? "block" : "none";
        aboutSection.style.display = section === "about" ? "block" : "none";
    }

    if (homeBtn) homeBtn.addEventListener("click", () => {
        showSection("home");
        fetchQuote();
        generateQuiz();
    });

    if (allQuotesBtn) allQuotesBtn.addEventListener("click", () => {
        showSection("quotes");
        loadAllQuotes();
        loadTags();
    });

    if (aboutBtn) aboutBtn.addEventListener("click", () => {
        showSection("about");
    });

    // ✅ Gestion du bouton "Obtenir une citation aléatoire"
    const getQuoteBtn = document.getElementById("getQuote");
    if (getQuoteBtn) getQuoteBtn.addEventListener("click", fetchQuote);

    // ✅ Gestion du filtre de recherche
    const filterBtn = document.getElementById("filterBtn");
    if (filterBtn) filterBtn.addEventListener("click", filterQuotes);

    // ✅ Gestion du filtre par tag
    const tagFilterBtn = document.getElementById("tagFilterBtn");
    if (tagFilterBtn) tagFilterBtn.addEventListener("click", filterQuotesByTag);

    // ✅ Gestion du bouton "Suivant" du quiz
    const nextQuizBtn = document.getElementById("nextQuizBtn");
    if (nextQuizBtn) nextQuizBtn.addEventListener("click", generateQuiz);

    // ✅ Fonction pour récupérer une citation aléatoire
    async function fetchQuote() {
        try {
            console.log("📌 Récupération d'une citation...");
            const response = await fetch(`${API_BASE_URL}/quotes`);
            const quotes = await response.json();
            if (quotes.length === 0) return;

            const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
            document.getElementById("quote-box").innerHTML = `
                <blockquote class="box quote-container">
                    <p class="quote-text">${randomQuote.quote}</p>
                    <p class="quote-author">- <span>${randomQuote.author}</span></p>
                </blockquote>
            `;
        } catch (error) {
            console.error("❌ Erreur lors du chargement de la citation :", error);
        }
    }

    // ✅ Fonction pour générer un quiz
    async function generateQuiz() {
        try {
            console.log("📌 Génération du quiz...");
            const response = await fetch(`${API_BASE_URL}/quotes`);
            const quotes = await response.json();
            if (quotes.length < 4) return;

            const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
            const correctAuthor = randomQuote.author;

            let authors = new Set([correctAuthor]);
            while (authors.size < 4) {
                authors.add(quotes[Math.floor(Math.random() * quotes.length)].author);
            }

            document.getElementById("quiz-quote").innerHTML = `<p class="quote-text">${randomQuote.quote}</p>`;
            document.getElementById("quiz-options").innerHTML = "";

            [...authors].sort(() => Math.random() - 0.5).forEach(author => {
                const button = document.createElement("button");
                button.className = "button is-info is-light quiz-button full-width";
                button.innerText = author;
                button.onclick = () => checkAnswer(author, correctAuthor);
                document.getElementById("quiz-options").appendChild(button);
            });

            document.getElementById("quiz-result").innerHTML = "";
            document.getElementById("nextQuizBtn").style.display = "none";
            document.getElementById("quiz-section").style.display = "block";
        } catch (error) {
            console.error("❌ Erreur lors du quiz :", error);
        }
    }

    // ✅ Vérification de la réponse au quiz
    function checkAnswer(selected, correct) {
        const result = document.getElementById("quiz-result");
        if (selected === correct) {
            result.innerHTML = "✅ Bonne réponse !";
            result.style.color = "green";
        } else {
            result.innerHTML = `❌ Mauvaise réponse. C'était <strong>${correct}</strong>.`;
            result.style.color = "red";
        }
        document.getElementById("nextQuizBtn").style.display = "inline-block";
    }

    // ✅ Fonction pour charger toutes les citations
    async function loadAllQuotes() {
        console.log("📌 Chargement de toutes les citations...");
        try {
            const response = await fetch(`${API_BASE_URL}/quotes`);
            const quotes = await response.json();
            displayAllQuotes(quotes);
        } catch (error) {
            console.error("❌ Erreur lors du chargement :", error);
        }
    }

    // ✅ Fonction pour afficher toutes les citations
    function displayAllQuotes(quotes) {
        const container = document.getElementById("all-quotes-container");
        container.innerHTML = "";
        quotes.forEach(q => {
            const quoteElem = document.createElement("div");
            quoteElem.className = "box quote-item";
            quoteElem.innerHTML = `
                <p>${q.quote}</p>
                <p class="has-text-weight-bold">- ${q.author}</p>
            `;
            container.appendChild(quoteElem);
        });
    }

    // ✅ Fonction pour filtrer les citations par texte
    function filterQuotes() {
        const searchText = document.getElementById("filterInput").value.toLowerCase();
        const quotes = document.querySelectorAll(".quote-item");

        quotes.forEach(quote => {
            quote.style.display = quote.innerText.toLowerCase().includes(searchText) ? "block" : "none";
        });
    }

    // ✅ Fonction pour charger les tags sans duplication
    async function loadTags() {
        try {
            console.log("📌 Chargement des tags...");
            const response = await fetch(`${API_BASE_URL}/tags`);
            const tags = await response.json();
            const tagSelect = document.getElementById("tagFilter");

            tagSelect.innerHTML = `<option value="">📌 Sélectionner un tag</option>`;
            tags.forEach(tag => {
                const option = document.createElement("option");
                option.value = tag;
                option.textContent = tag;
                tagSelect.appendChild(option);
            });

            console.log(`✅ ${tags.length} tags chargés avec succès !`);
        } catch (error) {
            console.error("❌ Erreur lors du chargement des tags :", error);
        }
    }

    // ✅ Fonction pour filtrer les citations par tag
    async function filterQuotesByTag() {
        const selectedTag = document.getElementById("tagFilter").value;
        if (!selectedTag) return;

        console.log(`📌 Filtrage des citations pour le tag: ${selectedTag}`);

        try {
            const response = await fetch(`${API_BASE_URL}/quotes/by_tag?tag=${encodeURIComponent(selectedTag)}`);
            const filteredQuotes = await response.json();
            displayAllQuotes(filteredQuotes);
        } catch (error) {
            console.error("❌ Erreur lors du filtrage des citations :", error);
        }
    }

    // ✅ Lancer une citation et un quiz au chargement
    fetchQuote();
    generateQuiz();
});
