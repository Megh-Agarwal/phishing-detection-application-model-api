# Phishing detection (probability based) application ML model API

This application corresponds to a FastAPI server that serves one job: Estimate and return the probability that a URL is trying to phish a user.
The FastAPI accepts only a HTTP POST request to the following URL: https://phishing-model-api.herokuapp.com/predict wherein the POST body should have the following body:

    { "url": "your url" }

The application works in a simple way, it first loads the ML model, estimates the probability by breaking the input URL into different components (features to be input in the ML Model),
and return the provided estimated probability (the probability says that "x" or "x%" is the chance that the URL is trying to phish a user).

For indepth information regarding how the model is trained, with its internal, please refer the following [research paper](https://www.ijser.org/onlineResearchPaperViewer.aspx?Estimating_the_Phishing_Non_phishing_Probability_of_a_URL_using_a_Tree_based_Ensemble_Model.pdf).

This application is just an API, a web application is created for users to input their URLs following the showcase of the estimated probabilities. Please visit the following
link for a demo: https://phishing-detection-application.herokuapp.com/
