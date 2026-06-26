import pandas as pd
from database.db import get_connection

def get_tickets(filters: dict = None) -> pd.DataFrame:
    conn = get_connection()
    q = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if filters:
        if filters.get('status'):
            q += " AND status=?"
            params.append(filters['status'])
        if filters.get('mes'):
            q += " AND substr(data_abertura,1,7)=?"
            params.append(filters['mes'])
        if filters.get('area'):
            q += " AND area=?"
            params.append(filters['area'])
        if filters.get('criado_por'):
            q += " AND criado_por=?"
            params.append(filters['criado_por'])
        if filters.get('paciente'):
            q += " AND paciente_nome LIKE ?"
            params.append(f"%{filters['paciente']}%")
        if filters.get('busca'):
            q += " AND (paciente_nome LIKE ? OR numero LIKE ? OR descricao LIKE ? OR motivo LIKE ?)"
            b = f"%{filters['busca']}%"
            params.extend([b,b,b,b])
    q += " ORDER BY data_abertura DESC"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def get_pacientes(busca='') -> pd.DataFrame:
    conn = get_connection()
    q = "SELECT * FROM pacientes"
    params = []
    if busca:
        q += " WHERE nome LIKE ?"
        params.append(f"%{busca}%")
    q += " ORDER BY nome"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def get_ligacoes(mes='') -> pd.DataFrame:
    conn = get_connection()
    q = "SELECT * FROM ligacoes WHERE 1=1"
    params = []
    if mes:
        q += " AND mes=?"
        params.append(mes)
    q += " ORDER BY data_hora DESC"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def get_indicadores_diarios(mes='') -> pd.DataFrame:
    conn = get_connection()
    q = "SELECT * FROM indicadores_diarios WHERE 1=1"
    params = []
    if mes:
        q += " AND mes=?"
        params.append(mes)
    q += " ORDER BY data"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def get_consolidado(mes='') -> pd.DataFrame:
    conn = get_connection()
    q = "SELECT * FROM consolidado_mensal WHERE 1=1"
    params = []
    if mes:
        q += " AND mes=?"
        params.append(mes)
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def get_monitoramentos(status='') -> pd.DataFrame:
    conn = get_connection()
    q = "SELECT * FROM monitoramentos WHERE 1=1"
    params = []
    if status:
        q += " AND status=?"
        params.append(status)
    q += " ORDER BY data_registro DESC"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def get_pendencias(status='') -> pd.DataFrame:
    conn = get_connection()
    q = "SELECT * FROM pendencias WHERE 1=1"
    params = []
    if status:
        q += " AND status=?"
        params.append(status)
    q += " ORDER BY CASE prioridade WHEN 'Crítica' THEN 1 WHEN 'Alta' THEN 2 WHEN 'Normal' THEN 3 ELSE 4 END, prazo"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def get_call_back(status='') -> pd.DataFrame:
    conn = get_connection()
    q = "SELECT * FROM call_back WHERE 1=1"
    params = []
    if status:
        q += " AND status=?"
        params.append(status)
    q += " ORDER BY dias_aberto DESC"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def save_ticket(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO tickets (numero, paciente_nome, area, origem, tipo, classificacao, descricao,
            motivo, status, prioridade, prazo, data_abertura, responsavel, observacoes, criado_por, operadora)
        VALUES (:numero,:paciente_nome,:area,:origem,:tipo,:classificacao,:descricao,
            :motivo,:status,:prioridade,:prazo,:data_abertura,:responsavel,:observacoes,:criado_por,:operadora)
    """, data)
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def save_paciente(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO pacientes (nome, operadora, telefone, data_cadastro, status, observacoes)
        VALUES (:nome,:operadora,:telefone,:data_cadastro,:status,:observacoes)
    """, data)
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def save_monitoramento(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO monitoramentos (paciente_nome, situacao, pendencia, conduta, status,
            proxima_acao, data_proxima_acao, observacoes, data_registro, responsavel)
        VALUES (:paciente_nome,:situacao,:pendencia,:conduta,:status,
            :proxima_acao,:data_proxima_acao,:observacoes,:data_registro,:responsavel)
    """, data)
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def save_pendencia(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO pendencias (paciente_nome, origem, tipo, prioridade, prazo, status,
            responsavel, observacoes, proxima_acao, data_registro)
        VALUES (:paciente_nome,:origem,:tipo,:prioridade,:prazo,:status,
            :responsavel,:observacoes,:proxima_acao,:data_registro)
    """, data)
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_stats_overview() -> dict:
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    stats['total_pacientes'] = c.execute("SELECT COUNT(*) FROM pacientes").fetchone()[0]
    stats['total_tickets'] = c.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    stats['tickets_abertos'] = c.execute("SELECT COUNT(*) FROM tickets WHERE status='Aberto'").fetchone()[0]
    stats['tickets_fechados'] = c.execute("SELECT COUNT(*) FROM tickets WHERE status='Fechado'").fetchone()[0]
    from datetime import date
    hoje = date.today().strftime('%Y-%m-%d')
    stats['tickets_hoje'] = c.execute("SELECT COUNT(*) FROM tickets WHERE data_abertura=?", (hoje,)).fetchone()[0]
    stats['total_ligacoes'] = c.execute("SELECT COUNT(*) FROM ligacoes").fetchone()[0]
    stats['ligacoes_abandonadas'] = c.execute("SELECT COUNT(*) FROM ligacoes WHERE abandonada=1").fetchone()[0]
    stats['monitoramentos_ativos'] = c.execute("SELECT COUNT(*) FROM monitoramentos WHERE status='Ativo'").fetchone()[0]
    stats['pendencias_abertas'] = c.execute("SELECT COUNT(*) FROM pendencias WHERE status='Aberta'").fetchone()[0]
    stats['call_back_abertos'] = c.execute("SELECT COUNT(*) FROM call_back WHERE status='Aberto'").fetchone()[0]
    conn.close()
    return stats

def get_tickets_por_categoria() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT categoria, COUNT(*) as total FROM tickets
        WHERE categoria IS NOT NULL AND categoria != '' AND categoria != 'nan'
        GROUP BY categoria ORDER BY total DESC LIMIT 15
    """, conn)
    conn.close()
    return df

def get_tickets_por_motivo() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT motivo, COUNT(*) as total FROM tickets
        WHERE motivo IS NOT NULL AND motivo != '' AND motivo != 'nan'
        GROUP BY motivo ORDER BY total DESC LIMIT 10
    """, conn)
    conn.close()
    return df

def get_top_pacientes() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT paciente_nome, COUNT(*) as total FROM tickets
        WHERE paciente_nome IS NOT NULL AND paciente_nome != '' AND paciente_nome != 'nan'
        GROUP BY paciente_nome ORDER BY total DESC LIMIT 15
    """, conn)
    conn.close()
    return df

def get_tickets_por_operadora() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT operadora, COUNT(*) as total FROM tickets
        WHERE operadora IS NOT NULL AND operadora != '' AND operadora != 'nan'
        GROUP BY operadora ORDER BY total DESC
    """, conn)
    conn.close()
    return df

def get_timeline_paciente(paciente_nome: str) -> dict:
    conn = get_connection()
    tickets = pd.read_sql_query(
        "SELECT * FROM tickets WHERE paciente_nome=? ORDER BY data_abertura DESC",
        conn, params=[paciente_nome])
    monitoramentos = pd.read_sql_query(
        "SELECT * FROM monitoramentos WHERE paciente_nome=? ORDER BY data_registro DESC",
        conn, params=[paciente_nome])
    conn.close()
    return {'tickets': tickets, 'monitoramentos': monitoramentos}

def search_global(termo: str) -> dict:
    conn = get_connection()
    b = f"%{termo}%"
    tickets = pd.read_sql_query(
        "SELECT 'Ticket' as tipo, numero as ref, paciente_nome, data_abertura as data, status FROM tickets "
        "WHERE numero LIKE ? OR paciente_nome LIKE ? OR descricao LIKE ? OR motivo LIKE ? LIMIT 20",
        conn, params=[b,b,b,b])
    pacientes = pd.read_sql_query(
        "SELECT 'Paciente' as tipo, CAST(id AS TEXT) as ref, nome as paciente_nome, data_cadastro as data, status FROM pacientes "
        "WHERE nome LIKE ? LIMIT 10", conn, params=[b])
    conn.close()
    return {'tickets': tickets, 'pacientes': pacientes}
