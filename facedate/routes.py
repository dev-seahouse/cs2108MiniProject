import os
from flask import Flask, request, redirect, flash, render_template, url_for,send_from_directory
from app import app, db
from models import Profile
from process import get_matched_results
from werkzeug.utils import secure_filename

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile_pic/<path:filename>')
def display_profile(filename):
    return send_from_directory(app.config['PROFILE_PIC_LOCATION'], filename, as_attachment=False)

@app.route('/create', methods=["GET", "POST"])
def create_profile():
    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        # create new record
        name = request.form.get('name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        description = request.form.get('description')
        age = request.form.get('age')
        file = request.files['file']

        # create a new profile object
        new_profile = Profile(name = name, gender = gender, age = age, email = email, description=description)
        db.session.add(new_profile)
        # try to insert if failed ignore the rest
        insert_sucess = True
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            insert_sucess = False

        if insert_sucess == True:
            # get last inserted ld
            user_id = new_profile.id
            # save file
            filename = str(user_id) + ".jpg"
            profile_folder_name = "males" if gender == "M" else "females"
            save_path = os.path.join(app.config['PROFILE_PIC_LOCATION'], profile_folder_name, filename)
            file.save(save_path)
            flash("Profile created successfully.")
            return redirect("index")

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        target = app.config['UPLOAD_FOLDER']
        if  not os.path.isdir(target):
            os.mkdir(target)

        if 'file' not in request.files:
            flash('No file choosen')
            return redirect(request.url)

        file = request.files['file'] 

        if file.filename == '':
            flash('No file choosen')
            return redirect(request.url)

        if (file):
            filename = secure_filename('temp.jpg')
            destination = "/".join([app.config['UPLOAD_FOLDER'], filename])
            file.save(destination)

        gender = request.form.get('gender')
        description = request.form.get('description')
        # run matching and return matched results
        matched_profile_ids = get_matched_results(gender, description)
        
        print(matched_profile_ids)

        # display results

        # for each id in matched id, get the profile object from db by id
        matched_profiles = [ Profile.query.get(id) for id in matched_profile_ids]


        profile_folder_name = "males" if gender == "M" else "females"

        return render_template (
         'show.html',
          profiles      = matched_profiles,
          pic_folder    = profile_folder_name
        )