const fs = require('fs');
const path = require('path');
const vm = require('vm');

const htmlPath = path.join(__dirname, '..', '..', 'static', 'index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

const scriptMatch = htmlContent.match(/<script>([\s\S]*?)<\/script>/i);
const sandbox = {
    console,
    document: {
        addEventListener: () => {},
        getElementById: () => ({ innerText: '', value: '', classList: { add: ()=>{}, remove: ()=>{} } }),
        querySelectorAll: () => []
    },
    window: {
        addEventListener: () => {}
    },
    localStorage: { getItem: () => null, setItem: () => {} }
};
vm.createContext(sandbox);
vm.runInContext(scriptMatch[1], sandbox);

const isProposalAllowed = sandbox.isProposalAllowed;

console.log("\n=== ADVERSARIAL STRESS TEST FOR isProposalAllowed ===");

const adversarialInputs = [
    { name: "Object with numeric platform", job: { platform: 999 }, expected: false },
    { name: "Object with boolean platform", job: { platform: true }, expected: false },
    { name: "Object with array platform", job: { platform: ["Workana"] }, expected: true },
    { name: "Object with sub-string workana in company name only", job: { platform: "LinkedIn", company: "Workana Inc" }, expected: false },
    { name: "Mixed casing wOrKaNa", job: { platform: "wOrKaNa" }, expected: true },
    { name: "Spaced 99 freelas string", job: { platform: " 99 freelas " }, expected: false },
    { name: "Novenove variant", job: { platform: "NOVENOVE_VAGAS" }, expected: true },
    { name: "Null platform property, valid source property", job: { platform: null, source: "Workana" }, expected: true },
    { name: "Empty object", job: {}, expected: false }
];

let passed = 0;
let total = adversarialInputs.length;

adversarialInputs.forEach((tc) => {
    const res = isProposalAllowed(tc.job);
    const pass = res === tc.expected;
    if (pass) passed++;
    console.log(`[${pass ? 'PASS' : 'FAIL'}] ${tc.name} -> returned ${res} (expected ${tc.expected})`);
});

console.log(`\nAdversarial Results: ${passed}/${total} passed.`);
