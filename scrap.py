import requests
from bs4 import BeautifulSoup
import csv

base_url = "https://www.amazon.in/s"
search_params = {
    "k": "bags",
    "crid": "2M096C61O4MLT",
    "qid": "1653308124",
    "sprefix": "ba,aps,283",
    "ref": "sr_pg_"
}

product_data = []

for page_number in range(1, 21):
    url = base_url + "?" + "&".join([f"{key}={value}" for key, value in search_params.items()]) + str(page_number)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    results = soup.find_all('div', {'data-component-type': 's-search-result'})

    for result in results:
        product_url = "https://www.amazon.in" + result.find('a', {'class': 'a-link-normal s-no-outline'}).get('href')
        product_name = result.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text.strip()
        product_price = result.find('span', {'class': 'a-price-whole'}).text.strip()
        product_rating = result.find('span', {'class': 'a-icon-alt'}).text.strip().split()[0]
        product_reviews = result.find('span', {'class': 'a-size-base'}).text.strip().replace(',', '')

        product_response = requests.get(product_url)
        product_soup = BeautifulSoup(product_response.content, 'html.parser')

        product_description = ""
        product_description_element = product_soup.find('div', {'id': 'productDescription'})

        if product_description_element:
            paragraphs = product_description_element.find_all('p')
            for paragraph in paragraphs:
                product_description += paragraph.get_text(strip=True) + " "

        # Extracting the ASIN
        asin_element = product_soup.find(lambda tag: tag.name == 'th' and 'ASIN' in tag.text)
        asin = asin_element.find_next('td').text.strip() if asin_element else ""

        # Extracting the Manufacturer
        manufacturer_element = product_soup.find(lambda tag: tag.name == 'th' and 'Manufacturer' in tag.text)
        manufacturer = manufacturer_element.find_next('td').text.strip() if manufacturer_element else ""

        product_data.append({
            'Product URL': product_url,
            'Product Name': product_name,
            'Product Price': product_price,
            'Rating': product_rating,
            'Number of reviews': product_reviews,
            'Description': product_description,
            'ASIN': asin,
            'Manufacturer': manufacturer
        })

        if len(product_data) >= 200:
            break

    if len(product_data) >= 200:
        break


csv_filename = 'product_data.csv'
csv_fields = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of reviews', 'Description', 'ASIN', 'Manufacturer']
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
    writer.writeheader()
    writer.writerows(product_data)

print(f"Data exported to '{csv_filename}' successfully!")
