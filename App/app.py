import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask, url_for, request, redirect
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = db.execute('''
        SELECT * FROM
            (SELECT COUNT(*) n_contratos FROM contrato)
        JOIN
            (SELECT COUNT(*) n_vendedores FROM vendedor)
        JOIN
            (SELECT COUNT(*) n_clientes FROM cliente)
    ''').fetchone()

    return render_template('index.html',stats=stats,page = 'home')

@APP.route('/contratos/')
def listar_contratos():
    contratos = db.execute('''
        SELECT  cont.idContrato, 
                cont.dataPublicacao, 
                cont.dataCelebracao,  
                cont.objetoContrato 
        FROM Contrato cont 
        ORDER BY cont.idContrato
    ''').fetchall()
    
    id_contrato = request.args.get('idContrato')  # Captura o ID do formulário
    if id_contrato:
        contrato = db.execute('''
            SELECT idContrato, objetoContrato
            FROM contrato 
            WHERE idContrato = ?
        ''', [id_contrato]).fetchone()
        if contrato:
            return redirect(f"/contratos/{contrato['idContrato']}/")  # Redireciona para o vendedor encontrado
        else:
            return render_template('listar_contratos.html',page = 'contratos', contratos=contratos, erro="Cliente não encontrado")  # Mostra erro
    
    return render_template('listar_contratos.html',page = 'contratos', contratos=contratos)

@APP.route('/contratos/<int:codigo>/')
def contrato(codigo):
    # Obtém dados do contrato
    contrato = db.execute('''
        SELECT idContrato, objetoContrato
        FROM contrato 
        WHERE idContrato = ?
    ''', [codigo]).fetchone()
    # Obtém informações do contrato
    informacao = db.execute('''
        SELECT  c.precoContratual as precoContratual, 
                c.prazoExecucao as prazoExecucao,
                c.centralizado as centralizado,
                c.fundamentacao as fundamentacao,
                v.idVendedor as idVendedor, 
                v.designacao as vendedor,
                Cl.idCliente as idCliente,  
                Cl.designacao as cliente, 
                m.nome as municipio,
                m.idMun as idMun,
                d.nome as distrito,
                d.idDist as idDist,
                p.nome as pais,
                p.idPais as idPais,
                ac.descricao as acordo,
                tp.descricao as tp,
                cpv.descricao as cpv,       
                tc.descricao as tc
                
        FROM Contrato c 
        join ContratoVendedor cv on cv.idContrato = c.idContrato 
        join Vendedor v on cv.idVendedor = v.idVendedor
        join Cliente Cl on c.idCliente = cl.idCliente
        join Local l on l.idContrato = c.idContrato
        join Municipio m on m.idMun = l.idMun
        join Distrito d on m.idDist = d.idDist
        join Pais p on d.idPais = p.idPais
        join TipoProcedimento tp on c.idTipoProc = tp.idTipoProc
        join Tipo t on t.idContrato = c.idContrato
        join TipoContrato tc on t.idTipoCont = tc.idTipoCont
        join AcordoQuadro ac on ac.idAcordo = c.idAcordo
        join CP cp on cp.idContrato = c.idContrato
        join CPV cpv on cpv.idCPV = cp.idCPV
        where c.idContrato = ?
        ORDER BY c.idContrato
    ''', [codigo]).fetchall()
    return render_template('contrato.html',
                           page = 'contratos', 
                            contrato=contrato,
                            informacao=informacao)
    
@APP.route('/vendedores/', methods=['GET'])
def listar_vendedores():
    vendedores = db.execute('''
        SELECT  v.idVendedor as idVendedor, 
                v.designacao as designacao, 
                v.numFiscal as numFiscal,
                count(cv.idVendedor) as n_contratos
        from Vendedor v
        join ContratoVendedor cv on v.idVendedor = cv.idVendedor
        join Contrato c on c.idContrato = cv.idContrato
        group by v.idVendedor
        ORDER BY v.idVendedor
    ''').fetchall()
    
    id_vendedor = request.args.get('idVendedor')  # Captura o ID do formulário
    if id_vendedor:
        vendedor = db.execute('''
            SELECT idVendedor, designacao
            FROM vendedor
            WHERE idVendedor = ?
        ''', [id_vendedor]).fetchone()
        if vendedor:
            return redirect(f"/vendedores/{vendedor['idVendedor']}/")  # Redireciona para o vendedor encontrado
        else:
            return render_template('listar_vendedores.html', page = 'vendedores',vendedores=vendedores, erro="Vendedor não encontrado")  # Mostra erro
    
    nome_vendedor = request.args.get('nomeVendedor')  # Captura o nome enviado pelo formulário
    if nome_vendedor:
        vendedor = db.execute('''
        SELECT idVendedor, designacao
        FROM vendedor
        WHERE designacao = ?
    ''', [nome_vendedor]).fetchone()
    
        if vendedor:
            return redirect(f"/vendedores/{vendedor['idVendedor']}/")  # Redireciona para o vendedor encontrado
        else:
            return render_template('listar_vendedores.html',page = 'vendedores', vendedores=vendedores, erro="Vendedor não encontrado")  # Mostra erro

    return render_template('listar_vendedores.html',page = 'vendedores', vendedores=vendedores)

@APP.route('/vendedores/<int:codigo>/')
def vendedor(codigo):
    # Obtém dados do vendedor
    vendedor = db.execute('''
        SELECT idVendedor, designacao
        FROM vendedor 
        WHERE idVendedor = ?
    ''', [codigo]).fetchone()
    # Obtém contratos do Vendedor    
    contratos = db.execute('''
        SELECT  cont.idContrato, 
                cont.dataPublicacao, 
                cont.dataCelebracao,  
                cont.objetoContrato 
        FROM Contrato cont 
        join ContratoVendedor cv on cont.idContrato = cv.idContrato
        where cv.idVendedor = ? 
        ORDER BY cont.idContrato
    ''',[codigo]).fetchall()
    return render_template('vendedor.html',
                            page = 'vendedores', 
                            vendedor=vendedor,
                            contratos=contratos)                  

@APP.route('/clientes/')
def listar_clientes():
    clientes = db.execute('''
        SELECT  cl.idCliente as idCliente,
                cl.designacao as designacao,
                cl.nif as nif,
                count(c.idContrato) as n_contratos
        from Cliente cl
        join Contrato c on c.idCliente = cl.idCliente
        group by c.idCliente
        ORDER BY c.idCliente
    ''').fetchall()
    
    id_cliente = request.args.get('idCliente')  # Captura o ID do formulário
    if id_cliente:
        cliente = db.execute('''
            SELECT idCliente, designacao
            FROM cliente 
            WHERE idCliente = ?
        ''', [id_cliente]).fetchone()
        if cliente:
            return redirect(f"/clientes/{cliente['idCliente']}/")  # Redireciona para o vendedor encontrado
        else:
            return render_template('listar_clientes.html',page = 'clientes', clientes=clientes, erro="Cliente não encontrado")  # Mostra erro
    
    nome_cliente = request.args.get('nomeClientes')  # Captura o nome enviado pelo formulário
    if nome_cliente:
        cliente = db.execute('''
            SELECT idCliente, designacao
            FROM cliente 
            WHERE designacao = ?
        ''', [nome_cliente]).fetchone()
    
        if cliente:
            return redirect(f"/clientes/{cliente['idCliente']}/")  # Redireciona para o vendedor encontrado
        else:
            return render_template('listar_clientes.html',page = 'clientes', clientes=clientes, erro="Cliente não encontrado")  # Mostra erro

    return render_template('listar_clientes.html',page = 'clientes', clientes=clientes)

@APP.route('/clientes/<int:codigo>/')
def cliente(codigo):
    # Obtém dados do vendedor
    cliente = db.execute('''
        SELECT idCliente, designacao
        FROM cliente 
        WHERE idCliente = ?
    ''', [codigo]).fetchone()
    # Obtém contratos do Vendedor    
    contratos = db.execute('''
        SELECT  cont.idContrato, 
                cont.dataPublicacao, 
                cont.dataCelebracao,  
                cont.objetoContrato 
        FROM Contrato cont 
        join Cliente c on cont.idCliente = c.idCliente
        where c.idCliente = ? 
        ORDER BY cont.idContrato
    ''',[codigo]).fetchall()
    return render_template('cliente.html',
                            page = 'clientes', 
                            cliente=cliente,
                            contratos=contratos)      

@APP.route('/pais/')
def listar_pais():
    pais = db.execute('''
        SELECT  p.idPais as idPais, 
                p.nome as nome,
                n.n_distritos,
                m.idMun as idMun
        FROM Pais p
        join Distrito d on p.idPais = d.idPais
        join Municipio m on d.idDist = m.idDist 
        join(
                SELECT  p.idPais as idPais,
                        count(d.idDist) as n_distritos
                FROM Pais p
                join Distrito d on p.idPais = d.idPais
                group by p.idPais
            ) n on p.idPais = n.idPais
        group by p.idPais 
        ORDER BY idPais
    ''').fetchall()
    
    return render_template('listar_pais.html',page = 'pais', pais=pais)

@APP.route('/pais/<int:codigo>/')
def pais(codigo):
    # Obtém dados do pais
    pais = db.execute('''
        SELECT idPais, nome
        FROM Pais 
        WHERE idPais = ?
    ''', [codigo]).fetchone()
    # Obtém distritos do pais    
    distritos = db.execute('''
        select  d.idDist as idDist, 
                d.nome as nome,
                count(m.idMun) n_municipios
        from pais p
        join Distrito d on p.idPais = d.idPais
        join Municipio m on d.idDist = m.idDist
        where p.idPais = ?
        group by d.idDist 
        ORDER BY d.idDist
    ''',[codigo]).fetchall()
    
    nome_sanitizado = pais['nome'].replace(" ", "_")
    caminho_imagem = url_for('static', filename=f'/bandeiras/{nome_sanitizado}.jpg')
    
    return render_template('pais.html', 
                            pais=pais,
                            distritos=distritos,page = 'pais', caminho_imagem=caminho_imagem)      
    
@APP.route('/pais/distritos/<int:codigo>/')
def distrito(codigo):
    # Obtém dados do pais
    distrito = db.execute('''
        SELECT  d.idDist as idDist,
                d.nome as nome,
                p.idPais as idPais,
                p.nome as pais
        FROM Distrito d
        join Pais p on d.idPais = p.idPais 
        WHERE idDist = ?
    ''', [codigo]).fetchone()
    # Obtém distritos do pais    
    municipios = db.execute('''
        select  m.idMun as idMun,
                m.nome as nome,
                count(c.idContrato) n_contratos
        from Distrito d
        join Municipio m on d.idDist = m.idDist
        join Local l on l.idMun = m.idMun
        join Contrato c on c.idContrato = l.idContrato
        where d.idDist = ?
        group by m.idMun
        ORDER BY m.idMun
    ''',[codigo]).fetchall()
    return render_template('distrito.html',
                           page = 'pais', 
                            distrito=distrito,
                            municipios=municipios)      
    
@APP.route('/pais/distritos/municipios/<int:codigo>/')
def municipio(codigo):
    municipio = db.execute('''
        SELECT  m.idMun as idMun,
                m.nome as nome,
                d.idDist as idDist,
                d.nome as distrito,
                d.idPais as idPais,
                p.nome as Pais
        FROM Municipio m
        join Distrito d on m.idDist = d.idDist
        join Pais p on d.idPais = p.idPais
        WHERE idMun = ?
    ''', [codigo]).fetchone()
    contratos = db.execute('''
        SELECT  cont.idContrato, 
                cont.dataPublicacao, 
                cont.dataCelebracao,  
                cont.objetoContrato 
        FROM Contrato cont
        join Local l on cont.idContrato = l.idContrato
        join Municipio m on m.idMun = l.idMun
        where m.idMun = ?
        ORDER BY cont.idContrato
    ''',[codigo]).fetchall()
    
    nome_sanitizado = municipio['Pais'].replace(" ", "_")
    caminho_imagem = url_for('static', filename=f'/bandeiras/{nome_sanitizado}.jpg')
    
    return render_template('municipio.html',page = 'pais', municipio=municipio,contratos=contratos, caminho_imagem=caminho_imagem)


@APP.route('/perguntas/')
def listar_perguntas():
    return render_template('listar_perguntas.html',page = 'perguntas')

@APP.route('/perguntas/1')
def pergunta_1():
    resposta = db.execute('''
        SELECT idContrato as 'ID Contrato' , precoContratual as 'Preço Contratual' 
        FROM Contrato 
        WHERE precoContratual > 100000;
    ''').fetchall()
    
    return render_template('pergunta1.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/2')
def pergunta_2():
    resposta = db.execute('''
        SELECT Vendedor.designacao as Vendedor
        FROM Vendedor
        WHERE Vendedor.numFiscal ='RGPD';  
    ''').fetchall()
    
    return render_template('pergunta2.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/3')
def pergunta_3():
    resposta = db.execute('''
        SELECT COUNT(Contrato.idContrato) AS 'Número de Contratos Centralizados'
        FROM Contrato
        WHERE Contrato.centralizado='Sim'; 
    ''').fetchall()
    
    return render_template('pergunta3.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/4')
def pergunta_4():
    resposta = db.execute('''
        SELECT Distrito.nome AS Distrito , count(Municipio.idMun) as 'Número de Municípios'
        FROM Municipio 
        JOIN Distrito ON Municipio.idDist = Distrito.idDist
        where Distrito.nome <>'Distrito não determinado' and Distrito.nome <> 'Portugal Continental'
            and Distrito.nome not in (
            select nome from pais
        )
        Group by Distrito.idDist
        ORDER by Distrito.idDist; 
    ''').fetchall()
    
    return render_template('pergunta4.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/5')
def pergunta_5():
    resposta = db.execute('''
        SELECT Municipio.nome AS Municipio,COUNT(Contrato.idContrato) AS 'Quantidade de Contratos'
        FROM Contrato
        JOIN Local ON Contrato.idContrato = Local.idContrato
        JOIN Municipio ON Local.idMun = Municipio.idMun
        WHERE Municipio.nome not in (select nome from pais)
        GROUP BY Municipio.idMun
        ORDER BY COUNT(Contrato.idContrato) DESC;
    ''').fetchall()
    
    return render_template('pergunta5.html', resposta=resposta,page = 'perguntas')
@APP.route('/perguntas/6')
def pergunta_6():
    resposta = db.execute('''
        SELECT Distrito.nome AS Distrito, round(SUM(Contrato.precoContratual),2) AS 'Valor Total (€)'
        FROM Contrato
        JOIN Local ON Contrato.idContrato = Local.idContrato
        JOIN Municipio ON Local.idMun = Municipio.idMun
        JOIN Distrito ON Municipio.idDist = Distrito.idDist
        GROUP BY Distrito.idDist
        ORDER BY SUM(Contrato.precoContratual) DESC
        LIMIT 3;  
    ''').fetchall()
    
    return render_template('pergunta6.html', resposta=resposta,page = 'perguntas')
@APP.route('/perguntas/7')
def pergunta_7():
    resposta = db.execute('''
        SELECT Contrato.idContrato as 'ID Contrato', Distrito.nome AS Distrito, Municipio.nome AS Municipio 
        FROM Contrato 
        JOIN Local ON Contrato.idContrato = Local.idContrato 
        JOIN Municipio ON Local.idMun = Municipio.idMun 
        JOIN Distrito ON Municipio.idDist = Distrito.idDist
        WHERE Municipio.nome not in (select nome from pais)
        Order by Contrato.idContrato;
    ''').fetchall()
    
    return render_template('pergunta7.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/8')
def pergunta_8():
    resposta = db.execute('''
        SELECT Cliente.designacao as Cliente, round(SUM(Contrato.precoContratual),2) AS 'Valor Total' 
        FROM Contrato 
        JOIN Cliente 
        ON Contrato.idCliente = Cliente.idCliente 
        WHERE Cliente.idCliente = 1 
        GROUP BY Cliente.designacao;  
    ''').fetchall()
    
    return render_template('pergunta8.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/9')
def pergunta_9():
    resposta = db.execute('''
        SELECT Cliente.designacao as Cliente, SUM(Contrato.precoContratual) AS 'Valor Máximo' 
        FROM Contrato 
        JOIN Cliente 
        ON Contrato.idCliente = Cliente.idCliente 
        GROUP BY Cliente.designacao
        ORDER by SUM(Contrato.precoContratual) DESC
        Limit 1;  
    ''').fetchall()
    
    return render_template('pergunta9.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/10')
def pergunta_10():
    resposta = db.execute('''
        SELECT TipoProcedimento.descricao as 'Tipo de Procedimento', COUNT(Contrato.idContrato) AS 'Número de Contratos'
        FROM Contrato 
        JOIN TipoProcedimento 
        ON Contrato.idTipoProc = TipoProcedimento.idTipoProc 
        GROUP BY TipoProcedimento.descricao;  
    ''').fetchall()
    
    return render_template('pergunta10.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/11')
def pergunta_11():
    resposta = db.execute('''
        SELECT TipoProcedimento.descricao as 'Tipo de Procedimento', round(AVG(Contrato.precoContratual),2) AS 'Média do Valor do Contrato'
        FROM Contrato
        JOIN TipoProcedimento ON Contrato.idTipoProc = TipoProcedimento.idTipoProc
        GROUP BY TipoProcedimento.descricao
        ORDER BY AVG(Contrato.precoContratual) DESC;
    ''').fetchall()
    
    return render_template('pergunta11.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/12')
def pergunta_12():
    resposta = db.execute('''
        WITH RankContratos AS (
            SELECT 
                Cliente.designacao AS Cliente, 
                Pais.nome AS Pais, 
                COUNT(Contrato.idContrato) AS Num_Cont,
                (ROW_NUMBER() OVER (PARTITION BY Pais.idPais ORDER BY COUNT(Contrato.idContrato) DESC)) AS RowNum
            FROM Contrato
            JOIN Cliente ON Contrato.idCliente = Cliente.idCliente
            JOIN Local ON Contrato.idContrato = Local.idContrato
            JOIN Municipio ON Local.idMun = Municipio.idMun
            JOIN Distrito ON Municipio.idDist = Distrito.idDist
            JOIN Pais ON Distrito.idPais = Pais.idPais
            GROUP BY Cliente.idCliente, Pais.idPais
        )
        SELECT Cliente, Pais as País, num_cont as 'Número de Contratos'
        FROM RankContratos
        WHERE RowNum = 1 and Num_Cont>=2
        ORDER BY Pais;  
    ''').fetchall()
    
    return render_template('pergunta12.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/13')
def pergunta_13():
    resposta = db.execute('''
        SELECT Vendedor.designacao as Vendedor, COUNT(ContratoVendedor.idContrato) AS 'Número de Contratos'
        FROM Vendedor
        JOIN ContratoVendedor ON Vendedor.idVendedor = ContratoVendedor.idVendedor
        GROUP BY Vendedor.designacao
        HAVING COUNT(ContratoVendedor.idContrato) > 50
        ORDER BY COUNT(ContratoVendedor.idContrato) DESC;
    ''').fetchall()
    
    return render_template('pergunta13.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/14')
def pergunta_14():
    resposta = db.execute('''
        SELECT Vendedor.designacao AS Vendedor, Cliente.designacao AS Cliente, COUNT(Contrato.idContrato) AS 'Número de Contratos'
        FROM Vendedor
        JOIN ContratoVendedor ON Vendedor.idVendedor = ContratoVendedor.idVendedor
        JOIN Contrato ON ContratoVendedor.idContrato = Contrato.idContrato
        JOIN Cliente ON Contrato.idCliente = Cliente.idCliente
        GROUP BY Vendedor.idVendedor, Cliente.idCliente
        HAVING COUNT(Contrato.idContrato) >= 20
        ORDER BY COUNT(Contrato.idContrato) DESC;
    ''').fetchall()
    
    return render_template('pergunta14.html', resposta=resposta,page = 'perguntas')

@APP.route('/perguntas/15')
def pergunta_15():
    resposta = db.execute('''
    SELECT Distrito.nome as Distrito
    From Distrito 
    JOIN Pais on Pais.idPais=Distrito.idPais
    where   Pais.nome like 'Portugal' AND
            Distrito.nome <>'Distrito não determinado' AND
            Distrito.nome <> 'Portugal Continental' AND
            Distrito.nome not in (
                SELECT DISTINCT 
                Distrito.nome AS Distrito
                FROM Contrato
                JOIN CP ON Contrato.idContrato = CP.idContrato
                JOIN CPV ON CP.idCPV = CPV.idCPV
                JOIN Local ON Contrato.idContrato = Local.idContrato
                JOIN Municipio ON Local.idMun = Municipio.idMun
                JOIN Distrito ON Municipio.idDist = Distrito.idDist
                WHERE CPV.descricao LIKE '%Iogurte'
                ORDER by Distrito);
    ''').fetchall()
    
    return render_template('pergunta15.html', resposta=resposta,page = 'perguntas')


@APP.route('/perguntas/16')
def pergunta_16():
    resposta = db.execute('''
    SELECT 
    p.nome AS País,
    COUNT(DISTINCT CASE WHEN strftime('%m', c.dataPublicacao) = '01' THEN c.idContrato ELSE NULL END) AS janeiro,
    COUNT(DISTINCT CASE WHEN strftime('%m', c.dataPublicacao) = '02' THEN c.idContrato ELSE NULL END) AS fevereiro
    FROM Contrato c
    JOIN Local l ON c.idContrato = l.idContrato
    JOIN Municipio m ON l.idMun = m.idMun
    JOIN Distrito d ON m.idDist = d.idDist
    JOIN Pais p ON p.idPais = d.idPais
    WHERE p.nome IN ('Portugal', 'Espanha')
    GROUP BY p.nome;
    ''').fetchall()
    
    return render_template('pergunta16.html', resposta=resposta, page='perguntas')

