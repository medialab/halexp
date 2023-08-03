from flask import Flask, request, jsonify
from .retriever import Retriever

# create the Flask app
app = Flask(__name__)


retriever = Retriever(
    data_path='/home/jimena/work/dev/halexp/hal-productions.json')


# @app.route('/query-example')
# def query_example():
#     # if key doesn't exist, returns None
#     language = request.args.get('language')

#     # if key doesn't exist, returns a 400, bad request error
#     framework = request.args['framework']

#     # if key doesn't exist, returns None
#     website = request.args.get('website')

#     return '''
#               <h1>The language value is: {}</h1>
#               <h1>The framework value is: {}</h1>
#               <h1>The website value is: {}'''.format(language, framework, website)


# allow both GET and POST requests
@app.route('/form-example', methods=['GET', 'POST'])
def form_example():

    print(retriever)

    # handle the POST request
    if request.method == 'POST':
        language = request.form.get('language')
        framework = request.form.get('framework')
        return '''
                  <h1>The language value is: {}</h1>
                  <h1>The framework value is: {}</h1>'''.format(language, framework)

    return '''
              <form method="POST">
                  <div><label>Language: <input type="text" name="language"></label></div>
                  <div><label>Framework: <input type="text" name="framework"></label></div>
                  <input type="submit" value="Submit">
              </form>'''


# # GET requests will be blocked
# @app.route('/json-example', methods=['POST'])
# def json_example():
#     request_data = request.get_json()

#     language = request_data['language']
#     framework = request_data['framework']

#     # two keys are needed because of the nested object
#     python_version = request_data['version_info']['python']

#     # an index is needed because of the array
#     example = request_data['examples'][0]

#     boolean_test = request_data['boolean_test']

#     return jsonify({"a": 1, "b": 2, "c": 3})


# if __name__ == '__main__':
#     # run app in debug mode on port 5000
#     app.run(debug=True, port=5000)
