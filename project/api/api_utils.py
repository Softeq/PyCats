from datetime import datetime


def get_ui_time_from_api(timestamp):
    return ":".join(datetime.fromtimestamp(int(timestamp)).time().isoformat().split(":")[0:-1])
