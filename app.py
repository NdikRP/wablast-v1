import time
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd
import pywhatkit as pwk
import pyautogui

UPLOAD_FOLDER = os.path.join('uploads')

app = Flask(__name__)
# Mengganti Secret Key
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  


# Mendefinisikan form
class BulkWhatsAppForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    image = FileField('Image')
    submit = SubmitField('Send')


# Route
@app.route('/', methods=['GET', 'POST'])
def home():
    form = BulkWhatsAppForm()
    if form.validate_on_submit():
        # Process the form data and send messages
        return redirect(url_for('send'))

    return render_template('index.html', form=form)


# Sending message route
@app.route('/send', methods=['GET', 'POST'])
def send():
    # Get the form data
    csv_file = request.files.get('csv_file')
    message = request.form.get('message')
    image = request.files.get('image')

    # Menyimpan file locally
    csv_filename = os.path.join(app.config['UPLOAD_FOLDER'], csv_file.filename)
    csv_file.save(csv_filename)

    if image:
        image_filename = os.path.join(
            app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_filename)
    else:
        image_filename = None

    # Membaca csv (panda)
    df = pd.read_csv(csv_filename)

    # Looping ke dalam file csv dan mengirim pesan
    for index, row in df.iterrows():
        name = row['name']
        phone_number = str(row['phone_number'])
        phone_number = '+' + phone_number
        # Menyiapkan template pesan awal
        final_message = f'Hi {name}, {message}'

        # Mengirim pesan (pywhatkit)
        if image_filename:
            pwk.sendwhats_image(phone_number, image_filename, final_message,
                                wait_time=10)
        else:
            pwk.sendwhatmsg_instantly(phone_number, final_message)

        time.sleep(10)

        # Menutup web WA (pythongui)
        pyautogui.hotkey('ctrl', 'w')

        time.sleep(5)

    return "Messages sent successfully!"


if __name__ == '__main__':
    app.run(debug=True)
