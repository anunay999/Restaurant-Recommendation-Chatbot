# RASA Restaurant Recommendation Chatbot

## Overview 

Chatbot developed using Rasa framework for restaurant recommendations using Zomato API is an AI-powered conversational agent that can help users discover the best restaurants in their vicinity based on their preferences. The chatbot can converse with users in natural language and ask them questions about their preferred cuisine, budget, location, and other specific requirements. It then uses the Zomato API to fetch the most relevant results and presents them to the user in a conversational format. The chatbot can also handle queries related to restaurant timings, menus, and reservations, making it a one-stop solution for all restaurant-related needs.


## Installation

To install Rasa Open Source:
```bash
pip3 install rasa
```

Follow this [link](https://rasa.com/docs/rasa/installation/environment-set-up) for more info.

## Training the model

To train the model
```bash
rasa train	
```
To run the rasa server
```
rasa run
```

To run the model in shell mode

```bash
rasa shell
```

To run the model in interactive mode

```bash
rasa interactive
```

Follow this [link](https://rasa.com/docs/rasa/command-line-interface) for more commandds

## Configuring Chat Application
In my case, I have used slack to test the chat bot. But can be connected to any supported chat app.
Configure in `credentials.yml` to initate connection.

## Deploy

To deploy rasa server on k8s follow this [link](https://rasa.com/docs/rasa/deploy/deploy-rasa).



