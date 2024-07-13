# File: app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///family_tree.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

class FamilyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    suffix = db.Column(db.String(10))
    birth_date = db.Column(db.String(50))
    parent_id = db.Column(db.Integer, db.ForeignKey('family_member.id'), nullable=True)
    spouse = db.Column(db.String(100))
    wedding_anniversary = db.Column(db.String(50))
    bio = db.Column(db.Text)
    favorite_memories = db.Column(db.Text)
    image_file = db.Column(db.String(100))

    parent = db.relationship('FamilyMember', remote_side=[id], backref='children')

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'suffix': self.suffix,
            'birth_date': self.birth_date,
            'parent_id': self.parent_id,
            'spouse': self.spouse,
            'wedding_anniversary': self.wedding_anniversary,
            'bio': self.bio,
            'favorite_memories': self.favorite_memories,
            'image_file': self.image_file,
            'parent': self.parent.to_dict() if self.parent else None
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view')
def view_family_tree():
    return render_template('view_family_tree.html')

@app.route('/add', methods=['GET', 'POST'])
def add_family_member():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            middle_name = request.form['middle_name']
            last_name = request.form['last_name']
            suffix = request.form['suffix']
            birth_date = request.form['birth_date']
            parent_id = request.form['parent_id']
            spouse = request.form['spouse']
            wedding_anniversary = request.form['wedding_anniversary']
            bio = request.form['bio']
            favorite_memories = request.form['favorite_memories']
            image_file = request.files['image_file']

            if image_file:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
                image_file.save(image_path)
            else:
                image_path = None

            new_member = FamilyMember(
                first_name=first_name, middle_name=middle_name, last_name=last_name,
                suffix=suffix, birth_date=birth_date, parent_id=parent_id,
                spouse=spouse, wedding_anniversary=wedding_anniversary,
                bio=bio, favorite_memories=favorite_memories, image_file=image_path
            )

            db.session.add(new_member)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            return f"An error occurred: {e}"
    
    members = FamilyMember.query.all()
    return render_template('add_family_member.html', members=members)

@app.route('/edit', methods=['GET', 'POST'])
def edit_family_member():
    if request.method == 'POST':
        if 'member_id' in request.form:
            member_id = request.form['member_id']
            member = FamilyMember.query.get(member_id)
            
            members = FamilyMember.query.order_by(FamilyMember.last_name).all()
            return render_template('edit_family_member.html', members=members, member=member)
        else:
            try:
                member_id = request.form['member_id_hidden']
                member = FamilyMember.query.get(member_id)

                member.first_name = request.form['first_name']
                member.middle_name = request.form['middle_name']
                member.last_name = request.form['last_name']
                member.suffix = request.form['suffix']
                member.birth_date = request.form['birth_date']
                member.parent_id = request.form['parent_id'] if request.form['parent_id'] else None
                member.spouse = request.form['spouse']
                member.wedding_anniversary = request.form['wedding_anniversary']
                member.bio = request.form['bio']
                member.favorite_memories = request.form['favorite_memories']
                image_file = request.files['image_file']

                if image_file:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
                    image_file.save(image_path)
                    member.image_file = image_path

                db.session.commit()
                return redirect(url_for('index'))
            except Exception as e:
                return f"An error occurred: {e}"

    members = FamilyMember.query.order_by(FamilyMember.last_name).all()
    return render_template('edit_family_member.html', members=members)

@app.route('/display')
def display_family_members():
    members = FamilyMember.query.all()
    return render_template('display_family_members.html', members=members)

@app.route('/api/members', methods=['GET'])
def get_members():
    try:
        members = FamilyMember.query.all()
        return jsonify([member.to_dict() for member in members])
    except Exception as e:
        print(f"API Error: {e}")  # Debugging information
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)