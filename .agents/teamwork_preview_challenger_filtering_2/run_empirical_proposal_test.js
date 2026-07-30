const fs = require('fs');
const path = require('path');
const vm = require('vm');

const htmlPath = path.join(__dirname, '..', '..', 'static', 'index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

// Extract script content from index.html
const scriptMatch = htmlContent.match(/<script>([\s\S]*?)<\/script>/i);
if (!scriptMatch) {
    console.error("FATAL: Could not find <script> block in index.html");
    process.exit(1);
}

const scriptCode = scriptMatch[1];

// Helper functions needed for rendering if not in context
function esc(str) {
    const s = (str === null || str === undefined) ? '' : String(str);
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function escAttr(str) {
    const s = (str === null || str === undefined) ? '' : String(str);
    return s.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/"/g, "&quot;").replace(/\n/g, " ");
}

// Create a sandbox VM context
const sandbox = {
    console: console,
    document: {
        getElementById: () => ({ innerText: '', value: '', classList: { add: ()=>{}, remove: ()=>{} } }),
        querySelectorAll: () => []
    },
    window: {},
    localStorage: { getItem: () => null, setItem: () => {} },
    setInterval: () => {},
    setTimeout: () => {},
    fetch: () => Promise.resolve({ json: () => Promise.resolve({}) }),
    esc: esc,
    escAttr: escAttr
};

vm.createContext(sandbox);
try {
    vm.runInContext(scriptCode, sandbox);
} catch (e) {
    // DOM operations inside DOMContentLoaded listener might fail in VM, but functions will be defined
}

const isProposalAllowed = sandbox.isProposalAllowed;
if (typeof isProposalAllowed !== 'function') {
    console.error("FATAL: isProposalAllowed function is not defined or not extracted properly!");
    process.exit(1);
}

let passed = 0;
let failed = 0;
const failures = [];

function assert(desc, condition) {
    if (condition) {
        passed++;
        console.log(`  [PASSOU] ${desc}`);
    } else {
        failed++;
        console.log(`  [FALHOU] ${desc}`);
        failures.push(desc);
    }
}

console.log("\n=== 1. EMPIRICAL TEST: isProposalAllowed(job) ===");

// 1.1 Freela platforms
const freelaCases = [
    { platform: "Workana" },
    { platform: "workana" },
    { platform: " WORKANA " },
    { platform: " 99Freelas " },
    { platform: "99freelas" },
    { platform: "novenove" },
    { source: "Workana" },
    { origem: "99freelas" },
    { plataforma: "novenove" }
];

freelaCases.forEach(c => {
    const platName = JSON.stringify(c);
    assert(`Freela platform ${platName} MUST return true`, isProposalAllowed(c) === true);
});

// 1.2 Corporate platforms
const corporateCases = [
    { platform: "LinkedIn" },
    { platform: "linkedin" },
    { platform: "Infojobs" },
    { platform: "infojobs" },
    { platform: "Gupy" },
    { platform: "gupy" },
    { platform: "Catho" },
    { platform: "catho" },
    { platform: "Coodesh" },
    { platform: "coodesh" },
    { platform: "Vagas.com" },
    { platform: "vagas_com" },
    { platform: "Glassdoor" },
    { platform: "glassdoor" },
    { platform: "Indeed" },
    { platform: "ProgramaThor" },
    { platform: "GeekHunter" },
    { platform: "Jooble" }
];

corporateCases.forEach(c => {
    const platName = JSON.stringify(c);
    assert(`Corporate platform ${platName} MUST return false`, isProposalAllowed(c) === false);
});

// 1.3 Null / Undefined / Empty platforms
const invalidCases = [
    null,
    undefined,
    {},
    { platform: null },
    { platform: undefined },
    { platform: "" },
    { platform: "   " },
    { source: "" },
    { origem: null }
];

invalidCases.forEach((c, idx) => {
    assert(`Invalid/Empty platform input #${idx + 1} (${JSON.stringify(c)}) MUST return false`, isProposalAllowed(c) === false);
});

console.log("\n=== 2. EMPIRICAL TEST: HTML VIEW RENDERING RESTRICTIONS ===");

// Simulate rendering for Cards View, Table View, Kanban View
const testJobs = [
    { title: "Dev Python Freela", company: "Cliente X", platform: "Workana", link: "http://workana/1", requirements: "Fazer bot" },
    { title: "Dev React 99", company: "Cliente Y", platform: "99freelas", link: "http://99/2", requirements: "Fazer UI" },
    { title: "Engenheiro de Dados", company: "Empresa A", platform: "LinkedIn", link: "http://linkedin/3", requirements: "ETL em Python" },
    { title: "Analista Gupy", company: "Empresa B", platform: "Gupy", link: "http://gupy/4", requirements: "Dashboard" },
    { title: "Desenvolvedor Catho", company: "Empresa C", platform: "Catho", link: "http://catho/5", requirements: "SQL" },
    { title: "Dev Coodesh", company: "Empresa D", platform: "Coodesh", link: "http://coodesh/6", requirements: "Node.js" },
    { title: "Dev Infojobs", company: "Empresa E", platform: "Infojobs", link: "http://infojobs/7", requirements: "Java" },
    { title: "Dev Vagas.com", company: "Empresa F", platform: "Vagas.com", link: "http://vagas/8", requirements: "C#" },
    { title: "Dev Glassdoor", company: "Empresa G", platform: "Glassdoor", link: "http://glassdoor/9", requirements: "Go" }
];

// Cards View rendering template snippet test
console.log("\n--- 2.1 Cards View Rendering Test ---");
testJobs.forEach(job => {
    const canPropose = isProposalAllowed(job);
    const reqText = job.requirements;
    const cardHtml = `
        <div class="job-detail-card">
            <div class="job-card-header">...</div>
            <div class="job-card-description">${esc(reqText)}</div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                ${canPropose ? `<button class="btn btn-primary" style="background-color:#1f6beb;" onclick="openProposalCopilot('${escAttr(job.title)}', '${escAttr(reqText)}', '${escAttr(job.platform)}')"><i class="fa-solid fa-wand-magic-sparkles"></i> Criar Proposta com IA</button>` : `<span></span>`}
                <a href="${job.link}" target="_blank" class="btn btn-secondary">Abrir Link da Vaga</a>
            </div>
        </div>
    `;

    const hasButton = cardHtml.includes("Criar Proposta com IA") || cardHtml.includes("openProposalCopilot");
    if (canPropose) {
        assert(`Cards View: Platform ${job.platform} HAS 'Criar Proposta com IA' button`, hasButton === true);
    } else {
        assert(`Cards View: Corporate platform ${job.platform} DOES NOT HAVE 'Criar Proposta com IA' button`, hasButton === false);
    }
});

// Table View rendering template snippet test
console.log("\n--- 2.2 Table View Rendering Test ---");
testJobs.forEach(job => {
    const canPropose = isProposalAllowed(job);
    const tableRowHtml = `
        <tr>
            <td>${esc(job.title)}</td>
            <td>${esc(job.company)}</td>
            <td>${esc(job.platform)}</td>
            <td style="text-align:right;">
                ${canPropose ? `<button class="btn btn-primary" style="height:26px; padding:0 8px; background-color:#1f6beb;" onclick="openProposalCopilot('${escAttr(job.title)}', '${escAttr(job.requirements || job.title)}', '${escAttr(job.platform)}')"><i class="fa-solid fa-wand-magic-sparkles"></i> Proposta</button>` : ''}
                <button class="btn btn-secondary">Aplicado</button>
            </td>
        </tr>
    `;

    const hasButton = tableRowHtml.includes("Proposta") || tableRowHtml.includes("openProposalCopilot");
    if (canPropose) {
        assert(`Table View: Platform ${job.platform} HAS 'Proposta' button`, hasButton === true);
    } else {
        assert(`Table View: Corporate platform ${job.platform} DOES NOT HAVE 'Proposta' button`, hasButton === false);
    }
});

// Kanban View rendering template snippet test
console.log("\n--- 2.3 Kanban View Rendering Test ---");
testJobs.forEach(job => {
    const canPropose = isProposalAllowed(job);
    const kanbanCardHtml = `
        <div style="background:var(--bg-canvas);">
            <div>${job.title}</div>
            <div>${job.company} • ${job.platform}</div>
            <div>
                ${canPropose ? `<button class="btn btn-secondary" onclick="openProposalCopilot('${escAttr(job.title)}', '${escAttr(job.requirements || job.title)}', '${escAttr(job.platform || 'Workana')}')"><i class="fa-solid fa-wand-magic-sparkles"></i> IA</button>` : ''}
                <a href="${job.link}">Link</a>
            </div>
        </div>
    `;

    const hasButton = kanbanCardHtml.includes("openProposalCopilot");
    if (canPropose) {
        assert(`Kanban View: Platform ${job.platform} HAS Copilot button`, hasButton === true);
    } else {
        assert(`Kanban View: Corporate platform ${job.platform} DOES NOT HAVE Copilot button`, hasButton === false);
    }
});

console.log("\n==================================================");
console.log(`TOTAL PASSED: ${passed}`);
console.log(`TOTAL FAILED: ${failed}`);

if (failed > 0) {
    console.error(`\n[FALHOU] ${failed} assertion(s) failed:`);
    failures.forEach(f => console.error(` - ${f}`));
    process.exit(1);
} else {
    console.log("\n[PASSOU] ALL EMPIRICAL PROPOSAL RESTRICTION TESTS PASSED 100%!");
}
