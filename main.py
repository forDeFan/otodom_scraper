from scraper.otodom_scraper import OtoDomScraper

if __name__ == "__main__":

    scraper = OtoDomScraper()
    s = scraper.get_listing_page_soup(page_no=1)
    d = scraper.parse_page(soup=s)
