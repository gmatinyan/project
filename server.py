import os
from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from flask import Flask, render_template, redirect, request, flash, session, url_for, send_from_directory

from werkzeug.utils import secure_filename

from sqlalchemy.sql import func


from model import User, Recipe, Rating, Favorite, Ingridient, RecipeIngridient, Tool, RecipeTool, Occasion, RecipeOccasion

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif', 'jfif'])

# Required to use Flask sessions and the debug toolbar
app.secret_key = "goga"


# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
	"""Homepage."""

	recipes = Recipe.query.all()
	# make a second query for occasions
	
	return render_template("homepage.html", recipes=recipes, enumerate=enumerate)

@app.route('/search')
def search_cake():
	"""Searching cakes based on form input."""

	#taking the form input and assigning it to variable search
	search = request.args.get('search')
	#querying th db
	occasions = Occasion.query.filter(Occasion.oname.like('%' + search + '%')).all()
	recipe_names = Recipe.query.filter(Recipe.rname.like('%' + search + '%')).all()

	search_results = []

	for occasion in occasions:
		search_results.extend(occasion.recipes)

	search_results += recipe_names

	search_results = set(search_results)


	return render_template('search.html', search_results=search_results)


@app.route('/login', methods=['GET'])
def log_in_form():
	"""Logging users in by email & password"""

	return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_process():
	"""Process login."""

	email = request.form.get('email')
	password = request.form.get('password')

	user = User.query.filter_by(email=email).first()


	if user:
		if password == user.password:
			session['logged_in_user'] = user.user_id
			#flash("Logged in")
			return redirect("/user_profile/{}".format(user.user_id))
		elif password != user.password:
			#flash("Incorrect password.")
			return redirect('/login')
		else:
			#flash("Login failed")
			return redirect("/login")

	else:
		#flash("You are not yet registered")
		return redirect ("/register")



@app.route('/user_profile/<int:user_id>')
def user_info(user_id):
	"""Display user page."""

	if 'logged_in_user' in session:
		user = User.query.get(user_id)
		recipes = Recipe.query.all()
	
		return render_template("homepage.html", user=user, recipes=recipes, enumerate=enumerate)
	else:
		return redirect('/')



@app.route('/user_recipes')
def user_recipe():
	"""Showes all the recipes added by that user."""

	#query recipe tabel to get recipes by user.id

	user_id = session['logged_in_user']
	user_recipes = Recipe.query.filter_by(user_id=user_id).all()

	return render_template("user_recipes.html", user_recipes=user_recipes)


@app.route('/edit_recipe/<recipe_id>')
def show_user_recipe(recipe_id):
	"""Showes user the recipe that's added."""

	if "logged_in_user" in session:

		edit = Recipe.query.filter_by(recipe_id=recipe_id).first()
		edit_occasion = RecipeOccasion.query.filter_by(recipe_id=recipe_id).first()
		edit_ingridients = RecipeIngridient.query.filter_by(recipe_id=recipe_id).all()
		edit_tools = RecipeTool.query.filter_by(recipe_id=recipe_id).all()

		ingridient_names = {edit_ingridient.ingridient.iname for edit_ingridient in edit_ingridients}

		tool_names = {edit_tool.tool.tname for edit_tool in edit_tools}

		
		return render_template("edit_recipe.html", edit=edit, edit_occasion=edit_occasion.occasion, 
													   recipe_id=recipe_id, ingridient_names=ingridient_names, 
													   tool_names=tool_names, edit_ingridients=edit_ingridients, 
													   edit_tools=edit_tools)
	else:
		return redirect('/')

	

@app.route('/edit_recipe/<recipe_id>', methods=['POST'])
def edit_user_recipe(recipe_id):
	"""Gives users ability to edit recipe."""

	user_id = session['logged_in_user']

	recipe = Recipe.query.get(recipe_id)

	target = os.path.join(APP_ROOT, 'uploads/')

	print "target:", target
	print request.files.getlist('file')

	if request.files.getlist('file') != "":
		for upload in request.files.getlist('file'):
			filename = upload.filename
			print 'filename:', filename
			#Verifys if files are supported
			ext = os.path.splitext(filename)[1]
			#if ext in ALLOWED_EXTENSIONS:
				#flash('File extension supported.')
			#else:
				#flash('Upload a valid file.')
			destination = "".join([target, filename])
			upload.save(destination)
			print "destination:", destination
		recipe.img_url = destination.replace("/home/vagrant/src/project", "")

	form_title = request.form.get('title')

	if form_title != recipe.rname:
		recipe.rname = form_title

	form_occasion = request.form.get('occasion').lower()
	occasion = recipe.occasions[0]

	if form_occasion != occasion.oname:
		occasion.oname = form_occasion

	form_description = request.form.get('description')
	
	if form_description != recipe.style:
		recipe.style = form_description

	
	form_ingridients = request.form.getlist('ingridients')

	ingridient_ids = []

	for ingridient in form_ingridients:
		ingridient_id = Ingridient.query.filter_by(iname=ingridient).first().ingridient_id
		ingridient_ids.append(ingridient_id)
	
	recipeingridients = RecipeIngridient.query.filter_by(recipe_id=recipe_id).all()


	for recipeingredient_obj in recipeingridients:
		if  recipeingredient_obj.ingridient_id not in ingridient_ids:
			db.session.delete(recipeingredient_obj)

	recipeingridient_ids = []

	for recipeingridient in recipeingridients:
		recipeingridient_id = recipeingridient.ingridient_id
		recipeingridient_ids.append(recipeingridient_id)

	for ingridient_id in ingridient_ids:
		if ingridient_id not in recipeingridient_ids:
			new_recipe_ingridient = RecipeIngridient(recipe_id=recipe_id, ingridient_id=ingridient_id)
			db.session.add(new_recipe_ingridient)


	form_instructions = request.form.get('instructions')
	

	if form_instructions != recipe.instructions:
		recipe.instructions = form_instructions


	form_tools = request.form.getlist('tools')

	tool_ids = []

	for tool in form_tools:
		tool_id = Tool.query.filter_by(tname=tool).first().tool_id
		tool_ids.append(tool_id)

	recipetools = RecipeTool.query.filter_by(recipe_id=recipe_id).all()

	for recipetool_obj in recipetools:
		if recipetool_obj.tool_id not in tool_ids:
			db.session.delete(recipetool_obj)

	recipetool_ids = []

	for recipetool in recipetools:
		recipetool_id = recipetool.tool_id
		recipetool_ids.append(recipetool_id)

	for tool_id in tool_ids:
		if tool_id not in recipetool_ids:
			new_recipe_tool = RecipeTool(recipe_id=recipe_id, tool_id=tool_id)
			db.session.add(new_recipe_tool)



	db.session.commit()

	return redirect("/user_profile/{}".format(user_id))
	


@app.route('/favorites')
def show_favorite_recipes():
	"""Shows users personal collection of recipes."""

	user_id = session['logged_in_user']

	favorites = Favorite.query.filter_by(user_id=user_id).all()

	return render_template("user_favorite.html", user_id=user_id, favorites=favorites)


@app.route('/add_to_favorite/<int:recipe_id>')
def add_to_favorite(recipe_id):
	"""Adds recipe to user's personal collection. """

	user_id = session['logged_in_user']

	# favorites = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).all()

	user_favorite = User.query.get(user_id)
	#[<Favorite favorite_id=1, user_id=1, recipe_id=1>, <Favorite favorite_id=3, user_id=1, recipe_id=6>]
	user_favorites_list = user_favorite.favorites
	user_favorits_recipe_ids = [favorite.recipe_id for favorite in user_favorites_list]

	
	if recipe_id not in user_favorits_recipe_ids:
		favorite = Favorite(recipe_id=recipe_id, user_id=user_id)
		db.session.add(favorite)
		db.session.commit()
		#flash("Added to favorites.")
	#else:
		#flash("The recipe is in favprites already.")	


	return redirect('/favorites')

@app.route('/delete_from_favorites/<recipe_id>')
def del_from_favorites(recipe_id):
	"""Delete recipe from favorites"""

	user_id = session['logged_in_user']

	del_favorite = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

	db.session.delete(del_favorite)
	db.session.commit()

	return redirect('/favorites')



@app.route('/logout')
def logout():
	"""Log out user."""

	session.clear()
	#flash("Logged out.")
	return redirect('/')



@app.route('/register', methods=['GET'])
def register_user():
	"""Register users."""

	return render_template("register.html")


@app.route('/register', methods=['POST'])
def verify_user():
	"""Check if user in db, if not add user to db."""

	first_name = request.form.get('fname')
	last_name = request.form.get('lname')
	email = request.form.get('email')
	password = request.form.get('password')

	user = User.query.filter_by(email=email).first()

	if not user:
		new_user = User(fname=first_name, lname=last_name, email=email, password=password)
		db.session.add(new_user)
		db.session.commit()
		session['logged_in_user'] = new_user.user_id
		#flash("Registerd.")
		return redirect("/user_profile/{}".format(new_user.user_id))
	else:
		#flash("Please log in, you've already had account.")
		return redirect('/login')



@app.route('/recipe/<recipe_id>')
def detaild_cake_view(recipe_id):
	"""cake detaild view."""

	recipe = Recipe.query.get(recipe_id)

	avg_score = db.session.query(func.avg(Rating.score).label('average')).filter_by(recipe_id=recipe_id).scalar()

	if "logged_in_user" in session:

		user_id = session['logged_in_user']

		if user_id:
			user_rating = Rating.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()
		else:
			user_rating = None		

		return render_template("cake_detail.html", recipe=recipe, user_rating=user_rating, avg_score=None) 

	else:
		return render_template("cake_detail.html", recipe=recipe, user_rating=None, avg_score=avg_score)


@app.route('/add-rating/<recipe_id>', methods=['POST'])
def add_rating(recipe_id):
	"""Adding/Editing rating."""

	score = 6 - int(request.form.get('score'))
	user_id = session['logged_in_user']
	print score

	rating = Rating.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

	if rating:
		rating.score = score
		#flash("Rating updated.")
	else:
		rating = Rating(recipe_id=recipe_id, user_id=user_id, score=score)
		#flash("Rating added.")
		db.session.add(rating)
	
	db.session.commit()

	return redirect('/recipe/{}'.format(recipe_id))



@app.route('/add_new_recipe', methods=['GET'])
def show_new_recipe_form():
	"""Shows add new recipe form"""

	if "logged_in_user" in session:

		return render_template("add_new_recipe.html")


@app.route('/uploads/<filename>')
def send_image(filename):
    
    return send_from_directory('uploads/', filename)


@app.route('/add_new_recipe', methods=['POST'])
def add_new_recipe():
	"""Add new recipe to db."""


	target = os.path.join(APP_ROOT, 'uploads/')

	if not os.path.isdir(target):
		os.mkdir(target)
	for upload in request.files.getlist('file'):
		filename = upload.filename
		#Verifys if files are supported
		ext = os.path.splitext(filename)[1]
		#if ext in ALLOWED_EXTENSIONS:
			#flash('File extension supported.')
		#else:
			#flash('Upload a valid file.')
		destination = "/".join([target, filename])
		upload.save(destination)


	user_id = session['logged_in_user']
	img_url = "/uploads/" + filename
	
	title = request.form.get('title')
	occasion = request.form.get('occasion').lower()

	occasion_check = Occasion.query.filter_by(oname=occasion).first()

	if not occasion_check:
		new_occasion = Occasion(oname=occasion)
		db.session.add(new_occasion)

	description = request.form.get('description')
	ingridients = request.form.getlist('ingridients')
	instructions = request.form.get('instructions')
	tools = request.form.getlist('tools')

	new_recipe = Recipe(img_url=img_url, rname=title, style=description, instructions=instructions, user_id=user_id)
	db.session.add(new_recipe)
	db.session.commit()

	if not occasion_check:
		new_recipe_occasion = RecipeOccasion(recipe_id=new_recipe.recipe_id, occasion_id=new_occasion.occasion_id)
	else:
		new_recipe_occasion = RecipeOccasion(recipe_id=new_recipe.recipe_id, occasion_id=occasion_check.occasion_id)

	db.session.add(new_recipe_occasion)

	for ingridient in ingridients:
		ingreident_obj = Ingridient.query.filter_by(iname=ingridient).first()
		recipe_ingrident = RecipeIngridient(ingridient_id=ingreident_obj.ingridient_id, recipe_id=new_recipe.recipe_id)
		db.session.add(recipe_ingrident)
	for tool in tools:
		tool_obj = Tool.query.filter_by(tname=tool).first()
		recipe_tool = RecipeTool(tool_id=tool_obj.tool_id, recipe_id=new_recipe.recipe_id)
		db.session.add(recipe_tool)

	db.session.commit()

	recipe = Recipe.query.filter_by(rname=title, style=description).first()

	
	return render_template('new_recipe.html', img_name=filename, recipe=recipe)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = False
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app, "recipe-db")

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')


