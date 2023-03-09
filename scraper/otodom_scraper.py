import logging
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

    def _init_session(self) -> Session:
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
        """

        # TODO prepare function for user input - url data

        page_no: str = f"?{self.PARAMS['pagination']}={page_no}&"
        suffix_url: str = f"{self.PARAMS['suffix_url']}"
        base_url: str = f"{self.PARAMS['base_url']}" + page_no
        constructed_url: str = base_url + suffix_url

        # If next page of listing visited
        # self._reset_browser()
        assert (
            self.browser is not None
        ), "Failure in intializing the Browser!"
        with self.browser as browser:
            browser.get(constructed_url)
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
        # Need to reset in order to avoid session error from the browser.
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
        )

    def parse_page(self, soup: BeautifulSoup) -> List[Estate]:
        """
        Parse anouncement listing page, collect estate urls, visit each estate url and collect data from estate page.
        Return list of Estate validated models.
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
                    title=soup.find(
                        name="h1",
                        class_=self.PRESETS["estate_title_tag_class"],
                    ),
                    description="bla",
                    url=estate_url,
                    details=estate_details,
                )

                if self.PARAMS["verbose_logging"]:
                    logging.info(f"New entry parsed:\n{estate}")

                estates.append(estate)
                
        # Just for testing
        self.save_data(temp_path="example.txt", to_write=estates)

        return estates

    # Just for testing.
    def save_data(self, temp_path, to_write) -> None:
        with open(temp_path, "w+", encoding="utf-8") as f:
            for line in to_write:
                f.write(str(line))
                f.write('\n')
