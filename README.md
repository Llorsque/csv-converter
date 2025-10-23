# CSV Stramien Converter (Minimal)

**Doel:** Excel/CSV met verenigingsdata omzetten naar vast CSV-stramien.

## Gebruik (GitHub)
1. Upload je `.xlsx` of `.csv` naar de map `input/` (Add file → Upload files).
2. Ga naar **Actions** → workflow **Convert Excel to CSV Stramien (Minimal)**.
3. Download artifact **converted-csv** met je resultaten.

## Gebruik (lokaal)
```bash
pip install -r requirements.txt
python excel_to_stramien.py --input input --template template/import-organizations.csv --output output
# Optioneel sheet:
python excel_to_stramien.py --input input --sheet "Blad1"
```

Output: `output/<bron>-stramien.csv` met kolomvolgorde exact zoals in `template/import-organizations.csv`.
