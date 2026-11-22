from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

CATEGORIES = ["Wi-Fi", "Software", "Hardware", "Account / Password"]
TICKETS = []  # stored in memory (simple, no database)

HEADER = """
<h1>Campus IT Helpdesk</h1>
<a href="/">Home</a> | <a href="/new">Raise Ticket</a> | <a href="/tickets">View Tickets</a>
<hr>
"""


@app.route("/")
def home():
    open_count = sum(1 for t in TICKETS if t["status"] == "Open")
    return render_template_string(
        HEADER + "<p>Report your IT problem here.</p><p>Open tickets: <b>{{ n }}</b></p>",
        n=open_count,
    )


@app.route("/new", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        TICKETS.append({
            "id": len(TICKETS) + 1,
            "name": request.form["name"],
            "category": request.form["category"],
            "description": request.form["description"],
            "status": "Open",
        })
        return redirect("/tickets")
    return render_template_string(HEADER + """
    <h2>Raise a Ticket</h2>
    <form method="post">
      Name: <input name="name" required><br><br>
      Category: <select name="category">
        {% for c in cats %}<option>{{ c }}</option>{% endfor %}
      </select><br><br>
      Problem:<br><textarea name="description" rows="4" cols="40" required></textarea><br><br>
      <button type="submit">Submit</button>
    </form>""", cats=CATEGORIES)


@app.route("/tickets")
def tickets():
    return render_template_string(HEADER + """
    <h2>All Tickets</h2>
    <table border="1" cellpadding="6">
      <tr><th>ID</th><th>Name</th><th>Category</th><th>Problem</th><th>Status</th><th>Action</th></tr>
      {% for t in tickets %}
      <tr>
        <td>{{ t.id }}</td><td>{{ t.name }}</td><td>{{ t.category }}</td>
        <td>{{ t.description }}</td><td>{{ t.status }}</td>
        <td>{% if t.status == "Open" %}
          <form method="post" action="/resolve/{{ t.id }}"><button>Mark Resolved</button></form>
        {% endif %}</td>
      </tr>
      {% else %}
      <tr><td colspan="6">No tickets yet.</td></tr>
      {% endfor %}
    </table>""", tickets=TICKETS)


@app.route("/resolve/<int:tid>", methods=["POST"])
def resolve(tid):
    for t in TICKETS:
        if t["id"] == tid:
            t["status"] = "Resolved"
    return redirect("/tickets")


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)