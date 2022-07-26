import scrapy

file_nutrients = 'recipe_nutrients_18786_19999.csv'

class ExampleSpider(scrapy.Spider):
    def parse(self, response, **kwargs):
        recipe = response.css('body > div.container > div:nth-child(1) > div > center > b > h3::text').extract()
        nutrient_names = response.css('body > div.container > div:nth-child(2) > div.col.s12.m7 > div > table > tr > td > strong::text').extract()
        nutrient_values = response.css('body > div.container > div:nth-child(2) > div.col.s12.m7 > div > table > tr > td.roundOff::text').extract()

        with open(file_nutrients, 'a+') as f:
            f.write(f"Recipe, {recipe[0]}")
            f.write("\n")
            for index in range(len(nutrient_names)):
                name = nutrient_names[index].replace(",", "")
                f.write(name)
                f.write(", ")
                f.write(nutrient_values[index])
                f.write("\n")

    name = "example_spider"

    def start_requests(self):

        urls = ["https://cosylab.iiitd.edu.in/recipedb/search_recipeInfo/" + x for x in [f"{i}" for i in range(18786, 19999)]]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

