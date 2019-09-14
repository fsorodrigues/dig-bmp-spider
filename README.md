# Contents
## `./Spider`
This is the directory where the actual spider/scraper code is.

## `./`
- `requirements.txt`  
If you intend to use a virtual environment (which is advised), this is a list of modules that need to be installed. After activating your virtual environment, you can run `pip install ./requirements.txt`.

- `scrapy.cfg`  
This file has to be in the root directory or things break.

- `gsheet-auth.json` (omitted for security reasons)

- `auth_google.py`  
Quick function to authenticate web app to Google. This is how we programatically append rows to a gsheet.  
This one in particular uses the `.from_json_keyfile_name`, which on its turn depends on `gsheet-auth.json` (see above), but other methods could be used: for example, `.from_json_keyfile_dict` in tandem with environment variables is a classic alternative (and probably the most recommended when deploying to cloud services).  
See [documentation](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.service_account.html) for additional information.  

- `.env`  
Sets environment variables that will loaded with `dotenv`.

- `run-scraper.sh` (optional)
I use a bash script be able to call the script as a cronjob from a Python virtual environment. It would look somewhat like this:
```bash
#!/bin/bash
cd /absolute/path/to/root
PATH=$PATH:/absolute/path/to/virtual/env/bin/
export PATH
scrapy crawl spider
```
- `Procfile` (optional)
Used when deploying to some cloud services

## `./StringParser`
Just some utility functions I decided to spinoff into a separate file.

# Running the scraper
Scrapy is a powerful tool and handles a lot of things for you. It is also a command line utility. [Documentation](https://docs.scrapy.org/en/latest/) is robust and the tutorials are really good.  
Rather than a .py script, the scraper is called by passing its name to a subcommand from the root directory:
```bash
scrapy crawl [NAME]
```
`[NAME]` can be arbitrarily defined by you in `./spider/spiders/some_script.py`. Something like this:
```Python
...
# creating Spider class
class Spider(scrapy.Spider):
    # assigning name. this will be used to call the spider in shell command.
    name = 'spider'
    ...
```

# Spider and Pipelines
As I mentioned, Scrapy handles a lot of things automatically. One of those things is the relationship between your spiders and the `./spider/pipelines.py` file.

One small parenthesis before we dive into pipelines: the spider should (generally) be a Python generator, which is why it uses the `yield` keyword instead of the `return`.

That is part of the magic of Scrapy: it hands the result of that generator — the scraped values — to a sequence of pipelines.

After the scraper has retrieved data from a website, I mainly use pipelines for general tasks such as checking for duplicates previously scraped for example. Saving values to DBs and sending email notifications is also achieved with pipelines.

Pipelines are also Python classes. They can receive arbitrary names and mostly rely on a `process_item` function, which is automatically called by Scrapy for every item that is handed to the pipeline.

Which pipelines get called is defined in the `ITEM_PIPELINES` dict in ./spider/settings.py. They are ordered by the integer value assigned to them. Like this:
```Python
ITEM_PIPELINES = {
   'spider.pipelines.CheckDuplicatesPipeline': 100,
   'spider.pipelines.ParseTime': 200,
   'spider.pipelines.StorePipeline': 300,
   'spider.pipelines.SendNotification': 400
}
```
