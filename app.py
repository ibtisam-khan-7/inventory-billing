from flask import Flask, render_template, request, redirect, make_response
from weasyprint import HTML
from datetime import date
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["inventory_db"]
products_col = db["products"]


@app.route("/")
def list_products():
    all_products = list(products_col.find())
    return render_template("products.html", products=all_products)


@app.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        quantity = int(request.form["quantity"])
        products_col.insert_one({"name": name, "price": price, "quantity": quantity})
        return redirect("/")
    return render_template("add_product.html")


# Dashboard Route
@app.route("/dashboard")
def dashboard():
    all_products = list(products_col.find())
    total_products = len(all_products)
    total_quantity = sum(p["quantity"] for p in all_products)
    total_value = sum(p["price"] * p["quantity"] for p in all_products)

    # Data for Chart.js
    names = [p["name"] for p in all_products]
    quantities = [p["quantity"] for p in all_products]

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_quantity=total_quantity,
        total_value=total_value,
        names=names,
        quantities=quantities,
    )


# Sales Report Route
@app.route("/sales-report")
def sales_report():
    all_products = list(products_col.find())
    total_value = sum(p["price"] * p["quantity"] for p in all_products)
    date_today = date.today().strftime("%B %Y")

    return render_template(
        "sales_report.html",
        products=all_products,
        total_value=total_value,
        date_today=date_today
    )


# Download PDF Route
@app.route("/download-report")
def download_report():
    all_products = list(products_col.find())
    total_value = sum(p["price"] * p["quantity"] for p in all_products)
    date_today = date.today().strftime("%B %Y")

    html = render_template(
        "sales_report_pdf.html",
        products=all_products,
        total_value=total_value,
        date_today=date_today
    )

    pdf = HTML(string=html).write_pdf()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=sales_report_{date_today}.pdf"
    return response


if __name__ == "__main__":
    app.run(debug=True)
