#!/usr/bin/python3
# -*- conding:utf-8 -*-

import csv
import typer
import requests

from lxml import html

app = typer.Typer()

fake_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
}

TEST1_URL = 'https://www.petersofkensington.com.au/Public/Default.aspx'
TEST2_URL = 'https://bestbuy.com.au/coffee-machines/'
TEST3_URL = 'https://www.amazon.com.au/gp/site-directory?ref_=nav_em_fullstore_0_1_1_33'


@app.command()
def test1():
	page = requests.get(TEST1_URL, headers=fake_headers)
	tree = html.fromstring(page.content)
	top_menu_items = tree.xpath('//a[contains(@class, "top-menu-item")]')
	with open('test1_result.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		for idx, item in enumerate(top_menu_items):
			if item.text:
				writer.writerow([idx+1, item.text])


def get_test2_pagination_count(tree):
	pagination_items = tree.xpath('//div[contains(@class, "pagination") and contains(@class, "bottom")]/ul/li')
	return len(pagination_items) - 1


def get_test2_items_on_page(tree):
	return tree.xpath('//ul[contains(@class, "productGrid") and contains(@class, "visible")]/li[contains(@class, "product")]')


def get_test2_items_on_other_pages(page_count):
	all_products = []
	for i in range(2, page_count+1):
		page = requests.get(TEST2_URL + '?sort=featured&page=' + str(i), headers=fake_headers)
		tree = html.fromstring(page.content)
		all_products.extend(get_test2_items_on_page(tree))
	return all_products


class Test2Product():
	def __init__(self):
		self.name = ''
		self.was_price = None
		self.now_price = None
		self.product_url = None
		self.image_url = None


def construct_test2_product(tree):
	product = Test2Product()
	product.name = tree.xpath('.//h4[contains(@class, "card-title")]/a')[0].text
	prices = tree.xpath('.//div[contains(@class, "price-section")]/span')
	product.was_price = prices[0].text_content()
	if len(prices) == 2:
		product.now_price = prices[1].text_content()
	product.product_url = tree.xpath('.//figure/a')[0].attrib['href']
	product.image_url = tree.xpath('.//figure/a/img')[0].attrib['src']
	return product


@app.command()
def test2():
	page = requests.get(TEST2_URL, headers=fake_headers)
	tree = html.fromstring(page.content)
	page_count = get_test2_pagination_count(tree)
	all_products = get_test2_items_on_page(tree)
	all_products.extend(get_test2_items_on_other_pages(page_count))
	all_products = [construct_test2_product(product) for product in all_products]
	with open('test2_result.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		for product in all_products:
			writer.writerow([
				product.name,
				product.was_price,
				product.now_price,
				product.product_url,
				product.image_url,
			])


class Test3SubCategory():
	def __init__(self):
		self.title = ''
		self.link = ''


class Test3Category():
	def __init__(self):
		self.title = ''
		self.sub_categories = []


def construct_test3_categories(tree):
	category = Test3Category()
	category.title = tree.xpath('./*[@class="popover-category-name"]')[0].text
	for tree_sub_category in tree.xpath('.//ul/li'):
		sub_category = Test3SubCategory()
		sub_category.title = tree_sub_category.xpath('.//a')[0].text
		sub_category.link = tree_sub_category.xpath('.//a')[0].attrib['href']
		category.sub_categories.append(sub_category)
	return category


@app.command()
def test3():
	page = requests.get(TEST3_URL, headers=fake_headers)
	tree = html.fromstring(page.content)
	categories = tree.xpath('//table[@id="shopAllLinks"]//*[@class="popover-grouping"]')
	categories = [construct_test3_categories(category) for category in categories]
	with open('test3_result.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		for category in categories:
			for sub_category in category.sub_categories:
				writer.writerow([
					category.title,
					sub_category.title,
					sub_category.link,
			])


@app.command()
def run_all():
	test1()
	test2()
	test3()


def main():
	app()


if __name__ == '__main__':
	main()
