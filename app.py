from flask import Flask, escape, request, render_template
import json
import os
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favourites', methods=["GET", "POST"])
def favourites():
    filename = os.path.join('data.json')

    #if method is equal to POST, add a new movie to favourites
    if request.method == "POST":

        #create new movie object
        favourite = {
            "title": request.form["title"],
            "id": request.form["id"]
        }

        #open existing file
        with open(filename) as f:
            movies = json.load(f)
            
            #check if list already contains movie to be added
            if len(movies) > 0:
                for movie in movies:
                    if movie["id"] == request.form["id"]:

                        #render error message if match is found
                        return render_template("favourites.html", favourites=movies, error="This movie has already been added to your favourites")

            #if movie does not exist, append and write new list to file            
            movies.append(favourite)
            with open(filename, "w") as write_file:
                json.dump(movies, write_file, indent=2)   
    
    #open data file and parse json for rendering
    with open(filename, "r") as data_file:
        data = json.load(data_file)

    #render an error message if the favourite list is empty   
    if len(data) < 1:
        return render_template("favourites.html", error="No favourites added")

    return render_template('favourites.html', favourites=data)
    

@app.route('/search', methods=['POST'])
def search():
    query = request.form['title']  
    
    #render error message if the query is an empty string
    if query == "":
        return render_template("index.html", error="Please enter a search query")
    
    #make a search request to the movie database
    response = requests.get("http://www.omdbapi.com/?apikey=b2eed1b0&s={0}".format(query))

    #if response status is not OK, render an error message
    if response.status_code != 200:
        return render_template("index.html", error="Unable to connect to the movie database")
    
    #parse response body
    movies = json.loads(response.text)
    
    #if response yields zero results render error message
    if movies["Response"] == 'False':
        return render_template("index.html", error="No results found")

    return render_template("index.html", results=movies["Search"])  


@app.route('/movie/<movie_id>')  
def movie_detail(movie_id):
    #fetch individual movie using movie id.
    response = requests.get("http://www.omdbapi.com/?apikey=b2eed1b0&plot=full&i={0}".format(movie_id))
    
    #if response status is not OK, render an error message
    if response.status_code != 200:
        return render_template("index.html", error="Unable to connect to the movie database")
   
    #parse response body
    movie = json.loads(response.text)

    return render_template("movie.html", movie=movie) 


if __name__ == "__main__":
    app.run()
 
