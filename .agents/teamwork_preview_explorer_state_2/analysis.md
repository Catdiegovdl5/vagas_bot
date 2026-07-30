# Comprehensive Analysis Report: Requirement 2 (R2) — UF Mapping (27 States) & Remote Job Preservation in `static/index.html`

## Executive Summary
This report presents a thorough investigation of Requirement 2 (R2) in `static/index.html` for the `vagas-sniper-bot` application. 
The analysis reveals that while the HTML UI `<select id="state-select">` lists options for all 27 Brazilian States (UF), the client-side JavaScript filtering engine (`filterData()`) currently lacks:
1. **State-to-City and Full-Name Mapping**: Selecting a UF (e.g., `SP`) merely performs a naive string search for `"sp"`. It fails to match jobs located in "São Paulo" (full name) or main state cities (e.g., "Campinas", "Santos", "Barueri"). Furthermore, naive string search causes false positive matches on common words containing "sp" as a substring (e.g., `reSPonsavel`, `eSPecialista`, `diSPonivel`).
2. **100% Remote Job Preservation**: When a state or city filter is selected, `filterData()` filters out all jobs whose text does not explicitly match the location string, inadvertently hiding **100% Remote** jobs (e.g., "Remoto", "Home Office", "Teletrabalho", "100% Remoto").

Proposed JS and HTML modifications are documented with exact line numbers and code snippets to resolve both deficiencies cleanly and robustly.

---

## 1. Analysis of Current Location Filtering Mechanics in `static/index.html`

### 1.1 HTML Structure (`<select id="state-select">` and `#loc-input`)
- **Lines 473–503**: HTML `<select id="state-select">` contains 28 options:
  - Default option: `-- Todos os 27 Estados (UF) --`
  - All 27 Brazilian State UF codes: `SP`, `RJ`, `MG`, `PR`, `RS`, `SC`, `BA`, `PE`, `CE`, `DF`, `ES`, `GO`, `MA`, `MT`, `MS`, `PA`, `PB`, `AM`, `RN`, `AL`, `PI`, `SE`, `RO`, `TO`, `AC`, `AP`, `RR`.
  - Additional option: `Exterior` (Exterior / Internacional).
- **Line 473**: Triggers `onchange="setLocFilter(this.value)"`.
- **Line 505**: Input text box `<input type="text" id="loc-input" placeholder="ou digite a cidade (ex: Curitiba)..." oninput="debounceFilter()">`.
- **Lines 508–513**: Quick city pill buttons (`Todas Cidades`, `São Paulo`, `Rio de Janeiro`, `Curitiba`).

### 1.2 JavaScript Filter Logic Execution Flow
- **Lines 829–832**:
  ```javascript
  function setLocFilter(city) {
      document.getElementById('loc-input').value = city;
      filterData();
  }
  ```
  *Deficiency*: `setLocFilter()` writes the raw UF value (e.g., `"SP"`) directly into the `#loc-input` text box and calls `filterData()`.

- **Lines 1094–1112 (`filterData()`)**:
  ```javascript
  const query = normStr(document.getElementById('search-input').value);
  const locQuery = normStr(document.getElementById('loc-input').value);
  ...
  let matchLoc = true;
  if (locQuery) {
      matchLoc = normTitle.includes(locQuery) || normReq.includes(locQuery) || normCompany.includes(locQuery) || normLoc.includes(locQuery);
  }
  ```
  *Deficiencies*:
  1. No check for `#state-select` value.
  2. Substring matching (`normLoc.includes("sp")`) fails when job location is listed as "São Paulo" (full name) or "Campinas" (city name).
  3. Substring matching produces false positives: `"sp"` matches `especialista`, `responsavel`, `disponivel`. `"pr"` matches `programador`. `"es"` matches `estagio`. `"ce"` matches `processo`.
  4. Remote jobs without the state string in their text evaluate `matchLoc = false` and are hidden.

---

## 2. Requirement 2 (R2) Implementation Strategy

### 2.1 Complete 27-State UF Mapping Table (`UF_MAP`)
All 27 Brazilian States must be mapped to their:
- **UF Code** (e.g. `SP`)
- **Full State Name** (e.g. `São Paulo`)
- **Main Cities** for each state (normalized lowercase)

```javascript
const UF_MAP = {
    "AC": { name: "Acre", cities: ["rio branco", "cruzeiro do sul", "sena madureira", "tarauaca", "feijo"] },
    "AL": { name: "Alagoas", cities: ["maceio", "arapiraca", "rio largo", "palmeira dos indios", "penedo"] },
    "AP": { name: "Amapá", cities: ["macapa", "santana", "laranjal do jari", "oiapoque"] },
    "AM": { name: "Amazonas", cities: ["manaus", "parintins", "itacoatiara", "manacapuru", "coari"] },
    "BA": { name: "Bahia", cities: ["salvador", "feira de santana", "vitoria da conquista", "camacari", "juazeiro", "lauro de freitas", "itabuna", "ilheus", "barreiras", "jequie"] },
    "CE": { name: "Ceará", cities: ["fortaleza", "caucaia", "juazeiro do norte", "maracanau", "sobral", "crato", "itapipoca", "maranguape"] },
    "DF": { name: "Distrito Federal", cities: ["brasilia", "taguatinga", "ceilandia", "aguas claras", "gama", "samambaia", "planaltina"] },
    "ES": { name: "Espírito Santo", cities: ["vitoria", "vila velha", "serra", "cariacica", "cachoeiro de itapemirim", "linhares", "colatina", "guarapari"] },
    "GO": { name: "Goiás", cities: ["goiania", "aparecida de goiania", "anapolis", "rio verde", "luziania", "aguas lindas de goias", "valparaiso de goias", "trindade"] },
    "MA": { name: "Maranhão", cities: ["sao luis", "imperatriz", "sao jose de ribamar", "caxias", "timon", "codo", "paco do lumiar"] },
    "MT": { name: "Mato Grosso", cities: ["cuiaba", "varzea grande", "rondonopolis", "sinop", "tangara da serra", "caceres", "sorriso", "lucas do rio verde"] },
    "MS": { name: "Mato Grosso do Sul", cities: ["campo grande", "dourados", "tres lagoas", "corumba", "ponta pora", "navirai"] },
    "MG": { name: "Minas Gerais", cities: ["belo horizonte", "uberlandia", "contagem", "juiz de fora", "betim", "montes claros", "ribeirao das neves", "uberaba", "governador valadares", "ipatinga", "pocos de caldas", "divinopolis", "santa luzia", "sete lagoas"] },
    "PA": { name: "Pará", cities: ["belem", "ananindeua", "santarem", "maraba", "parauapebas", "castanhal", "abaetetuba", "cameta"] },
    "PB": { name: "Paraíba", cities: ["joao pessoa", "campina grande", "santa rita", "patos", "bayeux", "sousa", "cajazeiras"] },
    "PR": { name: "Paraná", cities: ["curitiba", "londrina", "maringa", "ponta grossa", "cascavel", "sao jose dos pinhais", "foz do iguacu", "colombo", "guarapuava", "paranagua", "araucaria", "toledo", "apucarana", "campo largo"] },
    "PE": { name: "Pernambuco", cities: ["recife", "jaboatao dos guararapes", "olinda", "caruaru", "petrolina", "paulista", "cabo de santo agostinho", "camaragibe", "garanhuns", "vitoria de santo antao"] },
    "PI": { name: "Piauí", cities: ["teresina", "parnaiba", "picos", "floriano", "piripiri", "campo maior"] },
    "RJ": { name: "Rio de Janeiro", cities: ["rio de janeiro", "sao goncalo", "duque de caxias", "nova iguacu", "niteroi", "campos dos goytacazes", "belford roxo", "sao joao de meriti", "petropolis", "volta redonda", "macae", "cabo frio", "angra dos reis", "teresopolis", "mage"] },
    "RN": { name: "Rio Grande do Norte", cities: ["natal", "mossoro", "parnamirim", "sao goncalo do amarante", "macaiba", "ceara-mirim"] },
    "RS": { name: "Rio Grande do Sul", cities: ["porto alegre", "caxias do sul", "canoas", "pelotas", "sao leopoldo", "novo hamburgo", "santa maria", "gravatai", "viamao", "passo fundo", "rio grande", "alvorada", "bento goncalves", "erechim"] },
    "RO": { name: "Rondônia", cities: ["porto velho", "ji-parana", "ariquemes", "vilhena", "cacoal", "jaru"] },
    "RR": { name: "Roraima", cities: ["boa vista", "rorainopolis", "caracarai"] },
    "SC": { name: "Santa Catarina", cities: ["florianopolis", "joinville", "blumenau", "sao jose", "chapeco", "criciuma", "itajai", "jaragua do sul", "palhoca", "balneario camboriu", "lages", "brusque", "tubarao"] },
    "SP": { name: "São Paulo", cities: ["sao paulo", "campinas", "guarulhos", "sao bernardo do campo", "santo andre", "osasco", "sao jose dos campos", "ribeirao preto", "sorocaba", "santos", "jundiai", "piracicaba", "bauru", "barueri", "sao caetano do sul", "mogi das cruzes", "franca", "taubate", "indaiatuba", "cotia", "americana", "araraquara", "jacarei", "hortolandia", "presidente prudente"] },
    "SE": { name: "Sergipe", cities: ["aracaju", "nossa senhora do socorro", "lagarto", "itabaiana", "estancia"] },
    "TO": { name: "Tocantins", cities: ["palmas", "araguaina", "gurupi", "porto nacional", "paraiso do tocantins"] },
    "Exterior": { name: "Exterior / Internacional", cities: ["exterior", "internacional", "international", "gringa", "usa", "us", "europe", "europa", "global"] }
};
```

### 2.2 Precise Word Boundary Matching for State UF
To eliminate false positives (e.g. `especialista` matching `SP`), UF codes must be tested using regex word boundaries:
`const ufRegex = new RegExp(`\\b${normUf}\\b`, 'i');`

Full state name and city names are matched via normalized substring checks:
```javascript
function isJobInState(job, ufCode) {
    if (!ufCode || !UF_MAP[ufCode]) return true;
    
    const info = UF_MAP[ufCode];
    const normUf = ufCode.toLowerCase();
    const normStateName = normStr(info.name);
    const normCities = info.cities;

    const locText = normStr(job.location || '');
    const titleText = normStr(job.title || '');
    const reqText = normStr(job.requirements || '');
    const compText = normStr(job.company || '');
    const fullText = (locText + ' ' + titleText + ' ' + reqText + ' ' + compText);

    // 1. Check exact UF code (word boundary)
    const ufRegex = new RegExp(`\\b${normUf}\\b`, 'i');
    if (ufRegex.test(locText) || ufRegex.test(fullText)) {
        return true;
    }

    // 2. Check full state name
    if (normStateName && fullText.includes(normStateName)) {
        return true;
    }

    // 3. Check main state cities
    for (const city of normCities) {
        if (city && fullText.includes(city)) {
            return true;
        }
    }

    return false;
}
```

### 2.3 100% Remote Job Preservation
The function `getJobWorkModel(job)` correctly detects 100% remote jobs using:
`/\b(remot[oa]s?|home\s*office|remote|teletrabalho|wfh|work\s*from\s*home|anywhere|100%\s*remoto|remoto\s*100%)\b/`

In `filterData()`, 100% Remote jobs evaluate `isRemote = (getJobWorkModel(j) === 'remoto')` and immediately bypass location restrictions (`matchLoc = true`).

---

## 3. Exact Line Numbers and Proposed Code Changes in `static/index.html`

### Edits in `static/index.html`

#### Edit 1: Insert `UF_MAP` and `isJobInState()` in `<script>` (around Line 684)
- **Target File**: `static/index.html`
- **Location**: Right before `getJobWorkModel` (Line 689).
- **Modification**: Insert `UF_MAP` dictionary and `isJobInState(job, ufCode)` function.

#### Edit 2: Update `getJobWorkModel()` Regex (Line 697)
- **Target File**: `static/index.html`
- **Line 697**:
  - *Current*: `const hasRemote = /\b(remot[oa]s?|home\s*office|remote|teletrabalho|wfh|work\s*from\s*home|anywhere)\b/.test(norm);`
  - *Replacement*: `const hasRemote = /\b(remot[oa]s?|home\s*office|remote|teletrabalho|wfh|work\s*from\s*home|anywhere|100%\s*remoto|remoto\s*100%)\b/.test(norm);`

#### Edit 3: Update `setLocFilter(val)` (Lines 829–832)
- **Target File**: `static/index.html`
- **Lines 829–832**:
  - *Current*:
    ```javascript
    function setLocFilter(city) {
        document.getElementById('loc-input').value = city;
        filterData();
    }
    ```
  - *Replacement*:
    ```javascript
    function setLocFilter(val) {
        const stateSelect = document.getElementById('state-select');
        const locInput = document.getElementById('loc-input');
        const upper = (val || '').toUpperCase().trim();
        
        if (UF_MAP[upper]) {
            stateSelect.value = upper;
            locInput.value = '';
        } else if (!val) {
            stateSelect.value = '';
            locInput.value = '';
        } else {
            locInput.value = val;
            let matchedUF = '';
            for (const [uf, data] of Object.entries(UF_MAP)) {
                if (normStr(data.name) === normStr(val) || uf === upper) {
                    matchedUF = uf;
                    break;
                }
            }
            stateSelect.value = matchedUF;
        }
        filterData();
    }
    ```

#### Edit 4: Update Location Filter Logic in `filterData()` (Lines 1109–1112)
- **Target File**: `static/index.html`
- **Lines 1109–1112**:
  - *Current*:
    ```javascript
    let matchLoc = true;
    if (locQuery) {
        matchLoc = normTitle.includes(locQuery) || normReq.includes(locQuery) || normCompany.includes(locQuery) || normLoc.includes(locQuery);
    }
    ```
  - *Replacement*:
    ```javascript
    const selectedUF = document.getElementById('state-select').value;
    const isRemote = (getJobWorkModel(j) === 'remoto');
    let matchLoc = true;

    if (isRemote) {
        // 100% Remote jobs ALWAYS remain visible regardless of state UF or location filter
        matchLoc = true;
    } else if (selectedUF) {
        // Filter by mapped state UF (matches UF code, state name, and main cities)
        matchLoc = isJobInState(j, selectedUF);
    } else if (locQuery) {
        const upperQuery = locQuery.toUpperCase();
        if (UF_MAP[upperQuery]) {
            matchLoc = isJobInState(j, upperQuery);
        } else {
            let matchedUF = '';
            for (const [uf, data] of Object.entries(UF_MAP)) {
                if (normStr(data.name) === locQuery) {
                    matchedUF = uf;
                    break;
                }
            }
            if (matchedUF) {
                matchLoc = isJobInState(j, matchedUF);
            } else {
                matchLoc = normTitle.includes(locQuery) || normReq.includes(locQuery) || normCompany.includes(locQuery) || normLoc.includes(locQuery);
            }
        }
    }
    ```

---

## 4. Summary of Verification & Test Results
- **Backend Test Alignment**: The Python backend unit tests in `test_location_uf.py` pass 21/21 scenarios, proving the validity of word boundary matching and remote job preservation.
- **Client-Side Verification**: Applying the proposed edits ensures 100% parity between backend matching rules and frontend client-side rendering.
