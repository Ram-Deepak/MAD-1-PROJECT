import os
from flask import current_app as app # importing the initialized app from main.py
from flask import Flask, request, render_template, redirect, url_for, abort
from application.models import *
from flask_login import login_required, LoginManager, logout_user, login_user, current_user
from application.forms import *
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
# from PIL import Image

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# function that converts image to blob
def photoToBlob(photo):
    blob = None 
    with open(photo, 'rb') as file:
        blob = file.read()
    return blob

# function that converts blob to image format
def blobToPhoto(blob, filename):
    with open(filename, 'wb') as file:
        file.write(blob)

# loads the user during login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# first page to be displayed 
@app.route('/', methods=['GET'])
def home(): # directs to the main page
    if request.method=='GET':
        return render_template('index.html')

# function for login page
@app.route('/login', methods=['GET', 'POST'])
def login(): # login page
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect('/profile/'+user.username)
        else:
            abort(404)
    return render_template('login.html', form=form)

# function for registering a new user
@app.route('/register', methods=['GET', 'POST'])
def register(): # register page
    form  = RegisterForm()
    if form.validate_on_submit():
        fname = form.first_name.data
        lname = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = bcrypt.generate_password_hash(form.password.data)
        user_record = User(fname=fname.lower(), lname=lname.lower(), email=email,
                            username=username, password=password)   
        db.session.add(user_record)
        db.session.flush()
        profile_record = Profile(user_id=user_record.id, post_count=0, 
                                followers_count=0, following_count=0,
                                photo=photoToBlob('default-image.jpg'))
        db.session.add(profile_record)
        db.session.flush()
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# function for logout
@app.route('/logout')
@login_required  # @login_required -> tells that this route can be accessed only if the user is logged in
def logout():
    logout_user()
    return redirect(url_for('login'))

# to display the profile page of the user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    profile = Profile.query.filter_by(user_id = current_user.id).first()
    blobToPhoto(profile.photo, '/home/ram/Desktop/IIT-M/PROJECT/21f2001114/MAD-1-PROJECT/static/images/img.jpeg')
    # iml = Image.open('/home/ram/Desktop/IIT-M/PROJECT/21f2001114/MAD-1-PROJECT/static/images/img.jpeg')
    if profile.posts==0:
        return render_template('profile.html', profile=profile)
    else:
        posts = Posts.query.filter_by(user_id=current_user.id).order_by(Posts.created.desc()).all()
        return render_template('profile.html', profile=profile, posts=posts)

# route for searching names and displaying their usernames
@app.route('/<username>/search', methods=['GET', 'POST'])
@login_required
def search(username):
    if request.method=='GET':
        return render_template('search.html')
    if request.method=='POST':
        name = request.form['name'].split(' ')
        fname, lname = '', ''
        if len(name)==1:
            fname = name[0]
        if len(name)==2:
            lname = name[1]
        accounts = User.query.filter(User.firstname.like('%'+fname+'%') & User.lastname.like('%'+lname+'%')).all()
        return render_template('search.html', accounts=accounts)

# to view the profiile page of other users
@app.route('/<username>/view/<account_username>', methods=['GET'])
@login_required
def view(username, account_username):
    if(account_username==username):
        return redirect('/profile/'+username)
    acc = User.query.filter_by(username=account_username).first()
    profile = Profile.query.filter_by(user_id = acc.id).first()
    blobToPhoto(profile.photo, '/home/ram/Desktop/IIT-M/PROJECT/21f2001114/MAD-1-PROJECT/static/images/img.jpeg')
    follow = Following.query.filter((Following.user_id==current_user.id) & (Following.following_id==acc.id)).first()
    posts = Posts.query.filter_by(user_id=acc.id).order_by(Posts.created.desc()).all()
    if follow:
        return render_template('view.html',
                                account_username=account_username, following=True, profile=profile, posts=posts)
    
    followed = Followers.query.filter(Followers.user_id==current_user.id, Followers.follower_id==acc.id).first()
    if followed:
        return render_template('view.html',
                                account_username=account_username, follow_back=True, profile=profile, posts=posts)
    
    return render_template('view.html', 
                            account_username=account_username, not_following=True, profile=profile, posts=posts)

# to follow a user
@app.route('/<username>/follow/<account_username>', methods=['GET'])
@login_required
def follow_someone(username, account_username):
    follow_account = User.query.filter_by(username=account_username).first()
    new_following = Following(user_id=current_user.id, following_id=follow_account.id)
    db.session.add(new_following)
    db.session.flush()
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()
    user_profile.following = user_profile.following+1
    db.session.flush()
    db.session.commit()
    # return redirect('/profile/'+username)
    return redirect('/'+username+'/view/'+account_username)

# to unfollow a user
@app.route('/<username>/unfollow/<account_username>', methods=['GET'])
@login_required
def unfollow(username, account_username):
    follow_account = User.query.filter_by(username=account_username).first()
    db.session.query(Following).filter((Following.user_id==current_user.id) & (Following.following_id==follow_account.id)).delete()
    db.session.flush()
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()
    user_profile.following = user_profile.following-1
    db.session.flush()
    db.session.commit()
    return redirect('/'+username+'/view/'+account_username)

# function to fetch the list of followers from the database
def list_of_followers(username, user):
    followers_list = Followers.query.filter_by(user_id=user.id).all()
    lst=[]
    for user in followers_list:
        record = User.query.filter_by(id=user.follower_id).first()
        lst.append(record)
    return lst

# funtion to fetch the list of following users from the database
def list_of_following(username, user):
    following_list = Following.query.filter_by(user_id=user.id).all()
    lst=[]
    for user in following_list:
        record = User.query.filter_by(id=user.following_id).first()
        lst.append(record)
    return lst

# to dispaly followers
@app.route('/profile/<username>/followers', methods=['GET'])
@login_required
def followers(username):
    lst = list_of_followers(username, current_user)
    return render_template('followers.html', followers_list=lst)

# to display users that follow you
@app.route('/profile/<username>/following', methods=['GET'])
@login_required
def following(username):
    lst = list_of_following(username,current_user)
    return render_template('following.html', following_list=lst)

# to view the followers of other users
@app.route('/<username>/view/<account_username>/followers', methods=['GET'])
@login_required
def followers_of_another_user(username, account_username):
    acc = User.query.filter_by(username=account_username).first()
    follower_list = list_of_followers(account_username, acc)
    return render_template('secondary_followers.html', followers_list=follower_list)

# to view the users that follow a particular user
@app.route('/<username>/view/<account_username>/following', methods=['GET'])
@login_required
def following_of_another_user(username, account_username):
    acc = User.query.filter_by(username=account_username).first()
    following_list = list_of_following(account_username, acc)
    return render_template('secondary_following.html', following_list=following_list)

# to update the profile image
@app.route('/<username>/update_image', methods=['POST'])
@login_required
def update_image(username):
    if request.method=='POST':
        profile = Profile.query.filter_by(user_id=current_user.id).first()
        photo = request.files['image']
        filename = photo.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(path)
        profile.photo = photoToBlob(path)
        db.session.commit()
        os.remove(path)
        return redirect('/profile/'+username)

# to create a post
@app.route('/create_post/<username>', methods=['GET','POST'])
@login_required
def create_post(username):
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        photo = form.photo.data
        filename = secure_filename(photo.filename) # secures the filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(path) # saves the photo in the mentioned path
        try:
            post = Posts(user_id=current_user.id,title=title,description=description,image=photoToBlob(path))
            db.session.add(post)
            db.session.commit()
        except:
            abort(500)
        os.remove(path) # deletes the item present in that path
        return redirect(url_for('profile', username=current_user.username))
    return render_template('createpost.html', form=form, name=current_user.firstname.capitalize(), username=username)

# to display the post
@app.route('/<username>/showpost/<int:post_id>', methods=['GET'])
@login_required
def show_own_post(username, post_id):
    post = Posts.query.get(post_id)
    blobToPhoto(post.image,'/home/ram/Desktop/IIT-M/PROJECT/21f2001114/MAD-1-PROJECT/static/images/post.jpeg')
    return render_template('own_post_view.html', post=post)

# to delete your post
@app.route('/<username>/delete_own_post/<int:post_id>', methods=['GET'])
@login_required
def delete_own_post(username, post_id):
    db.session.query(Posts).filter(Posts.id==post_id).delete()
    db.session.commit()
    return redirect(url_for('profile', username=username))

# to update information in your post
def update_post(post_info, form):
    change = False
    if form.title.data!=post_info.title:
        post_info.title = form.title.data
        change = True 
    if form.description.data!=post_info.description:
        post_info.description = form.description.data
        change = True 
    photo = form.photo.data
    if photo.filename!='':
        filename = secure_filename(photo.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(path)
        post_info.image = photoToBlob(path)
        change = True 
        os.remove(path)
    if change:
        db.session.commit()

# existing post data
def assign_post(post_info, form):
    form.title.data = post_info.title
    form.description.data = post_info.description
    form.photo.data = None 

# to update your post
@app.route('/<username>/update_own_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def update_own_post(username, post_id):
    post_info = Posts.query.get(post_id)
    form = UpdatePostForm()
    if form.validate_on_submit():
        update_post(post_info, form)
        return redirect(url_for('show_own_post', username=username, post_id=post_id))
    assign_post(post_info, form)
    return render_template('update_post.html', form=form, post_id=post_id)

# to display the feed page of the user
@app.route('/<username>/feed', methods=['GET'])
@login_required
def feed(username):
    following = Following.query.filter_by(user_id=current_user.id).add_columns(Following.following_id).all()
    following_list = set()
    for f in following:
        following_list.add(f[1])
    posts = Posts.query.filter(Posts.user_id.in_(following_list)).join(User).add_columns(Posts.id,Posts.user_id,User.username,Posts.title,Posts.description,Posts.created).filter(Posts.user_id==User.id).order_by(Posts.created.desc()).all()
    return render_template('feed.html', posts=posts)

# to display the post of a user
@app.route('/<username>/showpost/<follower_username>/<int:post_id>', methods=['GET'])
@login_required 
def show_follower_post(username,follower_username,post_id):
    post = Posts.query.get(post_id)
    blobToPhoto(post.image,'/home/ram/Desktop/IIT-M/PROJECT/21f2001114/MAD-1-PROJECT/static/images/post.jpeg')
    return render_template('follower_post_view.html', post=post, username=follower_username)

# function to update the user info
def update_user(user, form):
    user.firstname = form.first_name.data
    user.lastname = form.last_name.data
    db.session.commit()

# assigning existing user information to the form as default values
def assign_user(user, form):
    form.first_name.data = user.firstname 
    form.last_name.data = user.lastname

# to update the user account
@app.route('/update_account', methods=['GET','POST'])
@login_required 
def update_info():
    form = UpdateInfoForm()
    user = User.query.filter_by(username=current_user.username).first()
    if form.validate_on_submit():
        print('hello')
        # user.lastname = 'sivaganesan'
        update_user(user, form)
        return redirect(url_for('profile', username=current_user.username))
    assign_user(user, form)
    return render_template('update_info.html', form=form)

# to delete an account
@app.route('/delete_account', methods=['GET'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    db.session.query(Following).filter(Following.user_id==current_user.id).delete()
    followers = Followers.query.filter_by(user_id=current_user.id).all()
    for follower in followers:
        profile = Profile.query.filter_by(user_id=follower.follower_id).first()
        profile.following = profile.following - 1
    db.session.flush()
    db.session.query(Following).filter(Following.following_id==current_user.id).delete()
    db.session.query(Profile).filter(Profile.user_id==current_user.id).delete()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('login'))