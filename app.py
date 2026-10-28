
from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

DATA_FILE = "ev_market_test.csv"


def load_data():
    df = pd.read_csv(DATA_FILE)
    df.columns = df.columns.str.strip()
    return df


@app.route("/")
def home():
    df = load_data()

    total_vehicles = len(df)
    total_sales = df["annual_sales_units"].sum()
    avg_price = df["price_usd"].mean()
    avg_rating = df["customer_rating"].mean()

    # 1. Manufacturer sales
    manufacturer_sales = (
        df.groupby("manufacturer", as_index=False)["annual_sales_units"]
        .sum()
        .sort_values("annual_sales_units", ascending=False)
        .head(10)
    )
    fig1 = px.bar(
        manufacturer_sales,
        x="manufacturer",
        y="annual_sales_units",
        title="Top 10 Manufacturers by Annual Sales",
        labels={
            "manufacturer": "Manufacturer",
            "annual_sales_units": "Annual Sales Units",
        },
        color="annual_sales_units",
        color_continuous_scale="teal",
    )
    fig1.update_layout(template="plotly_dark")

    # 2. Battery technology
    battery_data = (
        df.groupby("battery_type", as_index=False)
        .agg(
            vehicles=("vehicle_id", "count"),
            avg_cycle_life=("battery_cycle_life", "mean"),
        )
    )
    fig2 = px.bar(
        battery_data,
        x="battery_type",
        y="avg_cycle_life",
        title="Average Battery Cycle Life by Technology",
        labels={
            "battery_type": "Battery Technology",
            "avg_cycle_life": "Average Cycle Life",
        },
        color="battery_type",
    )
    fig2.update_layout(template="plotly_dark", showlegend=False)

    # 3. Vehicle categories
    category_data = (
        df.groupby("category", as_index=False)["annual_sales_units"]
        .sum()
        .sort_values("annual_sales_units", ascending=False)
    )
    fig3 = px.pie(
        category_data,
        names="category",
        values="annual_sales_units",
        title="Annual Sales Share by Vehicle Category",
        hole=0.45,
    )
    fig3.update_layout(template="plotly_dark")

    # 4. Customer ratings
    fig4 = px.histogram(
        df,
        x="customer_rating",
        nbins=20,
        title="Customer Rating Distribution",
        labels={"customer_rating": "Customer Rating"},
        color_discrete_sequence=["#21d4a7"],
    )
    fig4.update_layout(template="plotly_dark")

    # 5. Price analysis
    fig5 = px.scatter(
        df,
        x="range_km",
        y="price_usd",
        color="category",
        hover_name="model_name",
        title="Vehicle Price vs Driving Range",
        labels={
            "range_km": "Driving Range (km)",
            "price_usd": "Price (USD)",
        },
    )
    fig5.update_layout(template="plotly_dark")

    charts = [
        pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
        for fig in [fig1, fig2, fig3, fig4, fig5]
    ]

    top_manufacturer = (
        manufacturer_sales.iloc[0]["manufacturer"]
        if not manufacturer_sales.empty
        else "N/A"
    )

    return render_template(
        "index.html",
        total_vehicles=f"{total_vehicles:,}",
        total_sales=f"{total_sales:,.0f}",
        avg_price=f"${avg_price:,.0f}",
        avg_rating=f"{avg_rating:.2f} / 5",
        top_manufacturer=top_manufacturer,
        charts=charts,
    )


if __name__ == "__main__":
    app.run(debug=True)
