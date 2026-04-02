import requests
from flask import Flask, render_template, jsonify

import mimetypes

# Força o reconhecimento correto dos arquivos estáticos
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from psycopg2.extras import RealDictCursor

from database import get_connection

app = Flask(__name__)
INVERTETEXTO_TOKEN = '25230|JpxCIycLGBhhfKreouqDCZH97JzfLvU3'
BASE_URL = 'https://api.invertexto.com/v1/cep/'
    
@app.route('/ping')
def ping():
    return "Projeto Busca CEP"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/consulta/<cep_input>')
def consulta(cep_input):
    #13401-543
    cep_format = ''.join(filter(str.isdigit, cep_input))

    #Verifica a  quantdade de dígitos do CEP
    if len(cep_input) != 8:
        return jsonify({'Error ' : ' Cep inválido! Deve conter 8 dígitos'}),400
    


    #Verifica a conexão com o banco de dados
    conn = get_connection()
    if not conn:
        return jsonify({"error" :"Erro de conexão com o banco de dados!"}), 500

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        params = [cep_format]
        sql = "SELECT * FROM ceps WHERE cep = %s"
        cursor.execute(sql, params)
        cep_bd_local = cursor.fetchone()

        #Verifica se o cep existe no banco local
        if cep_bd_local:
            cursor.close()
            conn.close()
            dados = {
                "source" : "local_db",
                "data" :  cep_bd_local
            }
            return jsonify(dados)

        response = requests.get(f"{BASE_URL}{cep_format}?token={INVERTETEXTO_TOKEN}")
        # response = requests.get("https://api.invertexto.com/v1/cep/13401543?token=25230|JpxCIycLGBhhfKreouqDCZH97JzfLvU3")
        if response.status_code == 200:
            dados = response.json()
            sql = "INSERT INTO ceps (cep, estado, cidade, bairro, rua, complemento, ibge) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            params = [cep_format, dados.get('state'), dados.get('city'),
                      dados.get('neighborhood'), dados.get('street'), dados.get('complement'), dados.get('ibge')]
            cursor.execute(sql,params)
            conn.commit()
            cursor.close()
            conn.close()

            dados_resposta = {
                "source" : "api-externa",
                "data" : {
                    "cep" : cep_format,
                    "estado" : dados.get('state'),
                    "cidade" : dados.get('city'),
                    "bairro" : dados.get('neighborhood'),
                    "rua" : dados.get('street'),
                    "complemento" : dados.get('complement'),
                    "ibge" : dados.get('ibge')
                }
            }

            return jsonify(dados_resposta)        #se não existir no BD, consulgta a API externa
        elif response.status_code == 404:
            cursor.close()
            conn.close()
            return jsonify({"error": "CEP não encontrado na API"})

        else:
            cursor.close()
            conn.close()
            return jsonify({"error": "Erro ao consultar API externa"}), response.status_code




    except Exception as ex:
        print('erro---------', ex)
        if conn:
            conn.close()

        return jsonify({"error" : "Erro interno no servidor"}), 500



if __name__ == '__main__':
    app.run(debug = True)