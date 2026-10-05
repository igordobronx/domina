from app.auth.security import hash_password
from app.models.enum import PerfilEnum
from app.models.usuario import Escola, Usuario
from app.database import SessionLocal

def run_seed():
    db = SessionLocal()

    try:
        escola_existente = db.query(Escola).first()

        if not escola_existente:

            escola = Escola(
                nome="COLEGIO PREPARA ENEM",
                cnpj="12345678000190",
            )
            db.add(escola)
            db.flush()
        else:
            escola = escola_existente

        email_teste = "professor@domina.com"
        senha_plana = "senha123"
        senha_teste = hash_password(senha_plana)

        usuario_existente = (db.query(Usuario).filter(Usuario.email == email_teste).first())

        if not usuario_existente:

            usuario = Usuario(
                escola_id=escola.id,
                nome="professor beto",
                email=email_teste,
                senha_hash = senha_teste,
                perfil=PerfilEnum.PROFESSOR,
            )
            db.add(usuario)
            db.commit()

            print("\nseed executada com sucesso\n")
            print("\n++++++++++++++++++++++++++++++++++++++\n")
            print(f"Escola: {escola.nome}\n")
            print(f"email: {email_teste}")
            print(f"senha: {senha_plana}")
        else:
            usuario_existente.senha_hash = senha_teste
            db.commit()
            print(f"\nO usuario {email_teste} ja existia no banco de dados. Senha atualizada com o hash correto!\n")
    
    except Exception as e:
        db.rollback()
        print(f"\n Erro ao executar o seed: {e}\n")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
