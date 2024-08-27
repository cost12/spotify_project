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
    info = control.sp.current_user()
    control.create_profile(info['id'],info['display_name'])
    return flask.redirect(flask.url_for('options',user_id=info['id']))

@app.route("/<user_id>/options", methods=['GET','POST'])
def options(user_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    return flask.render_template('options.html', user_id=user_id)

@app.route('/<user_id>/load_data')
def load_data(user_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    control.load_from_db(user_id)
    return flask.redirect(flask.url_for('ranking_hub',user_id=user_id))

@app.route('/<user_id>/load_file')
def load_file(user_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    control.load_from_file(user_id)
    return flask.redirect(flask.url_for('ranking_hub',user_id=user_id))

@app.route('/<user_id>/store_file')
def store_file(user_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    control.load_to_file(user_id)
    return flask.redirect(flask.url_for('ranking_hub',user_id=user_id))

@app.route('/<user_id>/get_playlists')
def get_playlists(user_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    playlists = control.get_playlists(user_id)

    return flask.render_template('get_playlists.html',playlists=playlists,user_id=user_id)

@app.route('/<user_id>/get_songs', methods=['GET','POST'])
def get_songs(user_id):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    if 'playlist' in flask.request.form:
        playlist_id = flask.request.form['playlist']
        control.add_playlist_from_spotify(user_id, playlist_id)
        return flask.redirect(flask.url_for('ranking_hub',user_id=user_id))
    else:
        return flask.redirect(flask.url_for('get_playlists',user_id=user_id))

@app.route('/<user_id>/create_ranking')
def create_ranking(user_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    if control.can_create_ranking(user_id):
        libraries = control.get_library_names(user_id)
        return flask.render_template('create_ranking.html', user_id=user_id, playlist={}, libraries=libraries)
    else:
        return flask.redirect(flask.url_for('ranking_hub', user_id=user_id))

@app.route('/<user_id>/initializer',methods=['GET','POST'])
def initializer(user_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    ranking_type = flask.request.form.get('rank_type')
    seed_type = flask.request.form.get('seed_type','manual')
    name = flask.request.form.get('list_name','default')
    desc = flask.request.form.get('description',f'list of {name}')
    library = flask.request.form['library']
    props = {property:float(flask.request.form[property]) for property in song_db.SONG_PROPERTIES}
    ranking = control.initialize_ranking(user_id, ranking_type, seed_type, library, name, desc, props)
    return flask.redirect(flask.url_for('ranking_results', user_id=user_id, ranking_id=ranking.id))

@app.route('/<user_id>/active_ranking/<ranking_id>', methods=["GET","POST"])
def active_ranking0(user_id:str, ranking_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    item1, item2 = control.get_two_items(user_id,ranking_id)
    return flask.redirect(flask.url_for('active_ranking1',user_id=user_id,ranking_id=ranking_id,item1_id=item1.id,item2_id=item2.id))

@app.route('/<user_id>/active_ranking/<ranking_id>/<item1_id>/<item2_id>', methods=["GET","POST"])
def active_ranking1(user_id:str, ranking_id:str, item1_id:str, item2_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    list_name = control.get_ranking_name(user_id, ranking_id)
    item1_info = control.get_item_info(user_id, ranking_id, control.id_to_item(item1_id))
    item2_info = control.get_item_info(user_id, ranking_id, control.id_to_item(item2_id))
    expected_outcome = control.get_expected_outcome(user_id, ranking_id, item1_id,item2_id)
    return flask.render_template('active_ranking.html',user_id=user_id,ranking_id=ranking_id,list_name=list_name, item1_info=item1_info, item2_info=item2_info, expected_outcome=expected_outcome)

@app.route('/<user_id>/ranking_answer/<ranking_id>/<item1_id>/<item2_id>', methods=["GET","POST"])
def ranking_answer(user_id:str, ranking_id:str, item1_id:str, item2_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    result = float(flask.request.form.get('selection'))
    control.add_rank_result(user_id, ranking_id, item1_id, item2_id, result)
    return flask.redirect(flask.url_for('active_ranking0',user_id=user_id,ranking_id=ranking_id))

@app.route('/update_ranking', methods=['GET','POST'])
def update_ranking():
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    data = flask.request.get_json()
    control.add_item_result(data['user_id'], data['ranking_id'], data['id'], data['amount'])
    return flask.redirect(flask.url_for('ranking_results',user_id=data['user_id'], ranking_id=data['ranking_id']))

@app.route('/<user_id>/ranking_results/<ranking_id>', methods=['GET','POST'])
def ranking_results(user_id:str, ranking_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    headers = control.users[user_id].get_headers()
    items = control.get_ranking_items(user_id, ranking_id)
    ranking_name = control.get_ranking_name(user_id,ranking_id)
    ranking_desc = control.get_ranking_desc(user_id,ranking_id)
    return flask.render_template('ranking_results.html', user_id=user_id, ranking_id=ranking_id, headers=headers, items=items, ranking_name=ranking_name, ranking_desc=ranking_desc)

@app.route('/<user_id>/ranking_hub')
def ranking_hub(user_id:str):
    valid, url = control.validate_session()
    if not valid:
        return flask.redirect(url)
    
    rankings = control.get_rankings_info(user_id)
    libraries = control.get_libraries_info(user_id)
    return flask.render_template('ranking_hub.html',user_id=user_id,num_libraries=len(libraries),libraries=libraries,rankings=rankings,num_rankings=len(rankings))

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