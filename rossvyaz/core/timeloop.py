from datetime import timedelta

from timeloop import Timeloop

tl = Timeloop()


@tl.job(interval=timedelta(days=1))
def update_job():
    from . import info
    info.update_info(True)
