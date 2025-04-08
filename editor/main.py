import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Inicialização da aplicação FastAPI
app = FastAPI(title='FastAPI com Jinja2')

app.mount('/static', StaticFiles(directory='./editor/static'), name='static')
templates = Jinja2Templates(directory='./editor/templates')


@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Rota principal que renderiza o template index.html
    """
    return templates.TemplateResponse(
        'index.html', {'request': request, 'titulo': 'Página Inicial'}
    )


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
