from typing import List

from config.config_handler import ParametersHandler
from data_types.estate import Estate
from scraper.otodom_scraper import OtoDomScraper

if __name__ == "__main__":

    scraper: OtoDomScraper = OtoDomScraper()
    results: List[Estate] = scraper.parse_site()

    scraper.save_data(
        temp_path=ParametersHandler().get_params()["results_file"],
        to_write=results,
    )
