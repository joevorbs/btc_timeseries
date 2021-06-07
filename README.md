## Multivariate Timeseries Forecasting on BTC Price
This repo focuses on a machine-learning approach to timeseries forecasting. This differs from the traditional univariate method as this method allows for the use of multiple features. Using a multivariate approach can also help explain causality and give strong insights into the actual forecast. That is, as long as your data is good! 

A few different methods are included to develop forecasts on the price of bitcoin as there are different ways to perform a timeseries. This is also a way to experiment with Facebook's Prophet timeseries library. Prophet can develop strong univariate forecasts as well as pre-whiten the data for the multivariate approach.

Forecasts will be plotted and stored in the Visualizations folder.

*Currently being ported to aws.

Datasources: 
  1) blockchain.com - Blockchain metrics
  2) coindesk.com - Bitcoin Price

## AWS Architecture
To fully automate this application, a variety of AWS services are employed:
  1) Cloudwatch schedules a lambda function to start an EC2 instance at a specified time each week
  2) Once the instance starts, through the use of user data, a webscrape is ran to collect the current and historical BTC pricing
  3) After the data is downloaded, it lands in an S3 bucket which triggers the blockchain metrics scrape to run
  4) When the blockchain metrics are downloaded to it's S3 bucket, a lambda fuction is triggered to join the BTC data to the blockchain metrics to create an analytical dataset
  5) Once this dataset is created it's stored in another S3 bucket, which triggers a lambda function that utilizes Systems Manager to run the feature selection script on the EC2.
  6) Finally, when the list of features for the actual forecast model are chosen and land in their own S3 bucket, a final lambda function triggers another Systems Manager job to execute the timeseries model on the EC2 and generate a small report and graphic detailing the forecast. 

To note, an attempt at making this program serverless was attemped but using selenium inside lambda was proven to be too difficult and FB Prophet combined with its dependecies as well as the other required python libraries far exceed the storage available on the lambda (using a zip file AND the actual storage in the /tmp directory).
