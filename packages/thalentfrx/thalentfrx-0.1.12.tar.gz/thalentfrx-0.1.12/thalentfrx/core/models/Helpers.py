from datetime import datetime, timedelta
import pytz
import uuid
import time

class Helpers:
    def row2dict(self, row):
        d = {}
        for column in row.__table__.columns:
            value = getattr(row, column.name)
            if type(value) in [str,uuid.UUID]:
                d[column.name] = value.__str__()
            else:
                d[column.name] = value

        return d
    
    def get_timestamp(self) -> int:
        # ref_date = datetime(
        #     1900, 1, 1, tzinfo=pytz.utc
        # )
        # current_date = datetime.now(tz=pytz.utc)
        # interval: timedelta = current_date - ref_date
        #
        # return interval.microseconds

        # return Epoch time represents the number of seconds since January 1, 1970
        timestamp = int(time.time())
        return timestamp
