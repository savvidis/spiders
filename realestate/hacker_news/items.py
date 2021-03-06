# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class PropertiesItem(Item):
    # Primary fields
    unique_id = Field()
    title = Field()
    price_num = Field()
    description = Field()
    region = Field(default='')
    city = Field(default='')
    neighborhood = Field(default='')
    address = Field(default='null')
    img_url = Field()
    on_site_date = Field()
    views_num = Field()
    construction_year = Field()
    category_major = Field()
    category_minor = Field()
    fulltext = Field()
    # Calculated fields
    asset_type = Field()  # real estate or car
    transaction_type = Field()  # commercial or auction
    price_sm_num = Field()
    updated_date = Field()  # update date as date
    last_update_num = Field()  # update date as duration
    latitude = Field()
    longitude = Field()
    # Commercial sites

    # Auction specic
    debtor_name = Field()
    auctioneer_name = Field()
    auction_date = Field()
    auction_number = Field()

    # Real estate specific
    property_area_num = Field()
    property_rooms_num = Field()
    property_buy_or_rent = Field()

    # Car specific
    car_kms_num = Field()
    car_cc_num = Field()
    car_fuel = Field()

    # Contact fields
    contact_legal_name = Field()
    contact_name = Field()
    contact_phone = Field()
    contact_mobile = Field()
    contact_email = Field()
    contact_website = Field()
    contact_ln = Field()
    contact_lt = Field()
    # Housekeeping fields
    url = Field()
    spider = Field()
    source = Field()
    imported_date = Field()

    # Ohter
    imgs = Field()
    features = Field()
    geo = Field()


class BnbtutorialItem(Item):
    rev_count = Field()
    amenities = Field()
    host_id = Field()
    hosting_id = Field()
    room_type = Field()
    price = Field()
    bed_type = Field()
    person_capacity = Field()
    cancel_policy = Field()
    rating_communication = Field()
    rating_cleanliness = Field()
    rating_checkin = Field()
    satisfaction_guest = Field()
    instant_book = Field()
    accuracy_rating = Field()
    response_time = Field()
    response_rate = Field()
    nightly_price = Field()
    url = Field()
