from thalentfrx import ThalentFrx

from . import a, b

app = ThalentFrx()

app.include_router(a.router, prefix="/a")
app.include_router(b.router, prefix="/b")
