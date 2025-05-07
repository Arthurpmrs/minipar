import sys

sys.path.append('./')

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from minipar.interpreter import Minipar


class RunSchema(BaseModel):
    source: str


class RunResponse(BaseModel):
    output: str


# Inicialização da aplicação FastAPI
app = FastAPI(title='FastAPI com Jinja2')

origins = ['http://localhost:8000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory='./editor/static'), name='static')
templates = Jinja2Templates(directory='./editor/templates')


@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Rota principal que renderiza o template index.html
    """

    return templates.TemplateResponse(
        'index.html', {'request': request, 'titulo': 'Interpretador Minipar'}
    )


@app.post('/run', response_model=RunResponse)
async def run_code(run: RunSchema):
    """
    Rota que manda o código para o interpretador
    """
    minipar = Minipar()
    return {'output': minipar.run(run.source)}


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
