from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import pandas as pd
from typing import Dict, Text, Any, List
from rasa_sdk import Tracker

import smtplib
from email.message import EmailMessage
import json

zomato = pd.read_csv('zomato.csv')
zomato = zomato.drop_duplicates().reset_index(drop=True)
tier_1_cities = ['Ahmedabad', 'Bangalore', 'Chennai', 'New Delhi', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune']
tier_2_cities = ['Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly', 'Belgaum',
                 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bilaspur', 'Bokaro Steel City',
                 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai', 'Durgapur', 'Dindigul',
                 'Erode', 'Faridabad', 'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gwalior',
                 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli–Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar',
                 'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal',
                 'Kochi', 'Kolhapur', 'Kollam', 'Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow', 'Madurai', 'Malappuram',
                 'Mathura', 'Mangalore', 'Meerut', 'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore',
                 'Noida', 'Patna', 'Pondicherry', 'Purulia', 'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi',
                 'Rourkela', 'Ratlam', 'Salem', 'Sangli', 'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat',
                 'Thanjavur', 'Thiruvananthapuram', 'Thrissur', 'Tiruchirappalli', 'Tirunelveli', 'Tiruvannamalai',
                 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-Virar City', 'Vijayawada', 'Visakhapatnam',
                 'Vellore', 'Warangal']
available_cities = tier_1_cities + tier_2_cities


class ValidateRestaurantForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_restaurant_form"

    @staticmethod
    def cuisine_db() -> List[Text]:
        return [
            "chinese",
            "north indian",
            "south indian",
            "italian",
            "mexican",
            "american"
        ]

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""
        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_cuisine(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        print(value,'enter')
        if value.strip() in ["Chinese","North Indian","South Indian","Italian","Mexican","American"]:
            print(value,'yes')
            return {"cuisine": value}
        else:
            print(value, 'no')
            dispatcher.utter_message(response="utter_wrong_cuisine")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"cuisine": None}

    def validate_price(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if isinstance(value, str):
            if (value == 'Lesser than Rs. 300') or (value == "Rs. 300 to 700") or (value == "More than 700"):
                return {'price': value}
            elif self.is_int(value) and int(value) > 0:
                return {"price": int(value)}
            else:
                dispatcher.utter_message(response="utter_wrong_num_people")
                # validation failed, set slot to None
                return {"price": None}

    def validate_location(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate outdoor_seating value."""

        if isinstance(value, str):
            if value in available_cities:
                if zomato[zomato.City == value].shape[0] == 0:
                    dispatcher.utter_message(response="utter_location_not_operable")
                    return {"location": None}
                else:
                    return {"location": value}
            else:
                dispatcher.utter_message(response="utter_location_not_operable")
                return {"location": None}


class ActionSearchRestaurants(Action):

    def name(self) -> Text:
        return "action_search_restaurants"

    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        cost_for_two = tracker.get_slot('price')
        results = self.RestaurantSearch(City=loc, Cuisine=cuisine, cost=cost_for_two)
        response = str()
        if results.shape[0] == 0:
            response = "No Results"
        else:
            response = "Here are some recommendation based on your preference:"
            for restaurant, counter in zip(results.iterrows(), range(1, len(results) + 1)):
                restaurant = restaurant[1]
                response = response + f"\n {counter}. {restaurant['Restaurant Name']} in {restaurant['Address']} rated {restaurant['Aggregate rating']} with avg cost {restaurant['Average Cost for two']} \n\n"
        dispatcher.utter_message("-----\n" + response)
        return [SlotSet('location', loc)]

    def filter_Cities(self, zomato_data=zomato):
        zomato_filter = zomato_data[zomato_data.City.isin(available_cities)]
        return zomato_filter

    def RestaurantSearch(self, City, Cuisine, cost, top=5, zomato_data=zomato):
        zomato_data = self.filter_Cities(zomato_data)
        lower_price = 0
        upper_price = max(zomato['Average Cost for two'])
        if cost == 'Lesser than Rs. 300':
            upper_price = 300
        elif cost == 'Rs. 300 to 700':
            lower_price = 300
            upper_price = 700
            range_flag = True
        elif cost == 'More than 700':
            lower_price = 700
        else:
            price = int(cost)
            upper_price = price - 200
            lower_price = price + 500
        zomato_filter = zomato_data[(zomato_data.City == City) & (zomato_data['Cuisines'].str.contains(Cuisine)) & (
            zomato_data['Average Cost for two'].between(lower_price, upper_price, inclusive=False))]
        zomato_filter = zomato_filter.sort_values(by='Aggregate rating', ascending=False)
        zomato_filter = zomato_filter.drop_duplicates(subset='Restaurant ID', keep="last")
        zomato_filter = zomato_filter[
            ['Restaurant Name', 'Address', 'Aggregate rating', 'Average Cost for two', 'Cuisines']]
        return zomato_filter.head(top)


class ActionSendMail(Action):
    def name(self):
        return 'action_send_mail'

    def run(self, dispatcher, tracker, domain):
        pass
    # MailID = tracker.get_slot('mail_id')
    # sendmail(MailID,response)
    # return [SlotSet('mail_id',MailID)]
