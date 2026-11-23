from flask import Flask, request, redirect, render_template_string
from markupsafe import Markup

app = Flask(__name__)

CATEGORIES = ["Wi-Fi", "Software", "Hardware", "Account / Password"]
TICKETS = []  # stored in memory (simple, no database)

LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Campus IT Helpdesk</title>
<style>
  :root {
    --primary: #4f46e5;
    --primary-dark: #4338ca;
    --bg: #f3f4f8;
    --card: #ffffff;
    --text: #1f2937;
    --muted: #6b7280;
    --border: #e5e7eb;
    --green: #16a34a;
    --amber: #d97706;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
  }
  header {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #fff;
    padding: 18px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,.15);
  }
  .wrap { max-width: 960px; margin: 0 auto; padding: 0 20px; }
  .bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
  .brand { font-size: 22px; font-weight: 700; letter-spacing: .3px; }
  .brand small { display: block; font-size: 12px; font-weight: 400; opacity: .85; }
  nav a {
    color: #fff; text-decoration: none; padding: 8px 14px;
    border-radius: 8px; margin-left: 4px; font-size: 15px;
  }
  nav a:hover { background: rgba(255,255,255,.18); }
  nav a.active { background: rgba(255,255,255,.28); font-weight: 600; }
  main { padding: 30px 0 50px; }
  h2 { margin: 0 0 18px; font-size: 24px; }
  .card {
    background: var(--card); border-radius: 14px; padding: 26px;
    box-shadow: 0 2px 10px rgba(0,0,0,.06); border: 1px solid var(--border);
  }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 22px; }
  .stat { background: var(--card); border-radius: 14px; padding: 22px; border: 1px solid var(--border); border-left: 5px solid var(--primary); box-shadow: 0 2px 10px rgba(0,0,0,.05); }
  .stat.open { border-left-color: var(--amber); }
  .stat.done { border-left-color: var(--green); }
  .stat .num { font-size: 36px; font-weight: 700; }
  .stat .lbl { color: var(--muted); font-size: 14px; }
  .btn {
    display: inline-block; background: var(--primary); color: #fff; border: none;
    padding: 11px 20px; border-radius: 9px; font-size: 15px; font-weight: 600;
    cursor: pointer; text-decoration: none;
  }
  .btn:hover { background: var(--primary-dark); }
  .btn.small { padding: 6px 12px; font-size: 13px; background: var(--green); }
  .btn.small:hover { background: #15803d; }
  label { display: block; font-weight: 600; margin: 16px 0 6px; }
  input, select, textarea {
    width: 100%; padding: 11px 12px; border: 1px solid var(--border);
    border-radius: 9px; font-size: 15px; font-family: inherit; background: #fff;
  }
  input:focus, select:focus, textarea:focus {
    outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(79,70,229,.15);
  }
  .form-card { max-width: 560px; }
  .form-card .btn { margin-top: 22px; }
  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; }
  th {
    text-align: left; font-size: 13px; text-transform: uppercase; letter-spacing: .5px;
    color: var(--muted); padding: 12px 14px; border-bottom: 2px solid var(--border);
  }
  td { padding: 14px; border-bottom: 1px solid var(--border); vertical-align: middle; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #fafafa; }
  .badge { display: inline-block; padding: 4px 11px; border-radius: 999px; font-size: 12px; font-weight: 700; }
  .badge.open { background: #fef3c7; color: #92400e; }
  .badge.resolved { background: #dcfce7; color: #166534; }
  .cat { background: #eef2ff; color: #3730a3; }
  .empty { text-align: center; padding: 40px 10px; color: var(--muted); }
  .empty .icon { font-size: 40px; }
  .actions { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px; }
  .intro { color: var(--muted); margin: 0 0 22px; font-size: 16px; }
  footer { text-align: center; color: var(--muted); font-size: 13px; padding: 20px 0 30px; }
  form.inline { margin: 0; }
</style>
</head>
<body>
<header>
  <div class="wrap bar">
    <div class="brand">&#128736; Campus IT Helpdesk<small>Fast help for Wi-Fi, software, hardware and accounts</small></div>
    <nav>
      <a href="/" class="{{ 'active' if active == 'home' }}">Home</a>
      <a href="/new" class="{{ 'active' if active == 'new' }}">Raise Ticket</a>
      <a href="/tickets" class="{{ 'active' if active == 'tickets' }}">View Tickets</a>
    </nav>
  </div>
</header>
<main>
  <div class="wrap">{{ content }}</div>
</main>
<footer>HelpDeskOps &middot; Flask + Git + Jenkins + Docker</footer>
</body>
</html>
"""


def page(body, active, **ctx):
    """Render the page body first (auto-escaped), then wrap it in the layout."""
    content = Markup(render_template_string(body, **ctx))
    return render_template_string(LAYOUT, content=content, active=active)


@app.route("/")
def home():
    open_count = sum(1 for t in TICKETS if t["status"] == "Open")
    resolved_count = len(TICKETS) - open_count
    return page("""
    <h2>Welcome</h2>
    <p class="intro">Report your IT problem here and track it until it is resolved.</p>
    <div class="stats">
      <div class="stat open"><div class="num">{{ open_count }}</div><div class="lbl">Open tickets</div></div>
      <div class="stat done"><div class="num">{{ resolved_count }}</div><div class="lbl">Resolved tickets</div></div>
      <div class="stat"><div class="num">{{ total }}</div><div class="lbl">Total tickets</div></div>
    </div>
    <div class="card">
      <h2 style="font-size:20px">What do you need?</h2>
      <div class="actions">
        <a class="btn" href="/new">+ Raise a Ticket</a>
        <a class="btn" style="background:#374151" href="/tickets">View All Tickets</a>
      </div>
    </div>
    """, "home", open_count=open_count, resolved_count=resolved_count, total=len(TICKETS))


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
    return page("""
    <h2>Raise a Ticket</h2>
    <div class="card form-card">
      <form method="post">
        <label for="name">Your name</label>
        <input id="name" name="name" placeholder="e.g. Asha Rao" required>

        <label for="category">Category</label>
        <select id="category" name="category">
          {% for c in cats %}<option>{{ c }}</option>{% endfor %}
        </select>

        <label for="description">Describe the problem</label>
        <textarea id="description" name="description" rows="5" placeholder="e.g. Hostel Wi-Fi is not connecting" required></textarea>

        <button class="btn" type="submit">Submit Ticket</button>
      </form>
    </div>
    """, "new", cats=CATEGORIES)


@app.route("/tickets")
def tickets():
    return page("""
    <h2>All Tickets</h2>
    <div class="card">
      {% if tickets %}
      <div class="table-wrap">
        <table>
          <tr><th>ID</th><th>Name</th><th>Category</th><th>Problem</th><th>Status</th><th>Action</th></tr>
          {% for t in tickets %}
          <tr>
            <td>#{{ t.id }}</td>
            <td>{{ t.name }}</td>
            <td><span class="badge cat">{{ t.category }}</span></td>
            <td>{{ t.description }}</td>
            <td><span class="badge {{ t.status | lower }}">{{ t.status }}</span></td>
            <td>
              {% if t.status == "Open" %}
              <form class="inline" method="post" action="/resolve/{{ t.id }}">
                <button class="btn small">Mark Resolved</button>
              </form>
              {% else %}&#10003;{% endif %}
            </td>
          </tr>
          {% endfor %}
        </table>
      </div>
      {% else %}
      <div class="empty">
        <div class="icon">&#128237;</div>
        <p>No tickets yet.</p>
        <a class="btn" href="/new">Raise the first ticket</a>
      </div>
      {% endif %}
    </div>
    """, "tickets", tickets=TICKETS)


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