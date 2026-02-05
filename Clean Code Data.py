# Read raw files from data/raw and write outputs to data/preprocessed
RAW_DIR = Path("data") / "raw"
OUT_DIR = Path("data") / "preprocessed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def tidy_wide_years(df: pd.DataFrame, value_name: str) -> pd.DataFrame:
    id_vars = ["geo", "name"]
    year_cols = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
    out = df.melt(
        id_vars=id_vars,
        value_vars=year_cols,
        var_name="year",
        value_name=value_name
    )
    out["year"] = out["year"].astype(int)
    return out

def main():
    mort_path = RAW_DIR / "child-motality.csv"
    gdp_path = RAW_DIR / "gdp-data.csv"

    print(f"Reading mortality from: {mort_path}")
    mort = pd.read_csv(mort_path)
    mort_tidy = tidy_wide_years(mort, "mortality_rate")
    out_mort = OUT_DIR / "child-mortality_tidy.csv"
    mort_tidy.to_csv(out_mort, index=False)
    print(f"Wrote: {out_mort}")

    print(f"Reading GDP from: {gdp_path}")
    gdp = pd.read_csv(gdp_path)
    gdp_tidy = tidy_wide_years(gdp, "gdpcapita")
    out_gdp = OUT_DIR / "gdp_tidy.csv"
    gdp_tidy.to_csv(out_gdp, index=False)
    print(f"Wrote: {out_gdp}")

    merged = mort_tidy.merge(gdp_tidy, on=["geo", "name", "year"], how="inner", validate="one_to_one")
    merged = merged[["geo", "name", "mortality_rate", "gdpcapita", "year"]]
    out_merged = OUT_DIR / "mortality_gdp_merged.csv"
    merged.to_csv(out_merged, index=False)
    print(f"Wrote: {out_merged}")

if __name__ == "__main__":
    main()

--- FILE: scripts/merge_preserve_na.py ---

import pandas as pd

def main():
    gdp_path = 'data/preprocessed/gdp_tidy.csv'
    mort_path = 'data/preprocessed/child-mortality_tidy.csv'
    out_left = 'data/preprocessed/gdp_tidy_with_mortality_preserve_na.csv'
    out_merged = 'data/preprocessed/mortality_gdp_merged_preserve_na.csv'

    print('Reading', gdp_path)
    gdp = pd.read_csv(gdp_path)
    print('Reading', mort_path)
    mort = pd.read_csv(mort_path)

    # Keep original empties: do NOT fill or interpolate.
    mort['mortality_rate'] = pd.to_numeric(mort['mortality_rate'], errors='coerce')

    # Left join GDP with mortality (mortality cells remain NaN where originally missing)
    gdp_with_mort = gdp.merge(mort[['geo', 'name', 'year', 'mortality_rate']], on=['geo','name','year'], how='left')
    gdp_with_mort = gdp_with_mort[['geo','name','mortality_rate','gdpcapita','year']]
    gdp_with_mort.to_csv(out_left, index=False)
    print('Wrote', out_left)

    # Inner join (only rows where mortality exists) kept for convenience
    merged_inner = mort.merge(gdp[['geo','name','year','gdpcapita']], on=['geo','name','year'], how='inner')
    merged_inner = merged_inner[['geo','name','mortality_rate','gdpcapita','year']]
    merged_inner.to_csv(out_merged, index=False)
    print('Wrote', out_merged)

    # Print Angola sample for verification
    ago_sample = gdp_with_mort[(gdp_with_mort['geo']=='ago') & (gdp_with_mort['year']<=1955)]
    print('\nAngola sample (years <=1955) from preserve-NA merge:')
    print(ago_sample.head(20).to_string(index=False))

if __name__ == '__main__':
    main()

--- FILE: requirements.txt ---

pandas
