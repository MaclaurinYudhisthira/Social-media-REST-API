from flask import Blueprint, jsonify,request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager,jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from database import *

auth = Blueprint("auth", __name__)

# Routes
@auth.route("/", methods=["GET"])
def home():
    return jsonify({"message":"Hey! This is my API"}),200 # 200 OK

# Route for login and genrate jwt token
@auth.route("/authenticate", methods=["POST"])
def authenticate():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()
    print(user)
    if user:
        
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.user_id)
            access = create_access_token(identity=user.user_id)

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'email': user.email
                }

            }), 200 # 200 OK

    return jsonify({'error': 'Wrong credentials'}), 401 # 401 unathourized

# follow
@auth.route("/follow/<follower_id>", methods=["POST"])
@jwt_required()
def follow(follower_id):
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    
    if Follower.query.filter_by(follower_id=follower_id).first():
        return jsonify({'Message':'Already following'}), 409 # Conflict
    else: 
        follower=Follower(user_id,follower_id)
        db.session.add(follower)
        user.following+=1
        db.session.commit()
        return jsonify({'Message':'Started following'}), 201 # created

# unfollow
@auth.route("/unfollow/<follower_id>", methods=["POST"])
@jwt_required()
def unfollow(follower_id):
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    follower=Follower.query.filter_by(follower_id=follower_id).first()
    if follower:
        db.session.delete(follower)
        user.following-=1
        db.session.commit()
        return jsonify({'Message':'Unfollowed'}), 202 # Accepted
    else: 
        return jsonify({'Message':'Follower relationship dose not exist'}), 409 # Conflict

# user profile 
@auth.route("/user", methods=["GET"])
@jwt_required()
def user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    return jsonify({'Username':user.username,'followers':user.followers,'following':user.following}), 200 # OK

# create post
@auth.route("/posts", methods=["POST"])
@jwt_required()
def posts():
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    title = request.json.get("title", None)
    description = request.json.get("description", None)
    post=Post(user_id=user.user_id,title=title,description=description)
    db.session.add(post)
    db.session.commit()
    return jsonify({
        'post_id':post.post_id,
        'title':post.title,
        'description':post.description,
        'created_time':post.created_time
    }), 201 # Created

# delete posts
@auth.route("/posts/<post_id>", methods=["DELETE","GET"])
@jwt_required()
def get_delete_posts(post_id):
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    post=Post.query.filter_by(post_id=post_id,user_id=user.user_id).first()
    if request.method=="DELETE":
        if post:
            for like in Like.query.filter_by(post_id=post.post_id):
                db.session.delete(like)
            for comment in Comment.query.filter_by(post_id=post.post_id):
                db.session.delete(comment)
            db.session.commit()
            db.session.delete(post)
            db.session.commit()
            return jsonify({'Message':'Post deleted'}), 202 # Acc
        else:
            return jsonify({'Message':'Post either dose not exist or you are not creator of this post'}), 409 # Conflict
    if request.method=="GET":
        if post:
            return jsonify({
                'post_id':post.post_id,
                'title':post.title,
                'description':post.description,
                'created_time':post.created_time,
                'no_of_likes':post.likes,
                'no_ofcomments':post.comments
            }), 200 # OK
        else:
            return jsonify({'Message':'Post dose not exist'}), 409 # Conflict

# like
@auth.route("/like/<post_id>", methods=["POST"])
@jwt_required()
def like(post_id):
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    
    if Like.query.filter_by(post_id=post_id,user_id=user.user_id).first():
        return jsonify({'Message':'Already liked'}), 200 # OK
    else: 
        like=Like(user.user_id,post_id)
        db.session.add(like)
        post=Post.query.filter_by(post_id=post_id).first()
        post.likes+=1
        db.session.commit()
        return jsonify({'Message':'Post Liked'}), 201 # created

# unlike
@auth.route("/unlike/<post_id>", methods=["POST"])
@jwt_required()
def unlike(post_id=-1):
    if post_id==-1:
        return jsonify({'Message':'DDDose not exist'}), 409 # Conflict
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    like=Like.query.filter_by(post_id=post_id,user_id=user.user_id).first()
    if like:
        db.session.delete(like)
        post=Post.query.filter_by(post_id=post_id).first()
        post.likes-=1
        db.session.commit()
        return jsonify({'Message':'Post Unliked'}), 202 # Accepted
    else: 
        return jsonify({'Message':'like dose not exist'}), 409 # Conflict

# add comment
@auth.route("/comment/<post_id>", methods=["POST"])
@jwt_required()
def comment(post_id):
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    post=Post.query.filter_by(post_id=post_id).first()
    comment_text = request.json.get("comment", None)
    comment=Comment(user.user_id,post.post_id,comment_text)
    db.session.add(comment)
    post.comments+=1
    db.session.commit()
    return jsonify({
        'comment_id':comment.id,
    }), 201 # Created

# get all posts by authenticated user
@auth.route("/all_posts", methods=["GET"])
@jwt_required()
def all_posts():
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    posts = Post.query.filter_by(user_id=user_id).order_by("created_time").all()
    data=[]
    for post in posts:
        comments=Comment.query.filter_by(post_id=post.post_id).all()
        cs=[]
        if comments:
            for comment in comments:
                cs.append({
                    'user_id':comment.user_id,
                    'comment':comment.comment,
                })
        data.append({
            'post_id':post.post_id,
            'title':post.title,
            'description':post.description,
            'created_time':post.created_time,
            'comments':cs,
            'no_of_likes':post.likes,
        })
    return jsonify({"posts":data}),200 #OK

# Route to refresh token after 15  mins
@auth.route('/token/refresh', methods=["GET"])
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), 200 # OK

# Route to create data for testing
@auth.route("/tdata", methods=["GET"])
def tdata():
    password='123'
    pwd_hash = generate_password_hash(password)
    user = User(username='uname',email="test@app.com", password=pwd_hash)
    db.session.add(user)
    for i in range(10):
        user = User(username=f'uname{i}',email=f"test{i}@app.com", password=pwd_hash)
        db.session.add(user)
    for i in range(3):
        post=Post(user_id=1,title=f"title{i}",description=f"description{i}")
        db.session.add(post)
    db.session.commit()

    return jsonify({'message': "Test data created"}), 201 # 201 Created