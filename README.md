# jarvais-highcharts-service
Containerized service to return jarvAIs Analyzer results as dictionary compatible with HighCharts

## Getting Started
1. First build the Docker image: `docker build . -t jarvais-api`
2. Next, spin it up with Docker compose! `docker compose up -d`

Give it a few minutes and the service should be live on `http://127.0.0.1/`

Here are a quick overview of the endpoints while documentation is underway:
* POST `/upload`: add a file to form-data in the request body -> returns a JSON with the `analyzer_id` and metadata
* GET `/visualization/<analyzer_id>/correlation_heatmap?method=<method>`: returns a highcharts JSON of the correlation heatmap of all continuous variables
* GET `/visualization/<analyzer_id>/frequency_heatmap?column1=<column1>&column2=<column2>`: returns a highcharts JSON of the frequency heatmap of two categorical variables
* GET `/visualization/<analyzer_id>/pie)chart?var=<variable>`: returns a highcharts JSON of the pie chart of a given categorical variable