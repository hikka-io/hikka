from datetime import datetime, timedelta, date
from itertools import groupby
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return int(obj.timestamp())
        elif isinstance(obj, date):
            return int(datetime.combine(obj, datetime.min.time()).timestamp())
        return super().default(obj)


def find_consecutive_days(datetimes, min_length=3):
    sorted_dates = sorted(datetimes)

    dates = [dt.date() for dt in sorted_dates]

    consecutive_groups = []
    for k, g in groupby(
        enumerate(dates), lambda x: x[1] - timedelta(days=x[0])
    ):
        group = list(g)
        if len(group) >= min_length:
            start_date = group[0][1]
            end_date = group[-1][1]
            consecutive_groups.append(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "count": len(group),
                }
            )

    return consecutive_groups
