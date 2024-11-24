from flask import Flask, render_template, request, redirect, send_file, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(50), unique=True, nullable=False)
    item_type = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Available')
    next_cleaning = db.Column(db.Date, nullable=True)
    rental_count = db.Column(db.Integer, default=0)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    item_id = db.Column(db.String(50), db.ForeignKey('item.item_id'), nullable=False)
    rental_date = db.Column(db.Date, default=datetime.utcnow)
    return_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Active')

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
@app.route('/dashboard')
def dashboard():
    total_revenue = sum([rental.price for rental in Rental.query.all()])
    active_rentals = Rental.query.filter_by(status='Active').all()
    available_items = Item.query.filter_by(status='Available').all()
    return render_template(
        'dashboard.html',
        total_revenue=total_revenue,
        active_rentals=active_rentals,
        available_items=available_items
    )

@app.route('/inventory')
def inventory():
    items = Item.query.all()
    return render_template('inventory.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        new_item = Item(
            item_id=request.form['item_id'],
            item_type=request.form['item_type'],
            condition=request.form['condition'],
            status=request.form['status'],
            next_cleaning=datetime.strptime(request.form['next_cleaning'], '%Y-%m-%d'),
            rental_count=int(request.form['rental_count'])
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('inventory'))
    return render_template('add_item.html')

@app.route('/new_rental', methods=['GET', 'POST'])
def new_rental():
    items = Item.query.filter_by(status='Available').all()
    if request.method == 'POST':
        new_rental = Rental(
            customer_name=request.form['customer_name'],
            item_id=request.form['item_id'],
            rental_date=datetime.strptime(request.form['rental_date'], '%Y-%m-%d'),
            return_date=datetime.strptime(request.form['return_date'], '%Y-%m-%d'),
            price=float(request.form['price'])
        )
        db.session.add(new_rental)
        # Update item status to 'Rented'
        item = Item.query.filter_by(item_id=new_rental.item_id).first()
        item.status = 'Rented'
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('new_rental.html', items=items)

@app.route('/manage_items', methods=['GET', 'POST'])
def manage_items():
    items = Item.query.all()
    if request.method == 'POST':
        action = request.form.get('action')
        item_id = request.form.get('item_id')
        if action == 'delete':
            item = Item.query.filter_by(item_id=item_id).first()
            db.session.delete(item)
            db.session.commit()
        elif action == 'update':
            item = Item.query.filter_by(item_id=item_id).first()
            item.status = request.form.get('status')
            db.session.commit()
        return redirect(url_for('manage_items'))
    return render_template('manage_items.html', items=items)

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')
@app.route('/get_calendar_events', methods=['GET'])
def get_calendar_events():
    events = [
        {
            "title": "Rented: 001 (Husen)",
            "start": "2024-11-19",
            "end": "2024-11-24",
            "color": "red"
        },
        {
            "title": "Rented: 002 (Husen)",
            "start": "2024-12-01",
            "end": "2024-12-05",
            "color": "blue"
        }
    ]
    return jsonify(events=events)

@app.route('/generate_invoice/<int:rental_id>')
def generate_invoice(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    item = Item.query.filter_by(item_id=rental.item_id).first()
    
    rendered = render_template('invoice.html', rental=rental, item=item)
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(rendered.encode('UTF-8')), dest=pdf)
    
    if pisa_status.err:
        return "Error generating invoice", 500
    
    pdf.seek(0)
    return send_file(pdf, as_attachment=True, download_name=f"invoice_{rental.id}.pdf")
if __name__ == '__main__':
    app.run(debug=True)
    