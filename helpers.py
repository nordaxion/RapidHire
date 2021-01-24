import requests
import pprint as pp

api_key = "AIzaSyBzpUJpmYuchAFYRwZVOdgkca_KOVSp8mg"
directions_api_url = "https://maps.googleapis.com/maps/api/directions/json?"

def get_distance(job_location, user_location):
    job_location_string = job_location.split()
    job_location_string = "+".join(job_location_string)

    user_location_string = user_location.split()
    user_location_string = "+".join(user_location_string)

    response = requests.get(directions_api_url + "origin=" + job_location_string + "&destination=" + user_location_string + "&key=" + api_key)
    distance = response.json()
    pp.pprint(distance)
    distance = distance["routes"][0]["legs"][0]["distance"]["value"]

    return distance

def filter_distance(posting_location, potential_employees_list, distance=5):
    filtered_results = []
    for potential_employee in potential_employees_list:
        if get_distance(posting_location, potential_employee[2]) < distance * 1609.34:
            filtered_results.append(potential_employee)
    return filtered_results
