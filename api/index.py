from flask import Flask, render_template, request, send_file
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

UPLOAD_FOLDER = "reports"

# ---------------- RABIN KARP ---------------- #

def rabin_karp(text, pattern, d=256, q=101):

    n = len(text)
    m = len(pattern)

    h = pow(d, m - 1) % q

    p = 0
    t = 0

    result = []

    for i in range(m):
        p = (d * p + ord(pattern[i])) % q
        t = (d * t + ord(text[i])) % q

    for s in range(n - m + 1):

        if p == t:

            if text[s:s + m] == pattern:
                result.append(s)

        if s < n - m:

            t = (
                d * (t - ord(text[s]) * h)
                + ord(text[s + m])
            ) % q

            if t < 0:
                t += q

    return result


# ---------------- PDF REPORT ---------------- #

def generate_pdf(result_data):

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    pdf_path = os.path.join(UPLOAD_FOLDER, "report.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, 750, "Rabin-Karp Report")

    c.setFont("Helvetica", 12)

    c.drawString(50, 700,
                 f"Text Length: {result_data['text_length']}")

    c.drawString(50, 670,
                 f"Pattern Length: {result_data['pattern_length']}")

    c.drawString(50, 640,
                 f"Pattern Count: {result_data['count']}")

    c.drawString(50, 610,
                 f"Positions: {str(result_data['positions'])}")

    c.drawString(50, 580,
                 f"Execution Time: {result_data['time']} sec")

    c.save()

    return pdf_path


# ---------------- ROUTES ---------------- #

@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        pattern = request.form["pattern"]

        uploaded_file = request.files["file"]

        text = uploaded_file.read().decode("utf-8")

        start = time.time()

        positions = rabin_karp(text, pattern)

        end = time.time()

        result = {
            "text_length": len(text),
            "pattern_length": len(pattern),
            "positions": positions,
            "count": len(positions),
            "time": round(end - start, 6)
        }

        generate_pdf(result)

    return render_template("index.html", result=result)


@app.route("/download")
def download():

    path = "reports/report.pdf"

    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)