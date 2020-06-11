from starlette.applications import Starlette
from starlette.responses import JSONResponse

app = Starlette(debug=True)

@app.route('/add', methods=["POST"])
async def add(request):

    try:
        notebook = await request.json();
    except:
        notebook = None;

    if (notebook): print(notebook);

    return JSONResponse({});
