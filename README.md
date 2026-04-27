# 📦 NFEI – Nutrition-Sensitive Food Environment Index (Python Package)

![PyPI](https://img.shields.io/pypi/v/nfei)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🧠 What is the NFEI?

The **Nutrition-Sensitive Food Environment Index (N-FEI)** is a composite index designed to assess food environments through a **nutrition and public health lens**, capturing how food availability, accessibility, infrastructure, and exposure to unhealthy foods interact to influence malnutrition risk.

It is grounded in the definition of food environments as:

> “the collective physical, economic, policy, and sociocultural surroundings, opportunities, and conditions that influence people’s food and beverage choices and nutritional status.”

Unlike traditional indices that focus mainly on affordability, the N-FEI integrates:

- Food diversity (dietary adequacy)
- Spatial accessibility (proximity-based exposure)
- Vendor availability (temporal access)
- Infrastructure (water and sanitation)
- Unhealthy food exposure (risk factors)

The index is constructed from **nine indicators**, normalized and aggregated into a **0–10 scale**, where higher values indicate healthier food environments.

📄 **Full methodology and validation:**  
https://doi.org/10.55845/jos-2025-1116

---

## 🎯 Purpose of this Package

This package provides a **production-ready implementation** of the N-FEI methodology.

It is designed to:

- Translate research methodology into reusable code
- Standardize indicator computation across datasets
- Enable scalable, reproducible food environment analysis
- Reduce reliance on ad-hoc notebooks

---

## ⚙️ Installation

```bash
pip install nfei
```

Or locally:

```bash
pip install -e .
```

---

## 🚀 Quick Start (Core Example)

### Market-Level Diversity Score

```python
import pandas as pd
import nfei

df = pd.DataFrame({
    "vendor_id": [1, 2],
    "food_groups": [
        "grains,vegetables,fruits",
        "grains,meat"
    ]
})

df = nfei.add_market_level_diversity_score(
    df,
    column="food_groups",
    max_groups=10
)

print(df["market_diversity_score"])
```

---

## 🧱 Package Architecture

### 1. Availability Module
Captures **temporal access to food vendors**

- Daily availability (weighted by time of day)
- Weekly availability (days open)

Reflects real-world accessibility patterns where:
- Morning to evening has higher weight than night
- Full-day and full-week operations imply maximum availability

---

### 2. Diversity Module
Captures **nutritional quality of the food environment**

Includes:

- Vendor Healthy Food Diversity Score (MDD-W based)
- Environment-level diversity (spatial aggregation)
- Unhealthy food exposure

Key idea:
> Food diversity is a proxy for nutrient adequacy and malnutrition risk.

---

### 3. Color Diversity Module
Captures **bioactive nutrient diversity** using ProColor

- Maps fruits and vegetables into 6 color groups
- Counts presence across vendors or environments

This complements traditional food group diversity by capturing **micronutrient richness**

---

### 4. Density Module
Captures **market structure and saturation**

- Vendors per population
- Vendors per km²

Used to assess:
- Over-concentration vs under-service
- Accessibility at population level

---

### 5. Spatial Module
Captures **environmental exposure**

- Distance calculations
- Buffer-based aggregation (e.g., 50m radius)

This is critical because:
> Consumers interact with food environments, not just individual vendors

---

### 6. Scaling Module
Handles **normalization and comparability**

- Aligns indicators to common scale (0–10)
- Supports inversion (e.g., unhealthy food)

---

### 7. Validation Module
Ensures **data quality and robustness**

- Outlier detection
- Spatial consistency checks

---

## 🔄 How Everything Flows Together

The pipeline follows the research methodology:

1. Raw vendor data  
2. Indicator construction  
3. Spatial aggregation  
4. Normalization  
5. Aggregation (mean across indicators)  
6. Final NFEI score  

Result:

```text
Indicators → Normalized Scores → Composite Index (0–10)
```

---

## 📊 Indicators Implemented

The package supports computation of all core NFEI indicators:

1. Vendor Healthy Food Diversity Score  
2. Vendor Environment Healthy Food Diversity Score  
3. Vendor ProColor Diversity Score  
4. Vendor Environment ProColor Diversity Score  
5. Access to Sanitation  
6. Vendor Availability  
7. Vendors per Population  
8. Vendors per km²  
9. Unhealthy Food Count (inverted)  

---

## 🧪 Data Assumptions

- Binary variables are coded as 0/1  
- Multi-response fields are comma-separated strings  
- Spatial coordinates are in decimal degrees  
- Missing values must be handled explicitly  

---

## 📁 Examples

See the `examples/` folder for:

- End-to-end pipeline
- Multi-country dataset processing
- Spatial aggregation workflows
- Full NFEI computation

---

## 🧠 Design Principles

- Research-aligned implementation  
- Reproducibility first  
- Modular and extensible  
- Transparent computation logic  

---

## 📌 Citation

If you use this package, cite:

Akingbemisilu et al. (2025)  
*The Nutrition-Sensitive Food Environment Index*  
https://doi.org/10.55845/jos-2025-1116

---

## 🤝 Contributing

Contributions are welcome.

Please ensure:
- Functions follow the methodological framework
- Clear documentation is provided
- Tests are included

---

## 📬 Contact

For questions, collaborations, or extensions, open an issue or reach out.
