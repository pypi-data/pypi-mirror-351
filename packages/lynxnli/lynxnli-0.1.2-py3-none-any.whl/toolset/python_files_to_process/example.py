import pandas as pd
import numpy 


# 1) Read the CSV
df = pd.read_csv(
    "sample_data.csv",
    parse_dates=["Date"]
)

# 2) Quick look
print("=== Head of data ===")
print(df.head(), "\n")

# 3) Summary stats
print("=== Summary statistics ===")
print(df.describe(), "\n")

# 4) Total sales & profit by category
by_cat = df.groupby("Category")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
print("=== Total sales & profit by category ===")
print(by_cat, "\n")

# 5) Monthly sales trend
monthly = df.set_index("Date").resample("M")["Sales"].sum()
print("=== Monthly sales trend ===")
print(monthly, "\n")

# 6) Profit margin
df["Margin"] = df["Profit"] / df["Sales"]
avg_margin = df.groupby("Category")["Margin"].mean().sort_values(ascending=False)
print("=== Average profit margin by category ===")
print(avg_margin.apply(lambda x: f"{x:.1%}"), "\n")

# 7) Correlation between Sales and Profit
corr = df[["Sales", "Profit"]].corr().iloc[0,1]
print(f"=== Correlation between Sales and Profit: {corr:.2f} ===")

print("hello world")

print("helllllllllllllllllloooooooooooooooooooooooooo   remote server")