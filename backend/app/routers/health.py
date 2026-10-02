from fastapi import APIRouter
''' esse aqruivo serve como um verificador de saude, um health check
ele tem tres funcoes principais:
1- monitoramento e diagnostico--> fornece um endpoint leve como get(/health) para verificar 
rapidamente se o sv backend está no ar
2- serviceos de hospedagem usam essa rota pra saber se o container/apklicação subiu
com sucesso ou se precisa ser reiniciado automaticamente
3- despolue o main.py
'''


router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health_check():
    return {"status": "ok"}