import os
import flask
from flask_sqlalchemy import SQLAlchemy
from db import db

import song_nodb as song_db
import app_api

app = flask.Flask(__name__, template_folder='../templates',static_folder='../static')
app.secret_key = os.urandom(64)
control = app_api.Control(flask.session)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

@app.route("/")
def index():
    return flask.render_template('index.html')

@app.route("/spotify_login")
def spotify_login():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    return flask.redirect(flask.url_for('options'))

@app.route("/callback")
def callback():
    control.spotify_access_token(flask.request.args['code'])
    return flask.redirect(flask.url_for('options'))

@app.route("/options", methods=['GET','POST'])
def options():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    return flask.render_template('options.html')

@app.route('/load_data')
def load_data():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    control.load_from_db()
    return flask.redirect('ranking_hub')

@app.route('/load_file')
def load_file():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    control.load_from_file()
    return flask.redirect('ranking_hub')

@app.route('/store_file')
def store_file():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    control.load_to_file()
    return flask.redirect('ranking_hub')

@app.route('/get_playlists')
def get_playlists():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    playlists = control.get_playlists()

    return flask.render_template('get_playlists.html',playlists=playlists)

@app.route('/get_songs', methods=['GET','POST'])
def get_songs():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    if 'playlist' in flask.request.form:
        playlist_id = flask.request.form['playlist']
        control.add_playlist_from_spotify(playlist_id)
        return flask.redirect('ranking_hub')
    else:
        return flask.redirect('get_playlists')

@app.route('/create_ranking')
def create_ranking():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    if control.can_create_ranking():
        libraries = control.get_library_names()
        return flask.render_template('create_ranking.html',playlist={}, libraries=libraries)
    else:
        return flask.redirect('ranking_hub')

@app.route('/initializer',methods=['GET','POST'])
def initializer():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    ranking_type = flask.request.form.get('rank_type')
    seed_type = flask.request.form.get('seed_type','manual')
    name = flask.request.form.get('list_name','default')
    desc = flask.request.form.get('description',f'list of {name}')
    library = flask.request.form['library']
    props = {property:float(flask.request.form[property]) for property in song_db.SONG_PROPERTIES}
    ranking = control.initialize_ranking(ranking_type, seed_type, library, name, desc, props)
    control.set_current_ranking(ranking.id)
    return flask.redirect('ranking_results')

@app.route('/active_ranking', methods=["GET","POST"])
def selecter():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    list_name = control.get_ranking_name()
    song1_info, song2_info, expected_outcome = control.get_info_2items()
    return flask.render_template('active_ranking.html',list_name=list_name, song1_info=song1_info, song2_info=song2_info, expected_outcome=expected_outcome)

@app.route('/ranking_answer', methods=["GET","POST"])
def answer():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    result = float(flask.request.form.get('selection'))
    control.add_rank_result(result)
    return flask.redirect('active_ranking')
    
@app.route('/change_ranking', methods=['GET','POST'])
def change_ranking():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    data = flask.request.get_json()
    control.set_current_ranking(data['id'])
    return flask.redirect('ranking_results')

@app.route('/update_ranking', methods=['GET','POST'])
def update_ranking():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    data = flask.request.get_json()
    control.add_song_result(data['id'],data['amount'])
    return flask.redirect('ranking_results')

@app.route('/ranking_results', methods=['GET','POST'])
def rankings():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    if flask.request.method == 'POST':
        control.set_current_ranking(flask.request.form.get('ranking'))
    
    headers = control.user.get_headers()
    items = control.get_ranking_items()
    ranking_name = control.get_ranking_name()
    ranking_desc = control.get_ranking_desc()
    return flask.render_template('ranking_results.html', headers=headers, items=items, ranking_name=ranking_name, ranking_desc=ranking_desc)

@app.route('/ranking_hub')
def rank_hub():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    rankings = control.get_rankings_info()
    libraries = control.get_libraries_info()
    return flask.render_template('ranking_hub.html',num_libraries=len(libraries),libraries=libraries,rankings=rankings,num_rankings=len(rankings))

@app.route('/update_table_sort', methods=['GET','POST'])
def table_sort():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    data = flask.request.get_json()
    control.set_table_sort(data['table'],data['sort'])
    return flask.redirect('ranking_hub')

@app.route('/logout')
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('home'))

def main():
    app.run(host='0.0.0.0', debug=True)

if __name__=="__main__":
    main()