ENDPOINT = "s?k={}{}{}" #item name;wharehouse; price range;
WHAREHOUSE_PARAM = "&i=warehouse-deals"
URLS = {
    "AmazonES" : "https://www.amazon.es/",
    "AmazonFR" : "https://www.amazon.fr/",
    "AmazonIT" : "https://www.amazon.it/",
    #"AmazonDE" : "https://www.amazon.de/",
}

HEADERS = {'User-Agent': 'Mozilla/5.0'}

RESULTS = {
    "Title" : [],
    "URL" : [],
    "Item Price" : [],
    "Shipping Cost" : [],
    "Total Cost" : [],
    "Others Starting At" : [],
    "Website" : [],
    "Warehouse" : []
}
#&rh=p_36%3A20000-50000 price min to high
#&ref=sr_nr_p_n_condition-type_1 (tipo 1 é novo, tipo 2 é usado)