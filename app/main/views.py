from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash,request,current_app,make_response
from . import main
from .forms import PostForm,EditProfileForm,EditProfileAdminForm,CommentForm
from .. import db
from ..models import Role, User, Post, Comment,Permission
from ..decorators import admin_required, permission_required
from flask_login import login_required,current_user



@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
       form.validate_on_submit():
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash('You have submit the post')
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['AS_POSTS_PER_PAGE'],error_out=False)
    posts = pagination.items
    return render_template('index.html',form=form,posts=posts,
                show_followed=show_followed,pagination=pagination,current_time=datetime.utcnow())

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return "For administrators!"

@main.route('/user_profile/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, 
        per_page=current_app.config['AS_POSTS_PER_PAGE'],error_out=False)
    posts = pagination.items
    return render_template('user_profile.html',user=user,posts=posts,pagination=pagination)

@main.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.name.data :
            current_user.name = form.name.data
        if form.location.data :
            current_user.location = form.location.data
        if form.about_me.data :
            current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile have been updated')
        return redirect(url_for('main.user_profile',username=current_user.username))
    return render_template('edit_profile.html',form=form)

@main.route('/edit_profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        if form.email.data :
            user.email = form.email.data
        if form.username.data :
            user.username = form.username.data
        if form.confirmed.data :
            user.confirmed = form.confirmed.data
        if form.role.data :
            user.role = Role.query.get(form.role.data)
        if form.name.data :
            user.name = form.name.data
        if form.email.data :
            user.email = form.email.data
        if form.location.data :
            user.location = form.location.data
        if form.about_me.data :
            user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('You have been updated the user profile')
        return redirect(url_for('main.user_profile',username=user.username))
    return render_template('edit_profile_admin.html',form=form,user=user)

@main.route('/posts/<int:id>',methods=['GET','POST'])
def post(id):
    form = CommentForm()
    post = Post.query.get_or_404(id)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,post=post,
                    author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published')
        return redirect(url_for('main.post',id=post.id,page=-1)+'#comments')
    page = request.args.get('page',1,type=int)
    if page == -1 :
        page = (post.comments.count()-1)/current_app.config['AS_COMMENTS_PER_PAGE'] +1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['AS_COMMENTS_PER_PAGE'],
            error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                comments=comments, pagination=pagination)

@main.route('/edit_post/<int:id>',methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if current_user != post.author and \
      not current_user.can(Permission.ADMINISTER):
        abort(403)
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('You have been update the post')
        return redirect(url_for('main.post',id=id))
    form.body.data = post.body
    return render_template('edit_post.html',form=form)
    
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('You have followed %s' %username)
        return redirect(url_for('main.user_profile',username=username))
    current_user.follow(user)
    flash('You are now following %s' %username)
    return redirect(url_for('main.user_profile',username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('You have not followed %s' %username)
        return redirect(url_for('main.user_profile',username=username)) 
    current_user.unfollow(user)
    flash('You are not following %s' %username)
    return redirect(url_for('main.user_profile',username=username))

@main.route('/followers/<username>')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(page,
        per_page=current_app.config['AS_FOLLOWERS_PER_PAGE'],error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title="Followers of",endpoint='main.followers',
                            pagination=pagination,follows=follows)

@main.route('/followed_by/<username>')
@login_required
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(page,
        per_page=current_app.config['AS_FOLLOWERS_PER_PAGE'],error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='main.followed_by', pagination=pagination,
                           follows=follows)

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['AS_MODERATE_COMMENTS_PER_PAGE'],error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                            pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    if not comment.disabled:
        flash('This comment is already enabled')
        return redirect(url_for('main.moderate'))
    else:
        comment.disabled = False
        db.session.add(comment)
        db.session.commit()
        flash('This comment has been disabled')
        return redirect(url_for('main.moderate',page=request.args.get('page', 1, type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    if comment.disabled:
        flash('This comment is already disabled')
        return redirect(url_for('main.moderate',page=request.args.get('page', 1, type=int)))
    else:
        comment.disabled = True
        db.session.add(comment)
        db.session.commit()
        flash('This comment has been disabled')
        return redirect(url_for('main.moderate',page=request.args.get('page', 1, type=int)))

