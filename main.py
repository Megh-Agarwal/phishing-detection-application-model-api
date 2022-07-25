from fastapi import Request, FastAPI, status, Response
from fastapi.middleware.cors import CORSMiddleware
import pickle
from scripts.breakdown import *
from dotenv import load_dotenv
import os
import urllib.request

load_dotenv()

app = FastAPI()

origins = [
    os.environ["REQUESTER"]
]

if (os.environ["MODE"] == "production"):
    urllib.request.urlretrieve("https://www.dropbox.com/s/6g0h5xfkijyjuwp/model.pkl?dl=1", "model.pkl")
    print("Downloading model.pkl")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins
)

@app.post("/predict")
async def predict(response: Response, request: Request, status_code=200, response_class=Response):
    try:
        # Get the body of the request
        post_body = await request.json()
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return {
            'status': '500',
            'message': 'An internal server error occured while processing the request.'
        }

    # If the url key inst present in the post body
    if "url" not in post_body:
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {
            'status': '400',
            'message': 'Could not find a URL to predict phishing probabilty.'
        }

    # Set the URL that needs to be predicted
    url = post_body["url"]

    # Found empty url string, hence prediction cannot be made.
    if(url == ""):
        response.status_code = status.HTTP_400_BAD_REQUEST

        return {
            'status': '400',
            'message': 'Found empty URL string to predict phishing probability.'
        }

    # Load model to predict phishing detection.
    loaded_model = pickle.load(open("model/model.pkl", 'rb'))

    # Break the URL down in multiple components.
    breakdown = url_breakdown(url)

    # Convert to dictionary
    breakdownInDict = convertToDictionary(
        breakdown,
        [
            "Hostname length",
            "Number of digits (Hostname)",
            "Number of special characters (Hostname)",
            "Subdomain length",
            "Domain length",
            "Number of subdomain(s)",
            "Number of parameter(s)",
            "Length of parameter(s)",
            "Length of values of parameter(s)",
            "Number of special characters in query",
            "Number of directories",
            "Length of directories",
            "Number of special characters in directories",
            "Number of fragment(s)",
            "Length of fragment(s)",
            "Length of values of fragment(s)",
            "Number of special characters in fragment(s)",
            "Brand found",
            "Number of brands found",
            "Brand in domain",
            "Brand in domain exactly",
            "Is typosquatting"
        ]
    )

    # Predict the probabilties for whether the URL is phishing or not
    predicted_probabilties = loaded_model.predict_proba([breakdown])[:, 1]

    # Return success response
    response.status_code = status.HTTP_200_OK
    return {
        "status": "200",
        "message": "Successfully predicted the phishing probability for the input URL.",
        "data": {
            "probability": predicted_probabilties[0],
            "breakdown": breakdownInDict
        }
    } 