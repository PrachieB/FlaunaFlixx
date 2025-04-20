import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
import io
import pickle
import warnings
warnings.filterwarnings('ignore')

user_entries_file_path = "/Users/bstar/Desktop/Biodata/flask_app/user_entries.csv"

raw = pd.read_csv("/Users/bstar/Desktop/Biodata/flask_app/data.csv")

invasive = pd.read_csv("/Users/bstar/Desktop/Biodata/flask_app/invasive.csv")

raw.fillna(0, inplace=True)

df = pd.DataFrame(raw, columns=['SpeciesName', 'ScientificName', 'Location'])

df = df.drop_duplicates(keep='first')

def predict_location(species_name):

    return df.loc[(df['SpeciesName'] == species_name), 'Location']


invasive.fillna(0, inplace=True)

invasive_species = set(invasive['Species Name'])

invasive['Typical Range'] = invasive['Typical Range'].apply(lambda x: x.lower())
invasive['Species Name'] = invasive['Species Name'].apply(lambda x: x.lower())

def is_invasive(species_name, location):
    species_name = species_name.lower()
    location = location.lower()
    species_info = invasive[invasive['Species Name'] == species_name]

    if not species_info.empty:
        invasive_ranges = species_info.iloc[0]['Typical Range']
        invasive_states = [state.strip() for state in invasive_ranges.split(',')]
        if "across india" in invasive_ranges or location in invasive_states:
            return True
    return False




import joblib
from flask import Flask, request, jsonify, render_template
from pyngrok import ngrok


app = Flask(__name__)

def predict_location(species_name):
    df = pd.DataFrame(raw, columns=['SpeciesName', 'ScientificName', 'Location'])
    return df.loc[(df['SpeciesName'] == species_name), 'Location'].tolist()

def is_invasive(species_name, location):
    species_name = species_name.lower()
    location = location.lower()
    invasive.fillna(0, inplace=True)
    invasive['Typical Range'] = invasive['Typical Range'].apply(lambda x: x.lower())
    invasive['Species Name'] = invasive['Species Name'].apply(lambda x: x.lower())
    species_info = invasive[invasive['Species Name'] == species_name]

    if not species_info.empty:
        invasive_ranges = species_info.iloc[0]['Typical Range']
        invasive_states = [state.strip() for state in invasive_ranges.split(',')]
        if "across india" in invasive_ranges or location in invasive_states:
            return True
    return False

@app.route('/')
def home():
    return render_template('species.html')

@app.route('/location', methods=['POST'])
def location():
  species_name = request.form['species_name']
  locations = predict_location(species_name)
  return jsonify({'locations': locations})

@app.route('/invasive', methods=['POST'])
def invasive_check():
    species_name = request.form['species_name']
    location = request.form['location']
    result = is_invasive(species_name, location)
    return jsonify({'is_invasive': result})

@app.route('/add_entry', methods=['POST'])
def add_entry():
    species_name = request.form['species_name']
    scientific_name = request.form['scientific_name']
    location = request.form['location']
    
    # Add new entry to DataFrame
    new_entry = pd.DataFrame({
        'SpeciesName': [species_name],
        'ScientificName': [scientific_name],
        'Location': [location]
    })
    
   
    
    # Append to CSV file
    with open(user_entries_file_path, 'a') as f:
        new_entry.to_csv(f, header=f.tell()==0, index=False)
    
    return jsonify({'message': 'Entry added successfully'})

if __name__ == '__main__':
    app.run(debug=True)
