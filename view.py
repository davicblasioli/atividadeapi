from flask import Flask, jsonify, request
from main import app, con
from flask_bcrypt import generate_password_hash, check_password_hash
import re


@app.route('/livro', methods=['GET'])
def livro():
    cur = con.cursor()
    cur.execute('SELECT id_livros, titulo, autor, ano_publicacao FROM livros')
    livros = cur.fetchall()
    livros_dic = []
    for livros in livros:
        livros_dic.append({
            'id_livros': livros[0],
            'titulo': livros[1],
            'autor': livros[2],
            'ano_publicacao': livros[3]
        })
    return jsonify(mensagem='Lista de Livros', livros=livros_dic)


@app.route('/livros', methods=['POST'])
def livro_post():
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM LIVROS WHERE TITULO = ?', (titulo,))

    if cursor.fetchone():
        return jsonify('Livro já cadastrado')

    cursor.execute('INSERT INTO LIVROS(TITULO, AUTOR, ANO_PUBLICACAO) VALUES (?,?,?)', (titulo, autor, ano_publicacao))

    con.commit()
    cursor.close()

    return jsonify({
        'message': 'Livro cadastrado com sucesso!',
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })


@app.route('/livros/<int:id>', methods=['PUT'])
def livro_put(id):
    cursor = con.cursor()
    cursor.execute('SELECT ID_LIVROS, TITULO, AUTOR, ANO_PUBLICACAO FROM LIVROS WHERE ID_LIVROS = ?', (id,))
    livro_data = cursor.fetchone()

    if not livro_data:
        cursor.close()
        return jsonify({'Livro não foi encontrado'})

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor.execute('UPDATE LIVROS SET TITULO = ?, AUTOR = ?, ANO_PUBLICACAO = ? WHERE ID_LIVROS = ?',
                   (titulo, autor, ano_publicacao, id))

    con.commit()
    cursor.close()

    return jsonify({
        'message': 'Livro editado com sucesso!',
        'livro': {
            'id_livros': id,
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })


@app.route('/livros/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    cursor = con.cursor()

    # Verificar se o livro existe
    cursor.execute("SELECT 1 FROM livros WHERE ID_LIVROS = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Livro não encontrado"}), 404

    # Excluir o livro
    cursor.execute("DELETE FROM livros WHERE ID_LIVROS = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Livro excluido com sucesso!",
        'id_livros': id
    })

def validar_senha(senha):
    padrao = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
    return bool(re.fullmatch(padrao, senha))


@app.route('/usuario', methods=['GET'])
def usuario():
    cur = con.cursor()
    cur.execute('SELECT id_usuarios, nome, email, senha FROM usuarios')
    usuarios = cur.fetchall()
    usuarios_dic = []
    for usuario in usuarios:
        usuarios_dic.append({
            'id_usuarios': usuario[0],
            'nome': usuario[1],
            'email': usuario[2],
            'senha': usuario[3]
        })
    return jsonify(mensagem='Lista de Usuarios', usuarios=usuarios_dic)


@app.route('/usuarios', methods=['POST'])
def usuario_post():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not validar_senha(senha):
        return jsonify({"error": "A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais."}), 404

    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM USUARIOS WHERE NOME = ?', (nome,))

    if cursor.fetchone():
        return jsonify('Usuario já cadastrado')

    senha = generate_password_hash(senha).decode('utf-8')

    cursor.execute('INSERT INTO USUARIOS(NOME, EMAIL, SENHA) VALUES (?,?,?)', (nome, email, senha))

    con.commit()
    cursor.close()

    return jsonify({
        'message': 'Usuario cadastrado com sucesso!',
        'usuario': {
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })


@app.route('/usuarios/<int:id>', methods=['PUT'])
def usuario_put(id):
    cursor = con.cursor()
    cursor.execute('SELECT ID_USUARIOS, NOME, EMAIL, SENHA FROM USUARIOS WHERE ID_USUARIOS = ?', (id,))
    usuario_data = cursor.fetchone()

    if not usuario_data:
        cursor.close()
        return jsonify({'Usuario não foi encontrado'})

    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    # Validação da senha
    if not validar_senha(senha):
        return jsonify({"error": "A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais."}), 404

    cursor.execute('UPDATE USUARIOS SET NOME = ?, EMAIL = ?, SENHA = ? WHERE ID_USUARIOS = ?',
                   (nome, email, senha, id))

    con.commit()
    cursor.close()

    return jsonify({
        'message': 'Usuario editado com sucesso!',
        'usuario': {
            'id_usuarios': id,
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })


@app.route('/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    cursor = con.cursor()

    # Verificar se o livro existe
    cursor.execute("SELECT 1 FROM usuarios WHERE ID_USUARIOS = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Usuario não encontrado"}), 404

    # Excluir o livro
    cursor.execute("DELETE FROM usuarios WHERE ID_USUARIOS = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Usuario excluido com sucesso!",
        'id_usuarios': id
    })


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    cursor.execute('SELECT SENHA FROM USUARIOS WHERE EMAIL = ?', (email,))
    senha = cursor.fetchone()
    cursor.close()

    if not senha:
        return jsonify({"error": "Usuário não encontrado"}), 404

    senha_hash = senha[0]

    if check_password_hash(senha_hash, senha):  # Comparação direta
        return jsonify({"message: Login realizado com sucesso"}), 200

    return jsonify({"error": "email ou senha invalidos"}), 401


