from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float


import settings

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


def create_auctions_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


class Deals(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "auctions"

    id = Column(Integer, primary_key=True)

    unique_id = Column('unique_id', String)
    title = Column('title', String)
    price_num = Column('price_num', Integer, nullable=True)
    description = Column('description', String, nullable=True)
    region = Column('region', String, nullable=True)
    city = Column('city', String, nullable=True)
    neighborhood = Column('neighborhood', String, nullable=True)
    address = Column('address', String, nullable=True)
    img_url = Column('img_url', String, nullable=True)
    on_site_date = Column('on_site_date', DateTime, nullable=True)
    views_num = Column('views_num', Integer, nullable=True)
    construction_year_num = Column(
        'construction_year_num', Integer, nullable=True)
    category = Column('category', String, nullable=True)
    last_update_num = Column('last_update_num', Integer, nullable=True)
    updated_date = Column('updated_date', DateTime, nullable=True)

    # Calculated fields
    asset_type = Column('asset_type', String)  # real estate or car
    # commercial or auction
    transaction_type = Column('transaction_type', String)
    longitude = Column('longitude', Float)
    latitude = Column('latitude', Float)

    # Auction specic
    debtor_name = Column('debtor_name', String, nullable=True)
    auctioneer_name = Column('auctioneer_name', String, nullable=True)
    auction_date = Column('auction_date', String, nullable=True)
    auction_number = Column('auction_number', String, nullable=True)

    # Real estate specific
    property_area_num = Column('property_area_num', Integer, nullable=True)
    property_rooms_num = Column('property_rooms_num', Integer, nullable=True)
    property_buy_or_rent = Column(
        'property_buy_or_rent', String, nullable=True)

    # Car specific
    car_kms_num = Column('car_kms_num', Integer, nullable=True)
    car_cc_num = Column('car_cc_num', Integer, nullable=True)
    car_fuel = Column('car_fuel', String, nullable=True)

    # Contact fields
    contact_legal_name = Column('contact_legal_name', String, nullable=True)
    contact_name = Column('contact_name', String, nullable=True)
    contact_phone = Column('contact_phone', String, nullable=True)
    contact_mobile = Column('contact_mobile', String, nullable=True)
    contact_email = Column('contact_email', String, nullable=True)
    contact_website = Column('contact_website', String, nullable=True)

    # Housekeeping fields
    url = Column('url', String, nullable=True)
    source = Column('source', String)
    imported_date = Column('imported_date', DateTime, nullable=True)
