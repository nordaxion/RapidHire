import requests

api_key = "AIzaSyBzpUJpmYuchAFYRwZVOdgkca_KOVSp8mg"
directions_api_url = "https://maps.googleapis.com/maps/api/directions/json?"

def get_distance(job_location, user_location):
    job_location_string = job_location.split()
    job_location_string = "+".join(job_location_string)

    user_location_string = user_location.split()
    user_location_string = "+".join(user_location_string)

    response = requests.get(directions_api_url + "origins=" + job_location_string + "&destinations=" + user_location_string + "&key=" + directions_api_url)
    distance = response.json()["routes"][0]["legs"][0]["distance"]["text"]
    distance_int = int("".join([char for char in distance if char.isnumeric()]))

    return distance_int

def filter_distance(posting_location, potential_employees_list, distance=5):
    filtered_results = []
    for potential_employee in potential_employees_list:
        if get_distance(posting_location, potential_employee[2]) < distance:
            filtered_results.append(potential_employee)
    return filtered_results
