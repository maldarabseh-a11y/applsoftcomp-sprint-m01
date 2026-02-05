# NOTE: Data Cleaning Strategy, Visualization Choices, and Insights (Child Mortality + GDP)

## Goal
We transformed two messy raw CSVs (child mortality and GDP per capita) into tidy format and merged them into a single country-year table with columns:

`geo, name, mortality_rate, gdpcapita, year` (with `geo` first)

We also produced a preserve-NA merged dataset so missing mortality values remain missing exactly as in the source data.

---

## Data Cleaning Strategy

### 1) Wide → long (tidy) conversion
**What we did**
- We read each raw dataset from `data/raw/`.
- We identified year columns by matching column names that look like a 4-digit year (`^\d{4}$`).
- We reshaped each dataset from wide format (one column per year) to long/tidy format (one row per country-year) using `pandas.melt()`.

**Why we did it**
- Long/tidy format makes it straightforward to:
  - Merge datasets consistently on `geo, name, year`
  - Filter and plot time series by year
  - Run analyses without handling hundreds of year columns manually

**Outputs**
- `data/preprocessed/child-mortality_tidy.csv` (columns: `geo, name, year, mortality_rate`)
- `data/preprocessed/gdp_tidy.csv` (columns: `geo, name, year, gdpcapita`)

---

### 2) Preserve original missingness (NaNs) by default
**What we did**
- We kept missing mortality values as `NaN` in the tidy mortality dataset.
- We avoided filling, interpolating, forward-filling, or back-filling mortality values in the default workflow.

**Why we did it**
- Missing values reflect real data coverage gaps (not zero mortality).
- Preserving NaNs ensures that any imputation is explicit, intentional, and reversible.
- This prevents “inventing history” for early years where mortality data was never recorded.

---

### 3) Merging approach (two explicit outputs)
We created two merged datasets, because they serve different purposes.

#### A) Preserve-NA merges (recommended for analysis)
**What we did**
- We merged GDP with the original tidy mortality dataset **without any imputation**.
- We produced:
  - A **left join** from GDP → mortality (keeps all GDP rows and preserves missing mortality where unavailable)
  - An **inner join** (keeps only rows where both GDP and mortality exist)

**Why we did it**
- The left-join preserve-NA file is ideal for exploratory work while still keeping missingness honest.
- The inner-join file is convenient when we only want complete pairs for scatter plots or regressions.

**Outputs**
- `data/preprocessed/gdp_tidy_with_mortality_preserve_na.csv` (left join)
- `data/preprocessed/mortality_gdp_merged_preserve_na.csv` (inner join)

#### B) Filled / interpolated merges (optional, for exploration only)
**What we did**
- We optionally created “filled” variants by interpolating within each country over time and using forward/back fill to remove remaining gaps.

**Why we did it**
- Some visualizations or models require a complete panel with no missing values.
- However, this approach can create unrealistic early-year values when the true data starts much later.

**Important caution**
- Linear interpolation + ffill/bfill can move post-1950 values backward into 1800–1949 for countries that only have modern mortality coverage. For that reason, our default analysis uses preserve-NA outputs, and any filled results must be clearly labeled as imputed.

---

## Visualization Choices (and why)

### 1) Scatter plot: Mortality vs GDP per capita (country-year)
**What we plot**
- `mortality_rate` on the y-axis vs `gdpcapita` on the x-axis (log scale for GDP).

**Why**
- GDP per capita is highly skewed; log scaling makes the relationship interpretable.
- This plot highlights the expected negative relationship between income and child mortality.

### 2) Time series: Mortality over time for selected countries
**What we plot**
- `year` vs `mortality_rate` for a small set of countries (small multiples or separate lines).

**Why**
- Time series plots show trends, structural shifts, and where gaps exist in coverage.
- They help validate that we are not accidentally filling or shifting missing values.

### 3) Missingness diagnostics
**What we plot**
- A heatmap (country vs year) or bar chart showing missingness rates by year and/or by country.

**Why**
- Missingness is a major feature of the mortality dataset, especially in early years.
- Any historical interpretation must acknowledge coverage limitations.

**Plotting rule**
- If we ever use the filled dataset, we visually distinguish imputed values (lighter color, dotted lines, or lower alpha) from observed values.

---

## Key Insights from Initial Checks

1) **Historical development pattern**
- Early years tend to show high child mortality and low GDP per capita, consistent with broad historical patterns.

2) **Coverage gaps are substantial**
- Many countries have large blocks of missing mortality values in early years; this is structural missingness rather than random noise.

3) **Preserve-NA merging prevents misleading results**
- Some countries have GDP values where mortality is not observed; preserve-NA merges ensure we do not imply mortality was known when it was not.

---

## Limitations and Risks
- **Coverage bias:** Early-year analyses are limited because mortality data is missing for many countries.
- **Imputation risk:** Interpolation assumes smooth change and can generate unrealistic values when entire time ranges are unobserved.
- **Interpretation caution:** Any models using filled data reflect imputation assumptions and must be reported as such.

---

## Reproducibility (How we regenerate outputs)

### Inputs
- `data/raw/child-motality.csv`
- `data/raw/gdp-data.csv`

### Scripts
- `scripts/preprocess.py`  
  Generates tidy versions of each dataset and an initial merged file.
- `scripts/merge_preserve_na.py`  
  Generates preserve-NA merged outputs without any filling.

### Run commands
```bash
python scripts/preprocess.py
python scripts/merge_preserve_na.py
