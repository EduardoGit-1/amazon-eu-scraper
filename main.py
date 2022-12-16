from requirements import check_requirements
check_requirements()
import requests
from copy import deepcopy
import pandas as pd
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from settings import ENDPOINT, URLS, WHAREHOUSE_PARAM, HEADERS, RESULTS
from items import SEARCH_ITEMS_LIST

def set_search_params(base_url = "https://www.amazon.es/", amazon_name = "AmazonES", item_name = "", min_price = None, max_price = None, search_wharehouse = True):
    item_urls = []
    min_price = min_price * 100 if min_price else None
    max_price = max_price * 100 if max_price else None
    price_string = "&rh=p_36%3A{}-{}".format(min_price, max_price) if min_price or max_price else ""
    item_urls.append({
        "url" : base_url + ENDPOINT.format(item_name, "",price_string),
        "type" : "normal",
        "func" : get_results_grid if amazon_name != "AmazonDE" else get_results_list 
        })
    # if item_condition == "new":
    #     item_condition_string = "&rh=p_n_condition-type%3A15144009031"
    #     item_urls.append({"Normal" : base_url + ENDPOINT.format(item_name, "",price_string, item_condition_string)})
    # elif item_condition == "used":
    #     item_condition_string = "&rh=p_n_condition-type%3A15144010031"
    #     item_urls.append({"Normal" : base_url + ENDPOINT.format(item_name,"", price_string, item_condition_string)})
    # else:
    #     item_urls.append({"Normal" : base_url + ENDPOINT.format(item_name,"", price_string, "&rh=p_n_condition-type%3A15144009031")})
    #     item_urls.append({"Normal" : base_url + ENDPOINT.format(item_name, "",price_string, "&rh=p_n_condition-type%3A15144010031")})
    
    if search_wharehouse:
        item_urls.append({
            "url" : base_url + ENDPOINT.format(item_name, WHAREHOUSE_PARAM, ""),
            "type" : "wharehouse",
            "func" : get_results_list
            })
   
    return item_urls


def get_results_grid(url, amazon_url, amazon_name, item_name):
    
    html_elements = requests.get(url, headers=HEADERS).text
    soup = BeautifulSoup(html_elements, "lxml")
    items_div = soup.find("div", class_="s-main-slot s-result-list s-search-results sg-row")
    items = items_div.find_all("div", class_ = "sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20")
    results_dict = deepcopy(RESULTS)
    for item in items:
        item_title = item.find("div", class_="a-section a-spacing-none a-spacing-top-small s-title-instructions-style").text
        item_price = item.find("span", class_= "a-price-whole")
        if fuzz.partial_ratio(item_title,item_name) < 55 or not item_price:
            continue
       
        item_price = int(item_price.text[:-3].replace("\u202f", "").replace(".", ""))
        item_url = amazon_url[:-1] + item.find("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")["href"]
        shipping_cost_text = item.find("div", class_ = "a-row a-size-base a-color-secondary s-align-children-center").find("span", class_="a-color-base").text
        shipping_cost_text_arr = shipping_cost_text.replace(",", ".").split()
        for string in shipping_cost_text_arr: 
            try:
                shipping_cost = int(float(string))
                total_cost = shipping_cost + item_price
                break 
            except ValueError:
                shipping_cost = shipping_cost_text
                total_cost = item_price
        
        options_starting_at = item.find("div", class_ ="a-section a-spacing-none a-spacing-top-mini")
        options_starting_at = options_starting_at.find("span", class_ = "a-color-base") if options_starting_at else None
        options_starting_at = int(options_starting_at.text[:-5].replace("\u202f", "").replace(".", "")) if options_starting_at else "No more buying options"

        results_dict["Title"].append(item_title)
        results_dict["URL"].append(item_url)
        results_dict["Item Price"].append(item_price)
        results_dict["Shipping Cost"].append(shipping_cost) 
        results_dict["Total Cost"].append(total_cost)
        results_dict["Others Starting At"].append(options_starting_at)
        results_dict["Website"].append(amazon_name)
        results_dict["Warehouse"].append("No")
    df =  pd.DataFrame.from_dict(results_dict)
    return df

def get_results_list(url, amazon_url, amazon_name, item_name):
    print("yep, list")
    return
if __name__ == "__main__":
    for item in SEARCH_ITEMS_LIST:
        df_all = pd.DataFrame.from_dict(deepcopy(RESULTS))
        for amazon_name, amazon_url in URLS.items():
            item_name = item["item_name"].replace(" ", "+")
            item_urls = set_search_params(amazon_url, amazon_name, item_name, item["min_price"] , item["max_price"], item["search_wharehouse"])
            for url_dict in item_urls:
                print("Searching on amazon for:", item["item_name"], "using the following URL:",url_dict["url"])
                result_df = url_dict["func"](url_dict["url"], amazon_url,  amazon_name, item["item_name"])
                #result_df = get_results(url["Normal"], amazon_url, amazon_name, item["item_name"])
                df_all = pd.concat([df_all, result_df], ignore_index=True, sort=False)
                
        df_all = df_all.sort_values(['Total Cost', "Others Starting At"], ascending = [True, True])
        #df_all = df_all.sort_values(['Total Cost'], ascending = [True])
        df_all = df_all.drop_duplicates(subset = ['Title', 'Total Cost'], keep = 'first').reset_index(drop = True)
        df_all.to_excel("results/" +  item["output_file_name"] + ".xlsx")
        print("Found" , len(df_all.index) ,"results for the item", item["item_name"])
       

