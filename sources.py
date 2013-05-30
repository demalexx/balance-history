# coding=utf-8

import re
import urllib2
import logging
from decimal import Decimal, InvalidOperation

from lxml import etree
from lxml.cssselect import CSSSelector
from mechanize import Browser

from config import CONFIG


class Currency(object):
    """Simple object with value and currency name, useful for pretty-print"""

    def __init__(self, value, currency):
        self.value = value
        self.currency = currency

    def __str__(self):
        tmp = '%.2f' % self.value
        if self.currency == u'USD':
            return '$%s' % tmp
        elif self.currency == u'RUB':
            return '%s руб.' % tmp

        return tmp

    def __unicode__(self):
        return unicode(str(self).decode(u'utf8'))


class BaseSource(object):
    def __init__(self):
        super(BaseSource, self).__init__()
        self.browser = Browser()


    @classmethod
    def get_source_name(cls):
        return cls.__name__.lower()


    def get_balance(self):
        raise NotImplementedError()


    def open_with_retry(self, url, page_type=u''):
        logging.debug(u'Opening URL: %s', url)

        try:
            res = self.browser.open(url, timeout=30)
        except urllib2.URLError:
            logging.debug(u'Opening failed, retry')
            res = self.browser.open(url, timeout=30)

        page = res.read()
        self.save_page(page, page_type)

        return page


    def string_to_decimal(self, text):
        """
        Try to convert given string to Decimal, removing some garbage characters
        before that, and trying to play with separator (12.34 or 12,34)
        """

        logging.debug(u'Converting "%s" to decimal', text)

        text = text.replace(u'$', u'').replace(u' ', u'')
        try:
            return Decimal(text)
        except InvalidOperation:
            text = text.replace(u',', u'.')

        return Decimal(text)


    def save_page(self, page, page_type=None):
        """Save given page for debug purposes"""

        if page_type:
            fname = u'debug/%s-%s.html' % (self.get_source_name(), page_type)
            msg = u'Saving %s %s page to %s' % (
                self.get_source_name(), page_type, fname)
        else:
            fname = u'debug/%s.html' % self.get_source_name()
            msg = u'Saving %s page to %s' % (self.get_source_name(), fname)

        logging.debug(msg)
        with open(fname, u'w') as f:
            f.write(page)


class Payoneer(BaseSource):
    LOGIN_URL = u'https://myaccount.payoneer.com/login/login.aspx'
    ACCOUNT_URL = u'https://myaccount.payoneer.com/MainPage/LoadList.aspx'

    def get_balance(self):
        self.open_with_retry(self.LOGIN_URL, u'login')

        logging.debug(u'Filling login form')
        self.browser.select_form(name=u'form1')
        self.browser.new_control(u'text', u'__EVENTTARGET', {})
        self.browser[u'__EVENTTARGET'] = u'btLogin'
        self.browser[u'txtUserName'] = CONFIG[u'payoneer'][u'username']
        self.browser[u'txtPassword'] = CONFIG[u'payoneer'][u'password']

        logging.debug(u'Submitting login form')
        self.browser.submit()

        page = self.open_with_retry(self.ACCOUNT_URL, u'account')

        logging.debug(u'Parsing page and extracting balance')
        html = etree.HTML(page)
        raw_balance = CSSSelector(u'strong#cardBalanceText span')(html)[0].text

        return Currency(self.string_to_decimal(raw_balance), u'USD')


class ODesk(BaseSource):
    LOGIN_URL = u'https://www.odesk.com/login'
    ACCOUNT_URL = u'https://www.odesk.com/withdrawal-methods'

    def get_balance(self):
        self.open_with_retry(self.LOGIN_URL, u'login')

        logging.debug(u'Filling login form')
        self.browser.select_form(nr=0)
        self.browser[u'username'] = CONFIG[u'odesk'][u'username']
        self.browser[u'password'] = CONFIG[u'odesk'][u'password']

        logging.debug(u'Submitting login form')
        self.browser.submit()

        page = self.open_with_retry(self.ACCOUNT_URL, u'account')

        logging.debug(u'Parsing page and extracting balance')
        html = etree.HTML(page)
        raw_balance = CSSSelector(u'div.oMain tr.oTxtMega.txtMiddle span.oPos')(html)[0].text

        return Currency(self.string_to_decimal(raw_balance), u'USD')


class BWC(BaseSource):
    LOGIN_URL = u'http://issa.bwc.ru/'
    ACCOUNT_URL = u'http://issa.bwc.ru/cgi-bin/cgi.exe?function=is_account'

    def get_balance(self):
        self.open_with_retry(self.LOGIN_URL, u'login')

        logging.debug(u'Filling login form')
        self.browser.select_form(name=u'num')
        self.browser[u'mobnum'] = CONFIG[u'bwc'][u'phone']
        self.browser[u'Password'] = CONFIG[u'bwc'][u'password']

        logging.debug(u'Submitting login form')
        self.browser.submit()

        page = self.open_with_retry(self.ACCOUNT_URL, u'account')

        logging.debug(u'Parsing page and extracting balance')
        html = etree.HTML(page)
        balance_str = html.xpath(u'//p[contains(text(), "Баланс вашего лицевого счета равен")]')[0].text

        raw_balance = re.search('[\d.,]+', balance_str).group()

        return Currency(self.string_to_decimal(raw_balance), u'RUB')


class USDRUB(BaseSource):
    EXCHANGE_URL = u'http://www.cbr.ru/scripts/XML_daily.asp'

    def get_balance(self):
        page = self.open_with_retry(self.EXCHANGE_URL)

        xml = etree.XML(page)
        raw_value = xml.xpath(u'//Valute[@ID="R01235"]/Value')[0].text

        return Currency(self.string_to_decimal(raw_value), u'RUB')


source_classes = {c.get_source_name(): c
                  for c in [Payoneer, ODesk, BWC, USDRUB]}
