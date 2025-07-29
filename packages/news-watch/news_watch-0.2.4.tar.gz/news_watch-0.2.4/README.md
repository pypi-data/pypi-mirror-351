# news-watch: Indonesia's top news websites scraper

[![PyPI version](https://badge.fury.io/py/news-watch.svg)](https://badge.fury.io/py/news-watch)
[![Build Status](https://github.com/okkymabruri/news-watch/actions/workflows/test.yml/badge.svg)](https://github.com/okkymabruri/news-watch/actions)
[![PyPI Downloads](https://static.pepy.tech/badge/news-watch)](https://pepy.tech/projects/news-watch)


news-watch is a Python package that scrapes structured news data from [Indonesia's top news websites](#supported-websites), offering keyword and date filtering queries for targeted research


> ### ⚠️ Ethical Considerations & Disclaimer ⚠️
> **Purpose:** This project is intended for educational and research purposes only. It is not designed for commercial use that could be detrimental to the news source providers.
> 
> **User Responsibility:**
> - Users of this software are solely responsible for their actions and must comply with the Terms of Service and `robots.txt` file of each news website they intend to scrape.
> - Aggressive scraping or any use that violates a website's terms may lead to IP blocking or other consequences from the website owners.
> - We strongly advise users to scrape responsibly, respect website limitations, and avoid overloading servers.


## Installation

You can install newswatch via pip:

```bash
pip install news-watch
```

After installing the package, you need to install Playwright browsers:

```bash
playwright install chromium
```

To install the development version:

```bash
pip install git+https://github.com/okkymabruri/news-watch.git@dev
playwright install chromium
```

## Usage

To run the scraper from the command line:

```bash
newswatch -k <keywords> -sd <start_date> -s [<scrapers>] -of <output_format> -v
```
Command-Line Arguments

`--keywords`, `-k`: Required. A comma-separated list of keywords to scrape (e.g., -k "ojk,bank,npl").

`--start_date`, `-sd`: Required. The start date for scraping in YYYY-MM-DD format (e.g., -sd 2025-01-01).

`--scrapers`, `-s`: Optional. A comma-separated list of scrapers to use (e.g., -s "kompas,viva"). Use 'auto' for platform-appropriate scrapers (default), or 'all' to force all scrapers (may fail on some platforms).

`--output_format`, `-of`: Optional. Specify the output format (currently support csv, xlsx).

`--verbose`, `-v`: Optional. Show all logging output (silent by default).

`--list_scrapers`: Optional. List supported scrapers.


### Examples

Scrape articles related to "ihsg" from January 1st, 2025:

```bash
newswatch --keywords ihsg --start_date 2025-01-01
```

Scrape articles for multiple keywords (ihsg, bank, keuangan) with verbose logging:

```bash
newswatch -k "ihsg,bank,keuangan" -sd 2025-01-01 -v
```

List supported scrapers:

```bash
newswatch --list_scrapers
```

Scrape articles for specific news website (detik) with excel output format:

```bash
newswatch -k "ihsg" -s "detik" --output_format xlsx
```

Force all scrapers (may fail on Linux due to restrictions):

```bash
newswatch -k "ekonomi" -sd 2025-01-01 -s "all"
```

## Run on Google Colab

You can run news-watch on Google Colab [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/okkymabruri/news-watch/blob/main/notebook/run-newswatch-on-colab.ipynb)

## Output

The scraped articles are saved as a CSV or XLSX file in the current working directory with the format `news-watch-{keywords}-YYYYMMDD_HH`.

The output file contains the following columns:

- `title`
- `publish_date`
- `author`
- `content`
- `keyword`
- `category`
- `source`
- `link`

## Supported Websites

- [Bisnis.com](https://www.bisnis.com/)
- [Bloomberg Technoz](https://www.bloombergtechnoz.com/)
- [CNBC Indonesia](https://www.cnbcindonesia.com/)
- [Detik.com](https://www.detik.com/)
- [Jawapos.com](https://www.jawapos.com/)
- [Katadata.co.id](https://katadata.co.id/)
- [Kompas.com](https://www.kompas.com/)
- [Kontan.co.id](https://www.kontan.co.id/)
- [Media Indonesia](https://mediaindonesia.com/)
- [Metrotvnews.com](https://metrotvnews.com/)
- [Okezone.com](https://www.okezone.com/)
- [Tempo.co](https://www.tempo.co/)
- [Viva.co.id](https://www.viva.co.id/)


> Note:
> - Some scrapers ([Kontan.co.id](https://www.kontan.co.id/), [Jawapos](https://www.jawapos.com/), [Bisnis.com](https://www.bisnis.com/)) are automatically excluded on Linux platforms due to compatibility issues. Use `-s all` to force all scrapers (may cause errors).
> - Limitation: [Kontan.co.id](https://www.kontan.co.id/) scraper can process a maximum of 50 pages.

## Contributing

Contributions are welcome! If you'd like to add support for more websites or improve the existing code, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. The authors assume no liability for misuse of this software.


## Citation

If you use this software, please cite it using the following:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15401513.svg)](https://doi.org/10.5281/zenodo.15401513)

```bibtex
@software{mabruri_newswatch,
  author       = {Okky Mabruri},
  title        = {news-watch},
  version      = {0.2.4},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.15401513},
  url          = {https://doi.org/10.5281/zenodo.15401513}
}
```

Available on Zenodo: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15401513.svg)](https://doi.org/10.5281/zenodo.15401513)

### Related Work
* [indonesia-news-scraper](https://github.com/theyudhiztira/indonesia-news-scraper)
* [news-scraper](https://github.com/binsarjr/news-scraper)
