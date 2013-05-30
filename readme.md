balance-history
===============

Script is created to keep track of bank accounts balances, mobile phone balances etc (using internet banking and similar things). It's supposed to be run periodically. On each run it adds new line with current balances into appropriate file. And creates html page with graphs which shows changing balances in history.

Sample graphs page:

![](https://raw.github.com/demalexx/balance-history/master/docs/sample-graphs.png)

Requirements:

* [mechanize](https://pypi.python.org/pypi/mechanize/);
* [lxml](http://lxml.de/) ([Windows binaries](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml))
* [cssselect](https://pypi.python.org/pypi/cssselect);
* [Dygraphs](http://dygraphs.com/) (included).