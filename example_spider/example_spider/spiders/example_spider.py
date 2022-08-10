import scrapy

file_nutrients = 'recipe_nutrients_147200_149191.csv'
file_ingredients = 'recipe_ingredients_147200_149191.csv'
file_overview = 'recipe_overview_147200_149191.csv'

INGREDIENT_NAMES = "ingredient_names"
INGREDIENT_FIELDS = "ingredient_fields"
NUTRIENT_VALUES = "nutrient_values"
NUTRIENT_NAMES = "nutrient_names"
RECIPE_NAME = "recipe_name"
CUISINE = "cuisine"
INSTRUCTIONS = "instructions"
SOURCE = "source"
TIME = "time"

selectors = {
    RECIPE_NAME: 'body > div.container > div:nth-child(1) > div > center > b > h3::text',
    NUTRIENT_NAMES: 'body > div.container > div:nth-child(2) > div.col.s12.m7 > div > table > tr > td > strong::text',
    NUTRIENT_VALUES: 'body > div.container > div:nth-child(2) > div.col.s12.m7 > div > table > tr > td.roundOff::text',
    INGREDIENT_NAMES: '#myTable > tbody > tr > td:nth-child(1) > a::text',
    INGREDIENT_FIELDS: '#myTable > thead > tr > th::text',
    CUISINE: '#recipe_info > ul > li:nth-child(1) > p::text',
    TIME: '#recipe_info > ul > li:nth-child(3) > p::text',
    INSTRUCTIONS: '#steps::text',
    SOURCE: '#recipe_info > ul > li:nth-child(4) > p > a::attr(href)'
}

class ExampleSpider(scrapy.Spider):
    name = "example_spider"
    recipe_id = None
    recipe_name = None

    def parse(self, response, **kwargs):
        self.recipe_id, self.recipe_name = self.parse_id_name(response)
        self.parse_nutrients(response)
        self.parse_ingredients(response)
        self.parse_overview(response)

    def parse_nutrients(self, response, filename=file_nutrients):
        nutrient_names = self.parse_nutrient_names(response)
        nutrient_values = self.parse_nutrient_values(response)
        self.write(["field", "value"], [["id", "name"] + nutrient_names, [self.recipe_id, self.recipe_name] + nutrient_values], filename)

    def parse_ingredients(self, response, filename=file_ingredients):
        ingredient_names = self.parse_ingredient_names(response)
        ingredient_field_names = self.parse_ingredient_fields(response)
        ingredient_field_names.insert(0, "name")
        ingredient_field_names.insert(0, "id")
        recipe_ids = [self.recipe_id] * len(ingredient_names)
        recipe_names = [self.recipe_name for i in range(len(ingredient_names))]
        ingredient_fields = [[self.ingredient_field_value(response, row, col)
                                for row in range(1, len(ingredient_names) + 1)]
                                for col in range(2, len(ingredient_field_names) + 1)]
        ingredient_fields.insert(0, ingredient_names)
        ingredient_fields.insert(0, recipe_names)
        ingredient_fields.insert(0, recipe_ids)

        self.write(ingredient_field_names, ingredient_fields, filename)

    def parse_overview(self, response, filename=file_overview):
        names = ["field", "value"]
        overview_fields = [
                            "id",
                            "name",
                            "cuisine",
                            "time",
                            "source",
                            "instructions"
                          ]
        overview_values = [
                            self.recipe_id,
                            self.recipe_name,
                            self.parse_cuisine(response),
                            self.parse_time(response),
                            self.parse_source(response),
                            self.parse_instructions(response)
                          ]
        self.write(names, [overview_fields, overview_values], filename)


    def write(self, names, table, filename):
        with open(filename, 'a+') as f:
            for name in names:
                f.write(f"{name}, ")
            f.write("\n")
            for row in range(len(table[0])):
                for col in range(len(table)):
                    f.write(table[col][row].replace(",", ""))
                    f.write(", ")
                f.write("\n")

    def parse_cuisine(self, response):
        return response.css(selectors[CUISINE]).extract()[0].split("\n")[0]

    def parse_time(self, response):
        return response.css(selectors[TIME]).extract()[0].split("\n")[0]

    def parse_source(self, response):
        return "\n".join(response.css(selectors[SOURCE]).extract())

    def parse_instructions(self, response):
        return "\n".join(list(map(lambda x: x.replace("\t", " "), response.css(selectors[INSTRUCTIONS]).extract()[0].split("\n")[1].split(" | ")[1:-1])))

    def parse_nutrient_values(self, response):
        return response.css(
            selectors[NUTRIENT_VALUES]).extract()

    def parse_nutrient_names(self, response):
        return response.css(
            selectors[NUTRIENT_NAMES]).extract()

    def ingredient_field_value(self, response, row, col):
        value = response.css(self.ingredient_field_selector(row, col)).extract()
        return "" if not value else value[0]

    def ingredient_field_selector(self, row, col):
        return f"#myTable > tbody > tr:nth-child({row}) > td:nth-child({col})::text"

    def parse_ingredient_names(self, response):
        return response.css(selectors[INGREDIENT_NAMES]).extract()

    def parse_ingredient_fields(self, response):
        return response.css(selectors[INGREDIENT_FIELDS]).extract()

    def parse_id_name(self, response):
        recipe_id = response.url.split("/")[-1]
        recipe_name = response.css(selectors[RECIPE_NAME]).extract()[0]
        return recipe_id, recipe_name


    def start_requests(self):

        urls = ["https://cosylab.iiitd.edu.in/recipedb/search_recipeInfo/" + x for x in [f"{i}" for i in range(147200, 149191)]]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

