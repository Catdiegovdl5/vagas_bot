/**
 * test_category_pills_empirical.js
 * Empirical Test Suite for Category Pills (R1) in static/index.html
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

// 1. Read static/index.html
const htmlPath = path.join(__dirname, '..', '..', 'static', 'index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

// Extract the <script> block containing PROFESSION_CATEGORIES, normStr, matchesCategory, filterData, renderViewContent, etc.
const scriptMatch = htmlContent.match(/<script>([\s\S]*?)<\/script>/i);
if (!scriptMatch) {
    console.error("FAILED to extract <script> from static/index.html");
    process.exit(1);
}
let jsCode = scriptMatch[1];

// Append global export bindings so sandbox exposes top-level consts/funcs
jsCode += `
;
globalThis.PROFESSION_CATEGORIES = PROFESSION_CATEGORIES;
globalThis.FRESHNESS_CATEGORIES = FRESHNESS_CATEGORIES;
globalThis.WORKMODEL_CATEGORIES = WORKMODEL_CATEGORIES;
globalThis.SENIORITY_CATEGORIES = SENIORITY_CATEGORIES;
globalThis.normStr = normStr;
globalThis.matchesCategory = matchesCategory;
globalThis.selectCategory = selectCategory;
globalThis.filterData = filterData;
globalThis.renderViewContent = renderViewContent;
globalThis.changePage = changePage;
globalThis.setAllData = (d) => { allData = d; };
globalThis.getViewData = () => viewData;
globalThis.getAllData = () => allData;
`;

// 2. Setup mock DOM and global environment in vm context
class ClassList {
    constructor() {
        this.set = new Set();
    }
    add(...names) { names.forEach(n => this.set.add(n)); }
    remove(...names) { names.forEach(n => this.set.delete(n)); }
    contains(name) { return this.set.has(name); }
}

class MockElement {
    constructor(id, tagName = 'div') {
        this.id = id;
        this.tagName = tagName.toUpperCase();
        this.innerHTML = '';
        this.innerText = '';
        this._val = id === 'lang-select' ? 'all' : '';
        this.classList = new ClassList();
        this.children = [];
        this.attributes = {};
    }
    get value() { return this._val; }
    set value(v) { this._val = v; }
    querySelector() { return null; }
    querySelectorAll() { return []; }
    setAttribute(k, v) { this.attributes[k] = v; }
    getAttribute(k) { return this.attributes[k]; }
}

const elements = {};
function getElement(id) {
    if (!elements[id]) {
        elements[id] = new MockElement(id);
    }
    return elements[id];
}

// Pre-create element for lang-select
const langEl = getElement('lang-select');
langEl.value = 'all';

const mockDocument = {
    addEventListener: () => {},
    getElementById: (id) => getElement(id),
    querySelectorAll: (selector) => {
        if (selector === '.plat-cb:checked') {
            return [
                { value: 'Workana' }, { value: '99freelas' }, { value: 'novenove' },
                { value: 'LinkedIn' }, { value: 'Gupy' }, { value: 'Freelancer' }
            ];
        }
        if (selector === '.plat-cb') {
            return [{ value: 'Workana', checked: true }, { value: '99freelas', checked: true }];
        }
        return [];
    },
    querySelector: () => null,
    documentElement: new MockElement('html')
};

const mockLocalStorage = {
    store: {},
    getItem(k) { return this.store[k] || null; },
    setItem(k, v) { this.store[k] = String(v); }
};

const sandbox = {
    console: console,
    document: mockDocument,
    window: { SpeechRecognition: null, webkitSpeechRecognition: null, addEventListener: () => {} },
    localStorage: mockLocalStorage,
    setInterval: () => {},
    setTimeout: (fn) => fn(),
    clearTimeout: () => {},
    fetch: async () => ({ json: async () => ({ jobs: [] }) }),
    alert: () => {},
    ITEMS_PER_PAGE: 10,
    UF_MAPPING: {}
};

vm.createContext(sandbox);

try {
    vm.runInContext(jsCode, sandbox);
    console.log("SUCCESS: Environment and index.html JS code loaded successfully into VM.\n");
} catch (e) {
    console.error("ERROR running JS code from index.html:", e);
    process.exit(1);
}

// Extract required functions & structures from sandbox
const { PROFESSION_CATEGORIES, normStr, matchesCategory, selectCategory, filterData, renderViewContent, changePage, setAllData, getViewData, getAllData } = sandbox;

let passCount = 0;
let failCount = 0;
const failureDetails = [];

function assert(condition, testName, detail = '') {
    if (condition) {
        console.log(`  [PASS] ${testName}`);
        passCount++;
    } else {
        console.log(`  [FAIL] ${testName} ${detail ? '(' + detail + ')' : ''}`);
        failCount++;
        failureDetails.push({ testName, detail });
    }
}

console.log("=== TEST SUITE 1: 6 OFFICIAL BACKEND CATEGORIES AUDIT ===");
const expectedCategories = [
    { id: "all", name: "Todas as Vagas" },
    { id: "growth_engineer", name: "Growth & Tráfego" },
    { id: "ia_ops", name: "IA-Ops" },
    { id: "sdr_tecnico", name: "SDR Técnico" },
    { id: "analytics_engineer", name: "Analytics Engineer" },
    { id: "server_side_tracking", name: "Server-Side Tracking" },
    { id: "outros", name: "Outros" }
];

assert(Array.isArray(PROFESSION_CATEGORIES), "PROFESSION_CATEGORIES is an array");
assert(PROFESSION_CATEGORIES && PROFESSION_CATEGORIES.length === 7, `PROFESSION_CATEGORIES has 7 entries (all + 6 categories), found: ${PROFESSION_CATEGORIES ? PROFESSION_CATEGORIES.length : 0}`);

expectedCategories.forEach(expected => {
    const found = PROFESSION_CATEGORIES ? PROFESSION_CATEGORIES.find(c => c.id === expected.id) : null;
    assert(!!found, `Category pill for '${expected.id}' exists`);
    if (found) {
        assert(found.name === expected.name, `Category pill '${expected.id}' has name '${expected.name}'`, `got '${found.name}'`);
    }
});


console.log("\n=== TEST SUITE 2: CATEGORY MATCHING (EXACT PROFESSION MATCHES) ===");
const official6Jobs = [
    { title: "Vaga 1", profession: "Growth & Tráfego", expectedCatId: "growth_engineer" },
    { title: "Vaga 2", profession: "IA-Ops", expectedCatId: "ia_ops" },
    { title: "Vaga 3", profession: "SDR Técnico", expectedCatId: "sdr_tecnico" },
    { title: "Vaga 4", profession: "Analytics Engineer", expectedCatId: "analytics_engineer" },
    { title: "Vaga 5", profession: "Server-Side Tracking", expectedCatId: "server_side_tracking" },
    { title: "Vaga 6", profession: "Outros", expectedCatId: "outros" }
];

official6Jobs.forEach(j => {
    const catObj = PROFESSION_CATEGORIES.find(c => c.id === j.expectedCatId);
    const match = matchesCategory(j, catObj);
    assert(match === true, `Exact profession '${j.profession}' matches category '${j.expectedCatId}'`);
});


console.log("\n=== TEST SUITE 3: KEYWORD FALLBACK MATCHING (WHEN PROFESSION IS NULL/EMPTY) ===");
const kwJobs = [
    { title: "Gestor de Tráfego Pago e Meta Ads", profession: null, expectedCatId: "growth_engineer" },
    { title: "Especialista em Automação n8n e LLMs", profession: null, expectedCatId: "ia_ops" },
    { title: "SDR de Vendas B2B Outbound", profession: null, expectedCatId: "sdr_tecnico" },
    { title: "Analytics Engineer com dbt e PowerBI", profession: null, expectedCatId: "analytics_engineer" },
    { title: "Implementador GTM Server-Side & Meta CAPI", profession: null, expectedCatId: "server_side_tracking" },
    { title: "Analista de Suporte Técnico e DevOps Geral", profession: null, expectedCatId: "outros" }
];

kwJobs.forEach(j => {
    const catObj = PROFESSION_CATEGORIES.find(c => c.id === j.expectedCatId);
    const match = matchesCategory(j, catObj);
    assert(match === true, `Title '${j.title}' (profession=null) matches category '${j.expectedCatId}' via keywords`);
});


console.log("\n=== TEST SUITE 4: EDGE CASES (ACCENTS, CASE-INSENSITIVITY, RETAIL EXCLUSION, NULLS) ===");

// 4.1 Accent variations
const accentJobs = [
    { title: "Gestor de Trafego", profession: "Growth & Trafego", expectedCatId: "growth_engineer" },
    { title: "SDR Tecnico", profession: "SDR Tecnico", expectedCatId: "sdr_tecnico" }
];
accentJobs.forEach(j => {
    const catObj = PROFESSION_CATEGORIES.find(c => c.id === j.expectedCatId);
    const match = matchesCategory(j, catObj);
    assert(match === true, `Unaccented profession '${j.profession}' matches '${j.expectedCatId}'`);
});

// 4.2 Trailing/Leading Whitespace in profession
const spacedJob = { title: "Vaga Growth", profession: " Growth & Tráfego " };
const growthCat = PROFESSION_CATEGORIES.find(c => c.id === "growth_engineer");
const spacedMatch = matchesCategory(spacedJob, growthCat);
assert(spacedMatch === true, `Profession with trailing/leading space '${spacedJob.profession}' matches category 'growth_engineer'`);

// 4.3 Retail exclusion rule check (empirical observation: exact profession match evaluates before retail terms!)
const retailJob = { title: "Vendedor de Calçados no Shopping", profession: "Growth & Tráfego" };
const retailMatch = matchesCategory(retailJob, growthCat);
assert(retailMatch === true, `Retail title '${retailJob.title}' with exact profession '${retailJob.profession}' evaluates true because prof match precedes retail exclusion check`);

// 4.4 Missing/Null profession & unexpected title
const unknownJob = { title: "Desenvolvedor Node.js Backend", profession: null };
const catOutros = PROFESSION_CATEGORIES.find(c => c.id === "outros");
const outrosMatch = matchesCategory(unknownJob, catOutros);
assert(outrosMatch === false, `Job with unknown title '${unknownJob.title}' and null profession does NOT match 'Outros' (kws restriction check)`);


console.log("\n=== TEST SUITE 5: DOM SCREEN CLEARING & CARD DUPLICATION PREVENTION ===");

// Initialize sandbox with test jobs
setAllData([
    { title: "Job 1 Growth", profession: "Growth & Tráfego", platform: "Workana", status: "Disponível", link: "http://job1" },
    { title: "Job 2 Growth", profession: "Growth & Tráfego", platform: "Workana", status: "Disponível", link: "http://job2" },
    { title: "Job 3 IA-Ops", profession: "IA-Ops", platform: "99freelas", status: "Disponível", link: "http://job3" },
    { title: "Job 4 SDR", profession: "SDR Técnico", platform: "LinkedIn", status: "Disponível", link: "http://job4" },
    { title: "Job 5 Analytics", profession: "Analytics Engineer", platform: "Gupy", status: "Disponível", link: "http://job5" }
]);

getElement('lang-select').value = 'all';
selectCategory("all");

const viewContainer = getElement('view-container');

function countCardsInContainer(html) {
    const matches = html.match(/class="job-detail-card"/g);
    return matches ? matches.length : 0;
}

const countAll = countCardsInContainer(viewContainer.innerHTML);
assert(countAll === 5, `Initial 'all' view renders exactly 5 cards`, `got ${countAll}`);

// Test 5.2: Switch to Growth category (should clear and show exactly 2 cards)
selectCategory("growth_engineer");
const countGrowth = countCardsInContainer(viewContainer.innerHTML);
assert(countGrowth === 2, `Switching to 'growth_engineer' clears screen and renders exactly 2 cards`, `got ${countGrowth}`);

// Test 5.3: Rapid Category Switching (Growth -> IA-Ops -> All -> SDR -> Growth)
selectCategory("ia_ops");
selectCategory("all");
selectCategory("sdr_tecnico");
selectCategory("growth_engineer");
const countRapidSwitch = countCardsInContainer(viewContainer.innerHTML);
assert(countRapidSwitch === 2, `Rapid switching back to 'growth_engineer' results in exactly 2 cards without duplication`, `got ${countRapidSwitch}`);

// Test 5.4: Pagination clicking (Rapid Page Switch)
// Generate 25 jobs for page testing
const manyJobs = [];
for (let i = 1; i <= 25; i++) {
    manyJobs.push({
        title: `Job ${i}`,
        profession: "Growth & Tráfego",
        platform: "Workana",
        status: "Disponível",
        link: `http://job_${i}`
    });
}
setAllData(manyJobs);
selectCategory("all");

const countPage1 = countCardsInContainer(viewContainer.innerHTML);
assert(countPage1 === 10, `Page 1 renders maximum 10 items per page (ITEMS_PER_PAGE=10)`, `got ${countPage1}`);

changePage(2);
const countPage2 = countCardsInContainer(viewContainer.innerHTML);
assert(countPage2 === 10, `Page 2 renders 10 items per page after clearing Page 1 cards`, `got ${countPage2}`);

changePage(3);
const countPage3 = countCardsInContainer(viewContainer.innerHTML);
assert(countPage3 === 5, `Page 3 renders remaining 5 items without duplicating previous pages`, `got ${countPage3}`);

changePage(1);
const countBackPage1 = countCardsInContainer(viewContainer.innerHTML);
assert(countBackPage1 === 10, `Returning to Page 1 clears Page 3 and renders exactly 10 cards`, `got ${countBackPage1}`);


console.log("\n==================================================");
console.log(`SUMMARY: Passed: ${passCount} | Failed: ${failCount}`);
console.log("==================================================");

if (failCount > 0) {
    console.log("\nFAILURES:");
    failureDetails.forEach(f => console.log(` - ${f.testName}: ${f.detail}`));
    process.exit(1);
} else {
    console.log("\nALL EMPIRICAL TESTS PASSED SUCCESSFULLY!");
    process.exit(0);
}
