import logging
import smtplib
import time

import requests
from bs4 import BeautifulSoup

import config
import product

logger = logging.getLogger(__name__)

# URL example: https://www.amazon.in/Philips-HD7431-20-700-Watt-Coffee/dp/B017NSGHR6/
# Note: Remove the reference parts of the URL
HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/76.0.3809.100 Safari/537.36"}

# Time interval in seconds between checking the price.
TIME_INTERVAL = 60


# Get the price of the product from the website.
# noinspection SpellCheckingInspection
def check_price():
    page = requests.get(product.URL, headers=HEADER)
    soup = BeautifulSoup(page.content, 'html.parser')

    title = soup.find(id="productTitle").get_text()
    title = title.strip()

    price = soup.find(id="priceblock_ourprice").get_text()
    converted_price = int(price[2:3] + price[4:7])

    if converted_price <= product.NOTIFICATION_PRICE:
        send_mail(title, converted_price)


def send_mail(title, price):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(config.FROM_EMAIL, config.PASSWORD)

    subject = "Price fell down!"
    body = "The price for %s fell down to: %s \nCheck it out at: %s" % (title, price, product.URL)

    # formatting the message for the browser to display properly
    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail(
        config.FROM_EMAIL,
        config.TO_EMAIL,
        msg
    )

    logger.info("Success: MAIL SENT! PRICE IS DOWN!")
    server.quit()


# TODO: Add a cron job script to run this on a server
while True:
    check_price()
    time.sleep(TIME_INTERVAL)
