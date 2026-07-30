# Handoff Report — explorer_1

## 1. Observation
- File inspected: `C:/Users/99196/OneDrive/Documentos/vagas_bot/static/index.html` (805 lines total).
- Located seniority radio buttons inside `<main id="screen-settings" class="screen">` at lines 486–496:
  ```html
  486:             <div>
  487:                 <label style="color:var(--text-muted); font-size: 0.9rem; margin-bottom:5px; display:block;">Nível de Senioridade</label>
  488:                 <div style="display:flex; gap:10px; flex-wrap: wrap;">
  489:                     <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Todos" checked> Todos</label>
  490:                     <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Júnior"> Júnior</label>
  491:                     <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Pleno"> Pleno</label>
  492:                     <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Sênior"> Sênior</label>
  493:                     <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Jovem Aprendiz"> Jovem Aprendiz</label>
  494:                     <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="Ganhar Experiência"> Ganhar Experiência</label>
  495:                 </div>
  496:             </div>
  ```
- Checked JavaScript logic at line 623:
  `const level = document.querySelector('input[name="seniority"]:checked').value;`
  This dynamically extracts the `value` attribute of whichever radio button with `name="seniority"` is currently checked.

## 2. Logic Chain
1. `static/index.html` contains the settings tab under `<main id="screen-settings" class="screen">`.
2. Within this section, line 488 uses `<div style="display:flex; gap:10px; flex-wrap: wrap;">` to hold radio options with `name="seniority"`.
3. Adding `<label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="iniciantes tudo"> Iniciantes Tudo (Jovem Aprendiz + Ganhar Experiência)</label>` into this flex wrapper integrates seamlessly into the UI layout.
4. When selected, the script at line 623 reads `level = "iniciantes tudo"` and sends it in the JSON payload to `/api/trigger`.

## 3. Caveats
- Backend API (`/api/trigger` or python backend service) needs to handle the string `"iniciantes tudo"` if custom filtering logic is required for combined categories. HTML change itself is complete and non-breaking for frontend.

## 4. Conclusion
To add the "Iniciantes Tudo (Jovem Aprendiz + Ganhar Experiência)" option with value `"iniciantes tudo"`, append the following line inside the `<div style="display:flex; gap:10px; flex-wrap: wrap;">` container (lines 488–495) in `static/index.html`:
```html
<label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="iniciantes tudo"> Iniciantes Tudo (Jovem Aprendiz + Ganhar Experiência)</label>
```

## 5. Verification Method
- Open `C:/Users/99196/OneDrive/Documentos/vagas_bot/static/index.html` in a text editor or browser.
- Verify lines 486–496 contain the `seniority` radio buttons.
- Confirm the new `<label>` element includes `name="seniority"` and `value="iniciantes tudo"`.
