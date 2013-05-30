# coding=utf-8

import logging
from datetime import datetime


class Graphs(object):
    def generate_html(self):
        odesk = self.read_log_file(u'logs/odesk.log')
        payoneer = self.read_log_file(u'logs/payoneer.log')
        bwc = self.read_log_file(u'logs/bwc.log')

        logging.debug(u'Composing data for graph library')

        # Bank accounts graph data
        bank_data = [u'Дата,oDesk,Payoneer,Итого\\n']
        for o, p in zip(odesk, payoneer):
            ovalue = float(o[1])
            pvalue = float(p[1])
            total = ovalue + pvalue
            bank_data.append(u'%s,%s,%s,%s\\n' % (o[0], int(ovalue), int(pvalue), int(total)))
        bank_data_str = '"+"'.join(bank_data)

        # Mobile balance graph data
        mobile_data = [u'Дата,БВК\\n']
        for d in bwc:
            mobile_data.append(u'%s,%s\\n' % (d[0], int(d[1])))
        mobile_data_str = u'"+"'.join(mobile_data)

        # Latest USD-RUB exchange rate
        usdrub = self.read_log_file(u'logs/usdrub.log')
        usdrub_date = usdrub[-1][0].strftime(u'%d.%m.%Y')
        usdrub_last = usdrub[-1][1]

        # Open graphs template file
        with open(u'html/graphs.template.html', u'r') as f:
            template = f.read().decode(u'utf8')

        # Render graphs template
        render = template.replace(u'%(bank-data)s', bank_data_str) \
                         .replace(u'%(mobile-data)s', mobile_data_str) \
                         .replace(u'%(usdrub)s', unicode(usdrub_last)) \
                         .replace(u'%(usdrub-date)s', unicode(usdrub_date))

        # Write graphs file
        fname = u'html/graphs.html'
        with open(fname, u'w') as f:
            f.write(render.encode(u'utf8'))

        logging.info(u'File %s has been generated' % fname)


    def read_log_file(self, filename):
        """
        Read given log file, parse its lines and return list of tuples
        (datetime, float)
        """
        logging.debug(u'Reading %s' % filename)

        res = []
        with open(filename, u'r') as f:
            for l in f.readlines():
                parts = l.decode(u'utf8').split(u',')
                dt = datetime.strptime(parts[0], u'%d.%m.%Y %H:%M')
                value = float(parts[1])

                res.append((dt, value))

        return res
