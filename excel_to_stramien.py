#!/usr/bin/env python3
import argparse, re
import pandas as pd
from difflib import get_close_matches
from pathlib import Path

def norm(s: str) -> str:
    s = str(s).strip().lower()
    s = re.sub(r"[\s._-]+", " ", s)
    return s

SYNONYMS = {
  "name": ["vereniging","club","clubnaam","naam vereniging","organisatienaam","naam"],
  "description": ["omschrijving","beschrijving","about","info"],
  "email": ["e-mail","mail","e-mailadres","emailadres"],
  "phone": ["telefoon","telefoonnummer","mobiel","gsm","phone"],
  "website": ["url","site","web","homepage"],
  "facebook_url": ["facebook","facebook link","fb","fb url"],
  "instagram_url": ["instagram","insta","ig","instagram link"],
  "youtube_url": ["youtube","yt","youtube link","youtube kanaal"],
  "street": ["straat","adres","bezoekadres","street"],
  "house_number": ["huisnummer","nr","nummer","huis nr","hnr"],
  "zipcode": ["postcode","post code","zip","zip code"],
  "city": ["plaats","woonplaats","stad","dorp","vestigingsplaats"],
  "country": ["land","country"],
  "notes": ["notities","opmerkingen","memo","remarks"]
}

def load_template_cols(template_csv: Path):
    tpl = pd.read_csv(template_csv, nrows=1)
    return list(tpl.columns)

def read_table(path: Path, sheet: str | None = None) -> pd.DataFrame:
    if path.suffix.lower() == ".xlsx":
        if sheet is None:
            xl = pd.ExcelFile(path)
            sheet = xl.sheet_names[0]
        return pd.read_excel(path, sheet_name=sheet)
    return pd.read_csv(path)

def build_mapping(src_cols, template_cols, cutoff=0.86):
    norm_to_src = {norm(c): c for c in src_cols}
    mapping = {}
    for t in template_cols:
        tn = norm(t)
        if tn in norm_to_src:
            mapping[t] = norm_to_src[tn]
    for t in template_cols:
        if t in mapping: continue
        for alt in SYNONYMS.get(t, []):
            an = norm(alt)
            if an in norm_to_src:
                mapping[t] = norm_to_src[an]; break
    for t in template_cols:
        if t in mapping: continue
        tn = norm(t)
        match = get_close_matches(tn, list(norm_to_src.keys()), n=1, cutoff=cutoff)
        if match:
            mapping[t] = norm_to_src[match[0]]
    return mapping

def convert_df(df, template_cols, mapping):
    out = pd.DataFrame(columns=template_cols)
    for t in template_cols:
        out[t] = df[mapping[t]] if t in mapping else ""
    return out

def main():
    p = argparse.ArgumentParser(description="Excel/CSV -> vast stramien CSV (minimaal)")
    p.add_argument("--input", default="input", help="bestand of map (default: input)")
    p.add_argument("--template", default="template/import-organizations.csv", help="stramien CSV")
    p.add_argument("--output", default="output", help="outputmap (default: output)")
    p.add_argument("--sheet", default=None, help="Excel sheetnaam (optioneel)")
    p.add_argument("--cutoff", type=float, default=0.86, help="fuzzy cutoff (0..1)")
    args = p.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output); output_dir.mkdir(parents=True, exist_ok=True)
    template_cols = load_template_cols(Path(args.template))

    files = []
    if input_path.is_dir():
        files += list(input_path.glob("*.xlsx"))
        files += list(input_path.glob("*.csv"))
    elif input_path.exists():
        files = [input_path]
    else:
        raise SystemExit(f"Geen input op: {input_path}")

    if not files:
        raise SystemExit("Geen .xlsx of .csv in input/")

    for f in files:
        df = read_table(f, sheet=args.sheet)
        mapping = build_mapping(list(df.columns), template_cols, cutoff=args.cutoff)
        out = convert_df(df, template_cols, mapping)
        out_name = output_dir / f"{f.stem}-stramien.csv"
        out.to_csv(out_name, index=False, encoding="utf-8")
        print(f"OK: {f.name} -> {out_name.name}")
        print("Mapping (template <- bron):")
        for t in template_cols:
            print(f"  {t} <- {mapping.get(t,'(leeg)')}")

if __name__ == "__main__":
    main()
