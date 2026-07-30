const fs = require('fs');
const path = require('path');

// Extract or load functions from static/index.html
function normStr(str) {
    return (str || '').normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function getJobWorkModel(job) {
    const title = (job.title || '').toLowerCase();
    const reqs = (job.requirements || '').toLowerCase();
    const loc = (job.location || '').toLowerCase();
    
    const norm = (title + ' ' + reqs + ' ' + loc).normalize('NFD').replace(/[\u0300-\u036f]/g, '');

    const hasHybrid = /\b(hibrid[oa]s?|hybrid)\b/.test(norm);
    const hasRemote = /\b(remot[oa]s?|home\s*office|remote|teletrabalho|wfh|work\s*from\s*home|anywhere)\b/.test(norm);
    
    const normPresential = norm.replace(/\b(nao|não)\s+(e\s+)?presencia[li]s?\b/g, '');
    const hasPresential = /\b(presencia[li]s?|onsite|on-site)\b/.test(normPresential);

    if (hasHybrid) return 'hibrido';
    if (hasRemote && !hasPresential) return 'remoto';
    if (hasPresential && !hasRemote) return 'presencial';
    if (hasRemote) return 'remoto';
    if (hasPresential) return 'presencial';
    return 'outros';
}

function matchLocation(job, locQuery) {
    const normQuery = normStr(locQuery);
    if (!normQuery) return true;
    
    const normTitle = normStr(job.title);
    const normReq = normStr(job.requirements);
    const normCompany = normStr(job.company);
    const normLoc = normStr(job.location);

    return normTitle.includes(normQuery) || normReq.includes(normQuery) || normCompany.includes(normQuery) || normLoc.includes(normQuery);
}

// Full comprehensive test cases covering Objectives 1 & 2
const workModelTestCases = [
    // --- 1. Feminine forms ---
    { category: "Feminine forms", title: "Vaga Remota", requirements: "Oportunidade para desenvolvedor", location: "", expected: "remoto" },
    { category: "Feminine forms", title: "Engenheiro de Software", requirements: "Modalidade Híbrida em São Paulo", location: "", expected: "hibrido" },
    { category: "Feminine forms", title: "Analista de TI", requirements: "Atuação Presencial no escritório", location: "São Paulo", expected: "presencial" },
    { category: "Feminine forms", title: "Vaga Híbrida", requirements: "3 dias presenciais, 2 em casa", location: "", expected: "hibrido" },

    // --- 2. Plural forms ---
    { category: "Plural forms", title: "Vagas Remotas para Devs", requirements: "", location: "", expected: "remoto" },
    { category: "Plural forms", title: "Trabalhos Híbridos em Tech", requirements: "", location: "", expected: "hibrido" },
    { category: "Plural forms", title: "Vagas Presenciais na Matriz", requirements: "", location: "Curitiba", expected: "presencial" },
    { category: "Plural forms", title: "Oportunidades Remotas", requirements: "", location: "", expected: "remoto" },

    // --- 3. Accented variations ---
    { category: "Accented variations", title: "Dev Híbrido", requirements: "", location: "", expected: "hibrido" },
    { category: "Accented variations", title: "Dev Hibrido", requirements: "", location: "", expected: "hibrido" },
    { category: "Accented variations", title: "Dev Híbrida", requirements: "", location: "", expected: "hibrido" },
    { category: "Accented variations", title: "Dev Hibrida", requirements: "", location: "", expected: "hibrido" },
    { category: "Accented variations", title: "Trabalho Remóto", requirements: "", location: "", expected: "remoto" },
    { category: "Accented variations", title: "Vaga Presêncial", requirements: "", location: "", expected: "presencial" },

    // --- 4. English terms ---
    { category: "English terms", title: "Software Engineer - Work from home", requirements: "", location: "", expected: "remoto" },
    { category: "English terms", title: "Fullstack Developer (WFH)", requirements: "", location: "", expected: "remoto" },
    { category: "English terms", title: "Backend Engineer Onsite", requirements: "", location: "", expected: "presencial" },
    { category: "English terms", title: "Data Analyst (On-site)", requirements: "", location: "", expected: "presencial" },
    { category: "English terms", title: "DevOps Hybrid", requirements: "", location: "", expected: "hibrido" },
    { category: "English terms", title: "Senior Developer - Remote", requirements: "", location: "", expected: "remoto" },
    { category: "English terms", title: "Analista de Sistemas - Teletrabalho", requirements: "", location: "", expected: "remoto" },
    { category: "English terms", title: "Product Owner - Anywhere", requirements: "", location: "", expected: "remoto" },

    // --- 5. Negative phrases ---
    { category: "Negative phrases", title: "Analista de Dados", requirements: "Trabalho 100% home office, não é presencial", location: "", expected: "remoto" },
    { category: "Negative phrases", title: "Engenheiro de Software", requirements: "Atuação no escritório. Não aceita remoto.", location: "São Paulo", expected: "presencial" },
    { category: "Negative phrases", title: "Dev Python", requirements: "Vaga 100% presencial, não é remoto", location: "Curitiba", expected: "presencial" },
    { category: "Negative phrases", title: "Suporte TI", requirements: "Sem opção de trabalho remoto, presença obrigatória", location: "", expected: "presencial" },
    { category: "Negative phrases", title: "Vaga de QA", requirements: "Não presencial", location: "", expected: "remoto" },
    { category: "Negative phrases", title: "Desenvolvedor Java", requirements: "Não e presencial", location: "", expected: "remoto" },

    // --- 6. Hybrid vs Remote overlaps ---
    { category: "Hybrid vs Remote overlaps", title: "Dev React", requirements: "Modelo Híbrido com 2 dias em home office", location: "", expected: "hibrido" },
    { category: "Hybrid vs Remote overlaps", title: "Gerente de Projetos", requirements: "Trabalho híbrido: 3 dias no escritório e 2 dias remote / WFH", location: "", expected: "hibrido" },
    { category: "Hybrid vs Remote overlaps", title: "Tech Lead", requirements: "Híbrido (escritório em SP + teletrabalho)", location: "", expected: "hibrido" },
    { category: "Hybrid vs Remote overlaps", title: "Analista Financeiro", requirements: "Vaga remota com visitas presenciais eventuais (1x por mês)", location: "", expected: "hibrido" },
    { category: "Hybrid vs Remote overlaps", title: "DevOps", requirements: "Atuação presencial 1 dia na semana e 4 dias home office", location: "", expected: "hibrido" },

    // --- 7. Edge & Corner cases ---
    { category: "Edge cases", title: "", requirements: "", location: "", expected: "outros" },
    { category: "Edge cases", title: "Vaga Geral", requirements: "Salário a combinar, regime CLT", location: "São Paulo", expected: "outros" },
    { category: "Edge cases", title: "Desenvolvedor C++", requirements: "Atuação presencial ou remota a combinar", location: "", expected: "hibrido" },
    { category: "Edge cases", title: "Vaga na empresa Home Office S.A.", requirements: "Trabalho no escritório em São Paulo", location: "", expected: "presencial" }
];

const locationTestCases = [
    // --- 1. Sao Paulo variations ---
    { filterInput: "São Paulo", job: { title: "Dev Python", company: "Tech", location: "São Paulo" }, expectedMatch: true, note: "Exact match with accents" },
    { filterInput: "Sao Paulo", job: { title: "Dev Python", company: "Tech", location: "São Paulo" }, expectedMatch: true, note: "Filter without accent vs location with accent" },
    { filterInput: "SÃO PAULO", job: { title: "Dev Python", company: "Tech", location: "São Paulo" }, expectedMatch: true, note: "Filter UPPERCASE vs location titlecase" },
    { filterInput: "sao paulo", job: { title: "Dev Python", company: "Tech", location: "São Paulo" }, expectedMatch: true, note: "Filter lowercase vs location titlecase" },
    { filterInput: "São Paulo", job: { title: "Dev Python", company: "Tech", location: "Sao Paulo/SP" }, expectedMatch: true, note: "Filter vs City/UF format" },
    { filterInput: "São Paulo", job: { title: "Dev Python", company: "Tech", location: "SP" }, expectedMatch: true, note: "Filter 'São Paulo' vs location 'SP'" },
    { filterInput: "SP", job: { title: "Dev Python", company: "Tech", location: "São Paulo" }, expectedMatch: true, note: "Filter 'SP' vs location 'São Paulo'" },

    // --- 2. Rio de Janeiro variations ---
    { filterInput: "Rio de Janeiro", job: { title: "Dev React", company: "RioTech", location: "rio de janeiro" }, expectedMatch: true, note: "Filter vs lowercase" },
    { filterInput: "Rio de Janeiro", job: { title: "Dev React", company: "RioTech", location: "RJ" }, expectedMatch: true, note: "Filter 'Rio de Janeiro' vs location 'RJ'" },
    { filterInput: "Rio de Janeiro", job: { title: "Dev React", company: "RioTech", location: "Rio de Janeiro/RJ" }, expectedMatch: true, note: "Filter vs City/UF" },
    { filterInput: "Rio", job: { title: "Dev React", company: "RioTech", location: "Rio de Janeiro" }, expectedMatch: true, note: "Short filter 'Rio' vs 'Rio de Janeiro'" },
    { filterInput: "Rio", job: { title: "Dev React", company: "RioTech", location: "Rio Claro" }, expectedMatch: false, note: "Short filter 'Rio' vs 'Rio Claro' (False Positive risk)" },

    // --- 3. Curitiba variations ---
    { filterInput: "Curitiba", job: { title: "Dev C#", company: "Curitiba Soft", location: "curitiba" }, expectedMatch: true, note: "Filter vs lowercase" },
    { filterInput: "Curitiba", job: { title: "Dev C#", company: "Curitiba Soft", location: "Curitiba/PR" }, expectedMatch: true, note: "Filter vs City/UF" },
    { filterInput: "Curitiba", job: { title: "Dev C#", company: "Curitiba Soft", location: "PR" }, expectedMatch: true, note: "Filter 'Curitiba' vs state abbreviation 'PR'" },

    // --- 4. Exterior variations ---
    { filterInput: "Exterior", job: { title: "Global Engineer", company: "US Inc", location: "exterior" }, expectedMatch: true, note: "Filter vs lowercase" },
    { filterInput: "Exterior", job: { title: "Global Engineer", company: "US Inc", location: "EUA" }, expectedMatch: true, note: "Filter 'Exterior' vs location 'EUA'" },
    { filterInput: "Exterior", job: { title: "Global Engineer", company: "US Inc", location: "Portugal" }, expectedMatch: true, note: "Filter 'Exterior' vs location 'Portugal'" },
    { filterInput: "Exterior", job: { title: "Global Engineer", company: "US Inc", location: "USA" }, expectedMatch: true, note: "Filter 'Exterior' vs location 'USA'" }
];

console.log("=== RUNNING WORK MODEL STRESS TESTS ===");
let wmPassed = 0;
let wmFailed = 0;
const wmResults = [];

workModelTestCases.forEach((tc, idx) => {
    const actual = getJobWorkModel(tc);
    const pass = actual === tc.expected;
    if (pass) wmPassed++; else wmFailed++;
    wmResults.push({
        id: idx + 1,
        category: tc.category,
        title: tc.title,
        requirements: tc.requirements,
        location: tc.location,
        expected: tc.expected,
        actual: actual,
        pass: pass
    });
});

console.log(`Work Model Results: Total=${workModelTestCases.length}, Passed=${wmPassed}, Failed=${wmFailed}`);

console.log("\n=== RUNNING LOCATION FILTER STRESS TESTS ===");
let locPassed = 0;
let locFailed = 0;
const locResults = [];

locationTestCases.forEach((tc, idx) => {
    const actualMatch = matchLocation(tc.job, tc.filterInput);
    const pass = actualMatch === tc.expectedMatch;
    if (pass) locPassed++; else locFailed++;
    locResults.push({
        id: idx + 1,
        filterInput: tc.filterInput,
        jobLocation: tc.job.location,
        expectedMatch: tc.expectedMatch,
        actualMatch: actualMatch,
        pass: pass,
        note: tc.note
    });
});

console.log(`Location Filter Results: Total=${locationTestCases.length}, Passed=${locPassed}, Failed=${locFailed}`);

const outputData = {
    workModelStats: { total: workModelTestCases.length, passed: wmPassed, failed: wmFailed, rate: (wmPassed/workModelTestCases.length*100).toFixed(1) + '%' },
    locationStats: { total: locationTestCases.length, passed: locPassed, failed: locFailed, rate: (locPassed/locationTestCases.length*100).toFixed(1) + '%' },
    workModelResults: wmResults,
    locationResults: locResults
};

fs.writeFileSync(path.join(__dirname, 'test_results.json'), JSON.stringify(outputData, null, 2));
console.log("Saved test_results.json.");
