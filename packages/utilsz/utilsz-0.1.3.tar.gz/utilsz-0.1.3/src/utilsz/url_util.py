# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-09-30 10:44:28


from urllib.parse import urlparse


def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"
