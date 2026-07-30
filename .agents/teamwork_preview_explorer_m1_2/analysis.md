# Analysis Report: Requirement R2 — UF Mapping (27 States) & Location Filtering

**Explorer**: Explorer 2 (Frontend Specialist)  
**Target File**: `static/index.html`  
**Date**: 2026-07-21  

---

## 1. Executive Summary

An audit of `static/index.html` for **Requirement R2 (UF Mapping for 27 Brazilian States & Location Filtering)** was conducted. 

### Core Findings
1. **UI Dropdown**: Present in HTML (`<select id="state-select">` lines 473-503) containing all 27 Brazilian state options (AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PR, PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO) plus "Exterior / Internacional".
2. **UF Mapping Object in JS**: **MISSING**. There is no JavaScript mapping object dictionary (e.g., `UF_MAPPINGS`) mapping UF acronyms to their full state names (e.g., `SP` -> `"São Paulo"`) or major cities (e.g., `SP` -> `["São Paulo", "Campinas", "Santos", "Ribeirão Preto", ...]`).
3. **Location Matching Logic**: **FLAWED**. Selecting a state from `#state-select` calls `setLocFilter(value)`, which simply copies the 2-letter UF code (e.g., `"SP"`) directly into `#loc-input` and runs `filterData()`.
   - `filterData()` checks `normLoc.includes(locQuery) || normTitle.includes(locQuery) || ...`
   - Matching raw `"sp"` fails to match jobs whose location is stored as `"São Paulo"` (without `"SP"`) or major cities (e.g., `"Campinas"`).
   - Unbounded substring matching of 2-letter codes creates massive false positives (e.g. `"sp"` matches `"especialista"`, `"resposta"`, `"spring"`; `"ma"` matches `"master"`, `"manager"`; `"se"` matches `"senior"`, `"segurança"`; `"pr"` matches `"programador"`, `"projeto"`).

---

## 2. Detailed Inspection & Evidence Chain

### 2.1 UI Component Inspection (`static/index.html`: lines 473-503)
```html
<select id="state-select" class="input-text" style="height:30px; padding:0 8px; margin-bottom:8px; width:100%; cursor:pointer;" onchange="setLocFilter(this.value)">
    <option value="">-- Todos os 27 Estados (UF) --</option>
    <option value="SP">São Paulo (SP)</option>
    <option value="RJ">Rio de Janeiro (RJ)</option>
    <option value="MG">Minas Gerais (MG)</option>
    <option value="PR">Paraná (PR)</option>
    <option value="RS">Rio Grande do Sul (RS)</option>
    <option value="SC">Santa Catarina (SC)</option>
    <option value="BA">Bahia (BA)</option>
    <option value="PE">Pernambuco (PE)</option>
    <option value="CE">Ceará (CE)</option>
    <option value="DF">Distrito Federal (DF)</option>
    <option value="ES">Espírito Santo (ES)</option>
    <option value="GO">Goiás (GO)</option>
    <option value="MA">Maranhão (MA)</option>
    <option value="MT">Mato Grosso (MT)</option>
    <option value="MS">Mato Grosso do Sul (MS)</option>
    <option value="PA">Pará (PA)</option>
    <option value="PB">Paraíba (PB)</option>
    <option value="AM">Amazonas (AM)</option>
    <option value="RN">Rio Grande do Norte (RN)</option>
    <option value="AL">Alagoas (AL)</option>
    <option value="PI">Piauí (PI)</option>
    <option value="SE">Sergipe (SE)</option>
    <option value="RO">Rondônia (RO)</option>
    <option value="TO">Tocantins (TO)</option>
    <option value="AC">Acre (AC)</option>
    <option value="AP">Amapá (AP)</option>
    <option value="RR">Roraima (RR)</option>
    <option value="Exterior">Exterior / Internacional</option>
</select>
```
* **Observation**: All 27 UFs are present in the HTML dropdown values and label strings.

### 2.2 UF Handler Logic (`static/index.html`: lines 829-832)
```javascript
function setLocFilter(city) {
    document.getElementById('loc-input').value = city;
    filterData();
}
```
* **Observation**: Selecting `SP` in `#state-select` triggers `setLocFilter('SP')`, setting `document.getElementById('loc-input').value = 'SP'`.

### 2.3 Location Filter Matching Logic (`static/index.html`: lines 1080-1131)
```javascript
function filterData() {
    const query = normStr(document.getElementById('search-input').value);
    const locQuery = normStr(document.getElementById('loc-input').value);
    ...
    viewData = allData.filter(j => {
        const normTitle = normStr(j.title);
        const normReq = normStr(j.requirements);
        const normCompany = normStr(j.company);
        const normLoc = normStr(j.location);
        ...
        let matchLoc = true;
        if (locQuery) {
            matchLoc = normTitle.includes(locQuery) || normReq.includes(locQuery) || normCompany.includes(locQuery) || normLoc.includes(locQuery);
        }
        ...
        return matchQuery && matchLoc && matchPlat && matchCat && matchWm && matchSen;
    });
}
```

---

## 3. Flaw Analysis & Impact Matrix

| Requirement Aspect | Current Status | Flaw Description | Impact |
|---|---|---|---|
| **27 UFs mapped to full state names** | ❌ FAILED | No JS mapping object exists. `SP` is not mapped to `"São Paulo"` or `"Sao Paulo"`. | Selecting `SP` misses jobs titled or located with `"São Paulo"` if `"SP"` acronym isn't explicitly in the text. |
| **27 UFs mapped to major cities** | ❌ FAILED | No city lists per state in JS. `SP` does not map to `"Campinas"`, `"Santos"`, `"Guarulhos"`, etc. | Selecting `SP` filters out jobs in major cities of São Paulo state. |
| **Location Matching Precision** | ❌ FAILED | Simple substring `includes("sp")`, `includes("se")`, `includes("ma")`. | False positive pollution: `SP` matches `"especialista"`, `MA` matches `"manager"`, `SE` matches `"senior"`, `PR` matches `"programador"`. |

---

## 4. Proposed Solution & Implementation Blueprint

To achieve 100% compliance with Requirement R2, the implementer should add a complete `UF_MAPPING` structure in `static/index.html` and update the location matching logic in `filterData()`.

### 4.1 Proposed `UF_MAPPING` Structure (JavaScript)
```javascript
const UF_MAPPING = {
    "AC": { name: "Acre", cities: ["Rio Branco", "Cruzeiro do Sul", "Sena Madureira"] },
    "AL": { name: "Alagoas", cities: ["Maceió", "Arapiraca", "Rio Largo", "Palmeira dos Índios"] },
    "AP": { name: "Amapá", cities: ["Macapá", "Santana", "Laranjal do Jari"] },
    "AM": { name: "Amazonas", cities: ["Manaus", "Parintins", "Itacoatiara", "Manacapuru"] },
    "BA": { name: "Bahia", cities: ["Salvador", "Feira de Santana", "Vitória da Conquista", "Camaçari", "Juazeiro", "Lauro de Freitas", "Ilhéus", "Itabuna"] },
    "CE": { name: "Ceará", cities: ["Fortaleza", "Caucaia", "Juazeiro do Norte", "Maracanaú", "Sobral"] },
    "DF": { name: "Distrito Federal", cities: ["Brasília", "Taguatinga", "Ceilândia", "Águas Claras", "Gama"] },
    "ES": { name: "Espírito Santo", cities: ["Vitória", "Vila Velha", "Serra", "Cariacica", "Cachoeiro de Itapemirim", "Linhares"] },
    "GO": { name: "Goiás", cities: ["Goiânia", "Aparecida de Goiânia", "Anápolis", "Rio Verde", "Luziânia"] },
    "MA": { name: "Maranhão", cities: ["São Luís", "Imperatriz", "São José de Ribamar", "Timon", "Caxias"] },
    "MT": { name: "Mato Grosso", cities: ["Cuiabá", "Várzea Grande", "Rondonópolis", "Sinop", "Tangará da Serra"] },
    "MS": { name: "Mato Grosso do Sul", cities: ["Campo Grande", "Dourados", "Três Lagoas", "Corumbá"] },
    "MG": { name: "Minas Gerais", cities: ["Belo Horizonte", "Uberlândia", "Contagem", "Juiz de Fora", "Betim", "Montes Claros", "Ribeirão das Neves", "Uberaba", "Governador Valadares", "Ipatinga"] },
    "PA": { name: "Pará", cities: ["Belém", "Ananindeua", "Santarém", "Marabá", "Parauapebas", "Castanhal"] },
    "PB": { name: "Paraíba", cities: ["João Pessoa", "Campina Grande", "Santa Rita", "Patos"] },
    "PR": { name: "Paraná", cities: ["Curitiba", "Londrina", "Maringá", "Ponta Grossa", "Cascavel", "São José dos Pinhais", "Foz do Iguaçu", "Colombo"] },
    "PE": { name: "Pernambuco", cities: ["Recife", "Jaboatão dos Guararapes", "Olinda", "Caruaru", "Petrolina", "Paulista"] },
    "PI": { name: "Piauí", cities: ["Teresina", "Parnaíba", "Picos", "Piripiri"] },
    "RJ": { name: "Rio de Janeiro", cities: ["Rio de Janeiro", "São Gonçalo", "Duque de Caxias", "Nova Iguaçu", "Niterói", "Campos dos Goytacazes", "Belford Roxo", "São João de Meriti", "Petrópolis", "Volta Redonda", "Macaé"] },
    "RN": { name: "Rio Grande do Norte", cities: ["Natal", "Mossoró", "Parnamirim", "São Gonçalo do Amarante"] },
    "RS": { name: "Rio Grande do Sul", cities: ["Porto Alegre", "Caxias do Sul", "Canoas", "Pelotas", "Santa Maria", "Gravataí", "Viamão", "Novo Hamburgo", "São Leopoldo", "Passo Fundo"] },
    "RO": { name: "Rondônia", cities: ["Porto Velho", "Ji-Paraná", "Ariquemes", "Vilhena", "Cacoal"] },
    "RR": { name: "Roraima", cities: ["Boa Vista", "Rorainópolis", "Caracaraí"] },
    "SC": { name: "Santa Catarina", cities: ["Florianópolis", "Joinville", "Blumenau", "São José", "Chapecó", "Criciúma", "Itajaí", "Jaraguá do Sul", "Palhoça", "Balneário Camboriú"] },
    "SP": { name: "São Paulo", cities: ["São Paulo", "Campinas", "Guarulhos", "São Bernardo do Campo", "Santo André", "Osasco", "São José dos Campos", "Ribeirão Preto", "Sorocaba", "Santos", "Mauá", "SJC", "Jundiaí", "Piracicaba", "Bauru", "Franca", "Itaquaquecetuba"] },
    "SE": { name: "Sergipe", cities: ["Aracaju", "Nossa Senhora do Socorro", "Lagarto", "Itabaiana"] },
    "TO": { name: "Tocantins", cities: ["Palmas", "Araguaína", "Gurupi", "Porto Nacional"] }
};
```

### 4.2 Enhanced Matching Function (`filterData`)
```javascript
function getLocKeywords(locInput) {
    const raw = (locInput || '').trim();
    if (!raw) return [];
    const upper = raw.toUpperCase();
    
    // Check if input is a known UF acronym
    if (UF_MAPPING[upper]) {
        const ufData = UF_MAPPING[upper];
        const keywords = [upper, ufData.name];
        ufData.cities.forEach(c => keywords.push(c));
        return keywords.map(k => normStr(k));
    }

    return [normStr(raw)];
}

// Inside filterData():
let matchLoc = true;
if (locQuery) {
    const locKeywords = getLocKeywords(document.getElementById('loc-input').value);
    matchLoc = locKeywords.some(kw => 
        normLoc.includes(kw) || 
        normTitle.includes(kw) || 
        normReq.includes(kw) || 
        normCompany.includes(kw)
    );
}
```

---

## 5. Conclusion

Requirement R2 currently fails in `static/index.html` due to missing JS mapping data for all 27 Brazilian states and naive substring matching logic. Implementing the proposed `UF_MAPPING` structure and location keyword expansion will fully satisfy Requirement R2 without regression.
