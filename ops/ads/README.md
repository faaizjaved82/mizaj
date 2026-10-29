# Ad results (aggregates only)

Once ads run, the owner exports one CSV a week from Meta Ads Manager (Reports → breakdown by campaign, ad set, ad and
country) and saves it here as `<YYYY-MM-DD>.csv`. Columns, in this order:

`date_start,date_end,campaign,ad_set,ad,country,spend_pkr,impressions,link_clicks,results,result_type`

Aggregates only: no names, emails or user lists. The Monday report (see `ops/COO_PLAYBOOK.md`) joins these with the
utm sources in `ops/stats/latest.json` to compute cost per finished test, share rate and revenue per finished test by
audience, creative and country, and applies the kill and scale rules in `docs/ADS.md` §4.
