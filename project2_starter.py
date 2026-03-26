# SI 201 HW4 (Library Checkout System)
# Your name: Ashni Pothineni
# Your student id: 4559 8385
# Your email: apothine@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
    # Resources used:
        # https://stackoverflow.com/questions/13518874/python-regex-get-end-digits-from-a-string

# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listings = []

    # Open the file and feed file handle into Beautiful Soup
    f_handler = open(html_path, 'r')
    soup = BeautifulSoup(f_handler, 'html.parser')

    # Find all div tags that hold listing title and id
    listings_html = soup.find_all('div', class_='t1jojoys dir dir-ltr')

    # Go through all listing tags
    for l in listings_html:
        # Get id in div tag and extract listing id
            # In div tag, id appears like: id='title_<listing id>'
        id = l.get('id', None)
        listing_id = re.match(r'.*?_([0-9]+)$', id).group(1)

        # Get title text
        listing_title = l.text

        # Append (title, id) to list of listings
        listings.append((listing_title, listing_id))

    f_handler.close()
    return listings
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listing_details = {}

    file_path = os.path.join('html_files', f'listing_{listing_id}.html')
    f_handler = open(file_path, 'r')
    soup = BeautifulSoup(f_handler, 'html.parser')

    # Get list item and then inner span to get policy number
    li = soup.find('li', class_='f19phm7j dir dir-ltr')
    span_policy = li.find_next('span')
    policy_num = span_policy.text
    # Ensure capitalization of "Pending" or "Exempt" to follow p2 instructions
    if policy_num.lower() == "pending" or policy_num.lower() == "exempt":
        policy_num = policy_num.capitalize()

    # Get span to see if 'Superhost' listed, if not set to 'regular'
    span_type = soup.find('span', class_='_1mhorg9')
    host_type = span_type.text if span_type else 'regular'

    # There are two difference formats observed for host name and room type listed on an html page
        # (1) Get h2 with host name and room type, pull out text and get host name(s) and use string matching to assign room type
        # (2) Get two divs that separate room type and host name, pull out text and get host name(s) and assign room type

    # Set host name and room type to None
    host_name = None
    room_type = None

    # Format (1)
    h2_name_room = soup.find('h2', class_='_14i3z6h')
    if h2_name_room:
        hosted_by = h2_name_room.get_text(strip=True)
        match = re.search(r'.*?[Hh]osted by\s+(.+)$', hosted_by)
        if match:
            host_name = match.group(1)

        lower_hosted = hosted_by.lower()
        # Check if keyword for room type in string and assign room type
        if "private" in lower_hosted:
            room_type = "Private Room"
        elif "shared" in lower_hosted:
            room_type = "Shared Room"
        else:
            room_type = "Entire Room"

    # If Format (1) provides nothing, then follow with Format (2) to collect info
    if host_name is None:
        room_div = soup.find('div', class_='_kh3xmo')
        host_div = soup.find('div', class_='_cv5qq4')

        host_text = host_div.get_text(strip=True)
        host_name = re.search(r'.*?[Hh]osted by\s+(.+)$', host_text).group(1)
        room_text = room_div.get_text(strip=True).lower()

        # Check if keyword for room type in string and assign room type
        if "private" in room_text:
            room_type = "Private Room"
        elif "shared" in room_text:
            room_type = "Shared Room"
        else:
            room_type = "Entire Room"

    # Get div with text "Location" and then next span to get location rating, if not found set rating to 0.0
    div_outer = soup.find('div', class_='_y1ba89', string="Location")
    span_loc = div_outer.find_next('span', class_='_4oybiu') if div_outer else None
    location_rating = float(span_loc.text) if span_loc else 0.0

    # Create listing details inner dictionary
    listing_details[listing_id] = {}
    details = listing_details[listing_id]
    details['policy_number'] = policy_num
    details['host_type'] = host_type
    details['host_name'] = host_name
    details['room_type'] = room_type
    details['location_rating'] = location_rating

    f_handler.close()
    return listing_details
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listing_db = []

    # Get listing results (title, id)
    listing_results = load_listing_results(html_path)
    
    # For each listing id, get the listing details and append to listing database (list of tuples)
    for listing in listing_results:
        title, id = listing
        listing_details = get_listing_details(id)

        details = listing_details[f'{id}']
        listing_db.append((title, id, details['policy_number'], details['host_type'], details['host_name'], details['room_type'], details['location_rating']))

    return listing_db
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    header = ['Listing Title', 'Listing ID', 'Policy Number', 'Host Type', 'Host Name', 'Room Type', 'Location Rating']

    # Sort data in reverse order by location rating
    data = sorted(data, key=lambda x: x[6], reverse=True)

    # Write to csv
    with open(filename, 'w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=',')
        csv_writer.writerow(header)     # Write header row
        for row in data:
            csv_writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # Check that the number of listings extracted is 18.
        self.assertEqual(len(self.listings), 18)
        # Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # Call get_listing_details() on each listing id above and save results in a list.
        results = []
        for id in html_list:
            details = get_listing_details(id)
            results.append(details)

        # Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        self.assertEqual(results[2]["1944564"]["location_rating"], 4.9)

    def test_create_listing_database(self):
        # Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        for listing in self.detailed_data:
            self.assertEqual(len(listing), 7)
        # Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        last_tuple = self.detailed_data[-1]
        self.assertEqual(last_tuple, ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8))

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")
        
        # Call output_csv() to write the detailed_data to a CSV file.
        output_csv(self.detailed_data, out_path)
        # Read the CSV back in and store rows in a list.
        with open('airbnb_dataset.csv') as data:
            reader = csv.reader(data)
            rows = []
            for row in reader:
                rows.append(row)
        # Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        self.assertEqual(rows[1], ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"])

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)