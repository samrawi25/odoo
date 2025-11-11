from odoo import models, fields, api
from datetime import datetime, timedelta


class PriceComparisonReport(models.Model):
    _name = 'price.comparison.report'
    _description = 'Price Comparison Report'
    _auto = False

    date = fields.Date(string='Date')
    product_id = fields.Many2one('product.product', string='Product')
    competitor_id = fields.Many2one('competitor.competitor', string='Competitor')
    source = fields.Selection([
        ('your', 'AMG'),
        ('competitor', 'Competitor'),
    ], string='Source')
    price = fields.Float(string='Price')
    company_id = fields.Many2one('res.company', string='Company')

    @api.model
    def get_price_comparison_data(self, domain=None, product_ids=None, competitor_ids=None, start_date=None, end_date=None):
        domain = domain or []

        if product_ids:
            domain.append(('product_id', 'in', product_ids))
        if competitor_ids:
            domain += ['|', ('competitor_id', 'in', competitor_ids), ('competitor_id', '=', False)]
        if start_date:
            domain.append(('date', '>=', start_date))
        if end_date:
            domain.append(('date', '<=', end_date))

        price_data = self.search_read(domain, ['date', 'product_id', 'competitor_id', 'source', 'price'], order='date asc')

        def to_date(d):
            if isinstance(d, str):
                return datetime.strptime(d, '%Y-%m-%d').date()
            return d

        if price_data:
            min_date = min(to_date(rec['date']) for rec in price_data)
            max_date = max(to_date(rec['date']) for rec in price_data)
        else:
            today = datetime.today().date()
            min_date = max_date = today

        # Identify AMG and competitor data separately
        amg_data = [rec for rec in price_data if rec['source'] == 'your']
        comp_data = [rec for rec in price_data if rec['source'] == 'competitor']

        # Keep only products that exist in both AMG and competitor datasets
        amg_products = {rec['product_id'][0] for rec in amg_data if rec['product_id']}
        comp_products = {rec['product_id'][0] for rec in comp_data if rec['product_id']}
        common_product_ids = list(amg_products.intersection(comp_products))

        if not common_product_ids:
            return {'price_data': [], 'products': [], 'competitors': []}

        # Filter out non-common products
        price_data = [rec for rec in price_data if rec['product_id'][0] in common_product_ids]

        product_ids_all = list(set([rec['product_id'][0] for rec in price_data if rec['product_id']]))
        competitor_ids_all = list(set([rec['competitor_id'][0] for rec in price_data if rec['competitor_id']]))

        products_all = self.env['product.product'].browse(product_ids or product_ids_all)
        competitors_all = self.env['competitor.competitor'].browse(competitor_ids or competitor_ids_all)

        data_map = {}
        for rec in price_data:
            rec_date = to_date(rec['date'])
            competitor_name = rec['competitor_id'][1] if rec['competitor_id'] else 'AMG'
            data_map[(rec_date, rec['product_id'][0], competitor_name)] = rec['price']

        filled_data = []
        current_date = min_date
        while current_date <= max_date:
            for product in products_all:
                amg_price = data_map.get((current_date, product.id, 'AMG'), 0)
                filled_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'product_id': [product.id, product.name],
                    'competitor_id': False,
                    'competitor': 'AMG',
                    'source': 'your',
                    'price': amg_price,
                })
                for competitor in competitors_all:
                    comp_price = data_map.get((current_date, product.id, competitor.name), 0)
                    filled_data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'product_id': [product.id, product.name],
                        'competitor_id': [competitor.id, competitor.name],
                        'competitor': competitor.name,
                        'source': 'competitor',
                        'price': comp_price,
                    })
            current_date += timedelta(days=1)

        products = [{'id': p.id, 'name': p.name} for p in products_all]
        competitors = [{'id': c.id, 'name': c.name} for c in competitors_all]

        return {'price_data': filled_data, 'products': products, 'competitors': competitors}

    def init(self):
        self.env.cr.execute("DROP VIEW IF EXISTS price_comparison_report CASCADE")
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW price_comparison_report AS
            SELECT *
            FROM (
                -- AMG / your prices
                SELECT
                    ppl.id AS id,
                    ppl.changed_date::date AS date,
                    ppl.product_id,
                    NULL::int AS competitor_id,
                    'your' AS source,
                    ppl.new_price AS price,
                    COALESCE(u.company_id, 1) AS company_id
                FROM product_price_log ppl
                LEFT JOIN res_users u ON u.id = ppl.changed_by
                WHERE ppl.changed_date IS NOT NULL
                  AND ppl.product_id IS NOT NULL

                UNION ALL

                -- Competitor prices
                SELECT
                    mil.id + 1000000 AS id,
                    mil.mi_date::date AS date,
                    mil.product_id,
                    mil.competitor_id,
                    'competitor' AS source,
                    mil.unit_price AS price,
                    COALESCE(u.company_id, 1) AS company_id
                FROM market_intelligence_market_intelligence_line mil
                LEFT JOIN res_users u ON u.id = mil.create_uid
                WHERE mil.mi_date IS NOT NULL
                  AND mil.product_id IS NOT NULL
            ) AS all_data
            ORDER BY date ASC, id ASC
        """)

