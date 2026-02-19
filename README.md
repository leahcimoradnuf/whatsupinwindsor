a simple-as-can be flask app for tracking, summarizing, and reporting on official government proceedings in Windsor CT

architecture 
app.py - the front-end flask app, queries database
main.py - the backend routine for aggregating info, runs on cronjob, writes to database
reporter.py - module that interfaces with 3rd party zoom recording bot (recall.ai)
rssfeed.py - module that retrieves new data from the town's RSS feed
writer.py - module that interfaces with OpenAI api to use text summarization models
