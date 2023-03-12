import logging
import time
from time import sleep
from typing import Any, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, ResultSet, Tag, element
from requests.adapters import HTTPAdapter
from requests.sessions import Session
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from tenacity import retry
from tenacity.wait import wait_exponential
from urllib3.util import Retry

from config.config_handler import ParametersHandler, PresetsHandler
from data_types.estate import Estate
from data_types.estate_details import EstateDetails

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(message)s"
)


class OtoDomScraper:
    PARAMS = ParametersHandler().get_params()
    PRESETS = PresetsHandler().get_presets()

    def __init__(self) -> None:
        self.session: Session = self._init_session()
        self.browser: Firefox
        self._reset_browser()
        # For script execution time probing
        self.time_start: float = time.time()
        self.time_stop: float

    def _init_session(self) -> Session:
        """
        Start session per single browser instance.
        """
        session: Session = Session()
        retries: Retry = Retry(
            connect=self.PARAMS["retry"]["connect"],
            read=self.PARAMS["retry"]["read"],
            redirect=self.PARAMS["retry"]["read"],
        )

        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.headers.update({"User-agent": self.PARAMS["agent"]})

        return session

    def _reset_browser(self) -> None:
        """
        Reset browser when visiting ascending sites
        in order to avoid session error.
        """
        browser_options: Options = Options()
        browser_options.add_argument("--headless")
        self.browser = Firefox(options=browser_options)

    @retry(wait=wait_exponential(multiplier=1, min=2, max=5))
    def get_listing_page_soup(self, page_no: int) -> BeautifulSoup:
        """
        Get and return html content of anouncement listing page.
        Return: BeautifulSoup object
        """

        search_base_url: str = f"{self.PARAMS['search_base_url']}"
        offering_type: str = f"{self.PARAMS['offering_type']}/"
        estate_type: str = f"{self.PARAMS['estate_type']}/"
        city: str = f"{self.PARAMS['city']}/"
        district: str = f"{self.PARAMS['district']}?"
        radius: str = (
            f"{self.PARAMS['radius']}={self.PARAMS['radius_value']}&"
        )
        page_no: str = f"{self.PARAMS['pagination']}={page_no}&"
        max_listing_links: str = (
            f"limit={self.PARAMS['max_listing_links']}&"
        )
        price_min: str = f"{self.PARAMS['price_min']}={self.PARAMS['price_min_value']}&"
        price_max: str = f"{self.PARAMS['price_max']}={self.PARAMS['price_max_value']}&"
        area_min: str = f"{self.PARAMS['area_min']}={self.PARAMS['area_min_value']}&"
        area_max: str = f"{self.PARAMS['area_max']}={self.PARAMS['area_max_value']}&"
        suffix_url: str = f"{self.PARAMS['suffix_url']}"

        constructed_url: str = (
            search_base_url
            + offering_type
            + estate_type
            + city
            + district
            + radius
            + page_no
            + max_listing_links
            + price_min
            + price_max
            + area_min
            + area_max
            + suffix_url
        )

        logging.info(msg="Search url " + constructed_url)

        # If next page of listing visited
        self._reset_browser()

        assert (
            self.browser is not None
        ), "Failure in intializing the Browser!"

        with self.browser as browser:
            browser.get(constructed_url)
            # Scroll page down to the bottom to fetch complete content
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            page_source: str = browser.page_source
            page_soup: BeautifulSoup = BeautifulSoup(
                page_source, "html.parser"
            )

        return page_soup

    @retry(wait=wait_exponential(multiplier=1, min=2, max=5))
    def get_estate_page_soup(self, url: str) -> BeautifulSoup:
        """
        Get and return html content of particular estate anouncement page.
        Return: BeautifulSoup object
        """

        self._reset_browser()

        with self.browser as browser:
            browser.get(url)
            page_source: str = browser.page_source
            page_soup: BeautifulSoup = BeautifulSoup(
                page_source, "html.parser"
            )

        return page_soup

    def get_estate_details(
        self, details_el_tag: element.Tag
    ) -> List[str]:
        """
        Get and return estate anouncement details as list[str].
        """
        estate_details: list[str] = []

        for el in details_el_tag:
            try:
                text: str = el.text.strip()
                estate_details.append(text)
            except AttributeError:
                estate_details.append("no data")

        return estate_details

    def parse_estate(self, url: str):
        """
        Get estate details from url and return EstateDetails validated model.
        """
        estate_soup: BeautifulSoup = self.get_estate_page_soup(url)

        try:
            # Details in summary tab
            estate_details_summary: ResultSet[
                Any
            ] = estate_soup.find_all(
                name="div",
                class_=self.PRESETS["estate_details_tag_class"],
            )

            # Details outside summary tab
            estate_price: Tag = estate_soup.find(
                name="strong",
                class_=self.PRESETS["estate_price_tag_class"],
            )
            estate_details_summary.insert(1, estate_price)

            estate_location: Tag = estate_soup.find(
                name="a",
                class_=self.PRESETS["estate_location_tag_class"],
            )
            estate_details_summary.insert(3, estate_location)

            estate_description: Tag = estate_soup.find(
                "div",
                class_=self.PRESETS["estate_description_tag_class"],
            )
            estate_details_summary.insert(4, estate_description)

        except IndexError as e:
            logging.error(f"Error in parsing the estate details:\n{e}")
            return None

        estate_details: list[str] = self.get_estate_details(
            details_el_tag=estate_details_summary
        )

        return EstateDetails(
            price=estate_details[1],
            size=estate_details[0],
            location=estate_details[3],
            description=estate_details[4],
        )

    def parse_page(self, soup: BeautifulSoup) -> List[Estate]:
        """
        Parse anouncement listing page, collect estate urls, visit each estate url and collect data from estate page.
        Return: list[Estate] validated models.
        """

        estate_results: ResultSet[Any] = soup.find_all(
            "li", {"class": self.PRESETS["li_listing_class"]}
        )

        estates: List[Estate] = []

        for li in estate_results:
            for el in li.find_all("a"):
                raw_url: str = el.get("href")
                estate_url: str = urljoin(
                    self.PARAMS["result_base_url"], raw_url
                )
                estate_details: EstateDetails = self.parse_estate(
                    estate_url
                )

                if not estate_details:
                    continue

                # To prevernt server overload
                sleep(self.PARAMS["sleep_time"])

                estate = Estate(
                    url=estate_url,
                    details=estate_details,
                )

                if self.PARAMS["verbose_logging"]:
                    logging.info(f"New entry parsed:\n{estate.url}")

                estates.append(estate)

        return estates

    def parse_site(self) -> List[Estate]:
        """
        Main scraper method to parse otodom page, extract data and save it into file.

        Returns:
            List[Estate]: list of estate validated model to be saved in a file.
        """
        logging.info("## Scraper started ##")

        first_page_soup: BeautifulSoup = self.get_listing_page_soup(
            page_no=1
        )
        page_results: list[Estate] = self.parse_page(
            soup=first_page_soup
        )
        results: list[Estate] = page_results

        page_num: int = 2
        while len(page_results) > 0:
            logging.info(
                msg=f"### Start parsing next page (no: {page_num}) ###"
            )
            page_soup: BeautifulSoup = self.get_listing_page_soup(
                page_no=page_num
            )
            page_results = self.parse_page(page_soup)
            page_num += 1
            if page_results:
                results.extend(page_results)
            if (
                self.PARAMS["page_limit"]
                and page_num >= self.PARAMS["page_limit"]
            ):
                break

        # For script execution time probing
        self.time_stop = time.time()

        logging.info(
            msg=f"## Scraper finished ##\n# Execution time "
            + str(self.time_stop - self.time_start)
            + " seconds #"
        )

        return results

    def save_data(self, temp_path, to_write) -> None:
        """
        Save results to specified file in temp_path specified path - if just filename without path provided,
        it will be saved in project root.
        """
        with open(temp_path, "w+", encoding="utf-8") as f:
            for line in to_write:
                f.write(str(line))
                f.write("\n")
