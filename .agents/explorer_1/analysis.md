# Seniority Radio Button Analysis — static/index.html

## Executive Summary
This document provides the exact location, context, and required HTML snippet to add a new radio button for the seniority level in `static/index.html`.

---

## 1. Location of Existing Seniority Radio Buttons

- **File Path**: `C:/Users/99196/OneDrive/Documentos/vagas_bot/static/index.html`
- **Section / Screen**: Screen 5 (`<main id="screen-settings" class="screen">`) — "Orquestração" / Settings tab.
- **Parent Container**: `<div class="settings-group" style="margin-bottom: 20px;">` -> inner `<div>` for "Nível de Senioridade".
- **Flex Container**: `<div style="display:flex; gap:10px; flex-wrap: wrap;">`
- **Line Numbers**: Lines 486–496 in `static/index.html`.

### Existing HTML Structure (Lines 486–496)
```html
<div>
    <label style="color:var(--text-muted); font-size: 0.9rem; margin-bottom:5px; display:block;">Nível de Senioridade</label>
    <div style="display:flex; gap:10px; flex-wrap: wrap;">
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Todos" checked> Todos</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Júnior"> Júnior</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Pleno"> Pleno</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Sênior"> Sênior</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Jovem Aprendiz"> Jovem Aprendiz</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Ganhar Experiência"> Ganhar Experiência</label>
    </div>
</div>
```

---

## 2. New Radio Button Specification

- **Label**: `Iniciantes Tudo (Jovem Aprendiz + Ganhar Experiência)`
- **Value**: `iniciantes tudo`
- **Attribute `name`**: `seniority`
- **Styling**: `display:flex; align-items:center; gap:5px;` (matches sibling radio labels)

### Single-Line HTML Code to Add
```html
<label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="iniciantes tudo"> Iniciantes Tudo (Jovem Aprendiz + Ganhar Experiência)</label>
```

---

## 3. Updated Code Block (Proposed Placement)

Adding the new radio button after "Ganhar Experiência" (or at the desired position within the container):

```html
<div>
    <label style="color:var(--text-muted); font-size: 0.9rem; margin-bottom:5px; display:block;">Nível de Senioridade</label>
    <div style="display:flex; gap:10px; flex-wrap: wrap;">
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Todos" checked> Todos</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Júnior"> Júnior</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Pleno"> Pleno</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Sênior"> Sênior</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Jovem Aprendiz"> Jovem Aprendiz</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Ganhar Experiência"> Ganhar Experiência</label>
        <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="iniciantes tudo"> Iniciantes Tudo (Jovem Aprendiz + Ganhar Experiência)</label>
    </div>
</div>
```

---

## 4. Technical Impact & JavaScript Integration

1. **JavaScript Handling**:
   - In `static/index.html` at line 623:
     ```javascript
     const level = document.querySelector('input[name="seniority"]:checked').value;
     ```
   - Selecting this radio button will evaluate `level` to `"iniciantes tudo"`.
   - The value is sent via `POST` to `/api/trigger` in payload `{ platforms: platforms, keyword: keyword, level: level }`.

2. **Styling & Layout**:
   - The outer container uses `flex-wrap: wrap; gap: 10px;`.
   - The label will naturally wrap to the next line if screen width is narrow, matching the responsive behavior of other options.
